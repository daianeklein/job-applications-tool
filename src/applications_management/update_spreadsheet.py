import os
import sys
import openai
import datetime
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
SHEET_COMPANIES = "companies"
SHEET_EVENTS = "events"

########### COLUMN INDEXES ###########
COLUMN_A_INDEX = 1  # Column A (ID)
COLUMN_B_INDEX = 2  # Column B (Current Date)
COLUMN_D_INDEX = 4  # Column D (Job Role)
COLUMN_F_INDEX = 6  # Column F (Company Name)

########### OPEN AI ###########
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise ValueError("OPENAI API KEY NOT FOUND")

# Initialize OpenAI Chat Model
llm = ChatOpenAI(model_name="gpt-4o", openai_api_key=OPENAI_API_KEY)

def get_next_available_row(sheet_name):
    """
    Finds the next available row in column A (ID), ensuring all values are written in the same row.

    Args:
        sheet_name (str): Name of the sheet to check.

    Returns:
        int: The next empty row number.
    """
    sheet = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=f"{sheet_name}!A:A").execute()
    col_values = sheet.get("values", [])
    return len(col_values) + 1  # Next row index

def get_next_id():
    """
    Retrieves the last ID in Column A of 'companies2' and increments it by 1.

    Returns:
        int: The next ID value.
    """
    sheet = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=f"{SHEET_COMPANIES}!A:A").execute()
    col_values = sheet.get("values", [])

    if len(col_values) > 1:  # Ensure there's at least one row of data
        last_id = col_values[-1][0]  # Get the last row's ID
        return int(last_id) + 1 if last_id.isdigit() else 1
    return 1  # If no IDs exist, start at 1

def add_job_info_to_sheet():
    """
    Extracts company name and job role from the job description and writes them to the same row in 'companies2'.
    Also, adds an auto-incremented ID in Column A and the current date in Column B.
    """
    # Extract job info
    job_info = extract_job_info(extract_role_information_p, job_description_text)

    # Extract company name and job role
    company_name = None
    role_name = None

    for line in job_info.split("\n"):
        if "Company Name:" in line:
            company_name = line.replace("Company Name:", "").strip()
        elif "Role Name:" in line:
            role_name = line.replace("Role Name:", "").strip()

    if not company_name or not role_name:
        print("Missing extracted values. Skipping update.")
        return

    # Find next available row and generate new ID
    next_row = get_next_available_row(SHEET_COMPANIES)
    next_id = get_next_id()
    current_date = datetime.datetime.now().strftime("%d/%m/%Y")  # Format: DD/MM/YYYY

    # Update Google Sheet 'companies2' in the same row
    update_body = {
        "values": [[next_id, current_date, "", role_name, "", company_name]]  # ID in A, Date in B, Role in D, Company in F
    }
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_COMPANIES}!A{next_row}:F{next_row}",  # Update columns A, B, D, and F in the same row
        valueInputOption="RAW",
        body=update_body,
    ).execute()

    print(f"Added to 'companies2' Row {next_row}: ID={next_id}, Date={current_date}, Role='{role_name}', Company='{company_name}'.")

    # Now add event to 'events' tab
    add_event_to_sheet(next_id, current_date)

def add_event_to_sheet(event_id, event_date):
    """
    Adds the event to the 'events' sheet with:
    - Column A: ID from 'companies2'
    - Column B: Date from 'companies2'
    - Column C: 'application'
    """
    # Find next available row in 'events'
    next_event_row = get_next_available_row(SHEET_EVENTS)

    # Update Google Sheet 'events'
    update_body = {
        "values": [[event_id, event_date, "application"]]
    }
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_EVENTS}!A{next_event_row}:C{next_event_row}",  # Update columns A, B, and C
        valueInputOption="RAW",
        body=update_body,
    ).execute()

    print(f"Added to 'events' Row {next_event_row}: ID={event_id}, Date={event_date}, Type='application'.")

if __name__ == "__main__":
    add_job_info_to_sheet()
