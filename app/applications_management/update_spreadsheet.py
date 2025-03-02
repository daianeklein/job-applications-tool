import os
import sys
import openai
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build

########### DEFINE PATHS ###########
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir / "agents"))  # Add agents folder to path
sys.path.insert(0, str(parent_dir / "prompts"))  # Add prompts folder to path

# Import job description and prompt
from extract_job_info import extract_job_info
from job_description import job_description_text
from prompt_extract_role_information import extract_role_information_p

########### GOOGLE SHEETS API ###########
SERVICE_ACCOUNT_FILE = '/Users/daianeklein/Documents/DS/job-applications-tool/h.json'
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build("sheets", "v4", credentials=creds)

SPREADSHEET_ID = "1sBj_w8vevulAZmLfLz_mj6CMTl9VA942zfwJ-KF1Dxc"
SHEET_NAME = "companies2"
COLUMN_F_INDEX = 6  # Column F (Google Sheets is 1-based)

########### OPEN AI ###########
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise ValueError("OPENAI API KEY NOT FOUND")

# Initialize OpenAI Chat Model
llm = ChatOpenAI(model_name="gpt-4o", openai_api_key=OPENAI_API_KEY)

def get_next_available_row():
    """
    Finds the next available row in column F of the Google Sheets document.
    
    Returns:
        int: The next empty row number in column F.
    """
    sheet = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=f"{SHEET_NAME}!F:F").execute()
    col_values = sheet.get("values", [])
    return len(col_values) + 1  # Next row index

def update_spreadsheet():
    """
    Extracts company_name from job description and adds it to the next available row in column F.
    """
    # Extract job info
    job_info = extract_job_info(extract_role_information_p, job_description_text)

    # Extract company name
    company_name = None
    for line in job_info.split("\n"):
        if "Company Name:" in line:
            company_name = line.replace("Company Name:", "").strip()
            break

    if not company_name:
        print("No company name extracted.")
        return

    # Find next available row
    next_row = get_next_available_row()

    # Update Google Sheet
    update_body = {
        "values": [[company_name]]
    }
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!F{next_row}",
        valueInputOption="RAW",
        body=update_body,
    ).execute()

    print(f"Added '{company_name}' to row {next_row} in Column F.")

if __name__ == "__main__":
    update_spreadsheet()
