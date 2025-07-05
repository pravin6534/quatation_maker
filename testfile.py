


import requests
import json

API_KEY = "123456787"
SESSION_ID = "pravin"
API_URL = "https://wapi.vidhie.com/api/sendFile"


def send_file(chat_id, file_url, filename, mimetype, caption=""):
    """
    Simple function to send file using globally defined API settings
    
    Args:
        chat_id: Target chat ID (e.g., "9188888888@c.us")
        file_url: URL of the file to send
        filename: Name for the file
        mimetype: File type (e.g., "image/jpeg")
        caption: Optional caption (default: "")
    
    Returns:
        API response or error dictionary
    """
    headers = {
        "accept": "application/json",
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "chatId": chat_id,
        "file": {
            "mimetype": mimetype,
            "filename": filename,
            "url": file_url
        },
        "caption": caption,
        "session": SESSION_ID
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
    
result = send_file(
    chat_id="918085844448@c.us",
    file_url="https://raw.githubusercontent.com/devlikeapro/waha/refs/heads/core/examples/example.pdf",
    filename="myfile.pdf",
    mimetype="application/pdf",
    caption="Here's your file"
)

print(result)
