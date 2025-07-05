from flask import Flask, request, jsonify, Blueprint
import requests
import json
from datetime import datetime
import re
from googleapiclient.discovery import build
from google.oauth2 import service_account
import google.generativeai as genai
from sheets_service import initialize_sheets_service
import os
from dotenv import load_dotenv
# === Flask App and Blueprint ===
app = Flask(__name__)
bp = Blueprint('whatsapp', __name__)

# === Gemini API Configuration ===
load_dotenv()

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# WhatsApp API
WAHA_API_URL = os.getenv("WAHA_API_URL")
WAHA_API_KEY = os.getenv("WAHA_API_KEY")

# Google Sheets
SHEET_ID = os.getenv("SHEET_ID")
GID = os.getenv("GID")

SESSION_ID=os.getenv("SESSION_ID")


# === Gemini Parser ===
def parse_with_gemini(prompt_text):
    model = genai.GenerativeModel('gemini-1.5-flash')
    gemini_prompt = f"""
You are a smart quotation parser. Parse the message and return structured JSON.
Format:
{{
  "customer": "Customer Name",
  "items": [
    {{"item": "Fan", "qty": 2, "uom": "pcs", "rate": 1500, "gst": 18}},
    {{"item": "AC", "qty": 1, "uom": "nos", "rate": 35000, "gst": 28}}
  ]
}}

Message:
\"\"\"{prompt_text}\"\"\"
"""
    response = model.generate_content(gemini_prompt)
    # print(response)
    try:
        parsed = json.loads(response.text.strip('```json\n').strip())
        # print(parsed)
        return parsed.get('customer'), parsed.get('items')
    except Exception as e:
        print("Gemini parsing error:", e)
        return None, []
    
# === Send Message ===
def send_message(user_phone, message):
    payload = {
        "phone": user_phone,
        "text": message,
        "session": "pravin"
    }
    requests.get(f"{WAHA_API_URL}sendText", headers={
        "accept": "application/json",
        "X-Api-Key": WAHA_API_KEY
    }, params=payload)

# === Send File ===
def send_file(chat_id, caption=""):
    file_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=pdf&portrait=true&fitw=true&gridlines=false&gid={GID}"
    payload = {
        "chatId": chat_id,
        "file": {
            "mimetype": "application/pdf",
            "filename": "quotation.pdf",
            "url": file_url
        },
        "caption": caption,
        "session": SESSION_ID
    }
    headers = {
        "accept": "application/json",
        "X-Api-Key": WAHA_API_KEY,
        "Content-Type": "application/json"
    }
    requests.post(f"{WAHA_API_URL}sendFile", headers=headers, json=payload)

# === Add to Sheet ===
def add_quotation_to_sheet(sheet_id, quotation_data):
    print("called add_quotation_to_sheet")
    try:
        sheet = initialize_sheets_service()

        items = quotation_data['items']
        values = []

        for item in items:
            subtotal = item['qty'] * item['rate']
            gst_amt = round(subtotal * item['gst'] / 100, 2)
            total = round(subtotal + gst_amt, 2)

            values.append([
                quotation_data['quotation_id'],
                quotation_data['date'],
                quotation_data['customer'],
                item['item'],
                item['qty'],
                item.get('uom', ''),
                item['rate'],
                item['gst'],
                subtotal,
                gst_amt,
                total,
                quotation_data['phone'],
                quotation_data['status']
            ])

        print("Prepared values to insert:", values)

        response = sheet.values().append(
            spreadsheetId=sheet_id,
            range="Quotations!A1",
            valueInputOption="USER_ENTERED",
            body={"values": values}
        ).execute()

        print("Sheet append response:", response)
        return "ok"
    except Exception as e:
        print("Error in add_quotation_to_sheet:", e)
        return str(e)

# === Webhook ===
@bp.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print(data)
    if data.get('event') != 'message':
        return jsonify({"status": "ignored"}), 200

    message_data = data.get('payload', {})
    msg = message_data.get('body', '').strip()
    user = message_data.get('from', '').strip()

    if not msg or not user:
        return '', 200

    if msg.lower() == "/quotation":
        send_message(user, "🧾 Please send quotation details like this:\n\nCustomer: Mr. Sharma\nItems: 2 pcs Fans @1500 gst 18%, 1 nos AC @35000 gst 28%")
        return '', 200

    if msg.lower().startswith("customer:"):
        customer, items = parse_with_gemini(msg)
        if not items:
            send_message(user, "❌ Unable to parse. Try again with format:\nCustomer: Mr. Sharma\nItems: 2 pcs Fans @1500 gst 18%, 1 nos AC @35000 gst 28%")
            return '', 200

        now = datetime.now()
        qid = f"Q-{now.strftime('%Y%m%d-%H%M%S')}"
        today = now.strftime('%Y-%m-%d')
        # print(customer,items)
        quotation = {
            "quotation_id": qid,
            "date": today,
            "customer": customer,
            "items": items,
            "status": "Sent",
            "phone": user
        }
        print(quotation)
        add_quotation_to_sheet(SHEET_ID, quotation)
        send_file(user, qid)

    return '', 200
