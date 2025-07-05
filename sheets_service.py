import os
import json
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# Load variables from .env
load_dotenv()

def initialize_sheets_service():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    service_account_info = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)

    service = build('sheets', 'v4', credentials=creds, static_discovery=False)
    print("sheets service initialized")
    return service.spreadsheets()

initialize_sheets_service()