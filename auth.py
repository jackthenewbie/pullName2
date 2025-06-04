from google.oauth2 import service_account
from googleapiclient.discovery import build
def auth(SERVICE_ACCOUNT_FILE):

    if not SERVICE_ACCOUNT_FILE:
        SERVICE_ACCOUNT_FILE = 'credentials.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']  # read/write

    # 2. Credentials
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # 3. Build service
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    return sheet
