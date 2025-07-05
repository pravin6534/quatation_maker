


import requests
import json

WAHA_API_URL = 'https://wapi.vidhie.com/api/'
WAHA_API_KEY = '123456787'


def send_pdf_to_whatsapp(phone_number, quotation_id):
    # Format chat ID
    chat_id = f"{phone_number}@c.us"

    # Generate Google Sheet PDF export link
    pdf_url = f"https://github.com/examples/dev.likeapro.jpg"
    print(phone_number,quotation_id)
    payload = {
        "chatId": chat_id,
        "file": {
            "mimetype": "image/jpeg",
            "filename": f"{quotation_id}.pdf",
            "url": pdf_url
        },
        "caption": f"🧾 Your quotation {quotation_id} is ready.\nDownload attached PDF.",
        "session": "pravin"
    }

    headers = {
        "accept": "application/json",
        "X-Api-Key": WAHA_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(f"{WAHA_API_URL}sendFile", headers=headers, json=payload)
    print(response)
    if response.status_code == 200:
        print("✅ PDF sent successfully via WhatsApp")
    else:
        print(f"❌ Failed to send PDF: {response.status_code} - {response.text}")


send_pdf_to_whatsapp(918085844448, "test")