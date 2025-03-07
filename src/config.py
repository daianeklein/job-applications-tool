import os
from dotenv import load_dotenv
from google.oauth2 import service_account

#load env variables
load_dotenv()

#open AI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("Open AI API key not found")

#Google docs Credentials
SERVICE_ACCOUNT_FILE = '/Users/daianeklein/Documents/DS/job-applications-tool/h.json'
SCOPES = ['https://www.googleapis.com/auth/documents']
CREDS = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)