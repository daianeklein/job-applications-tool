import os
import sys
from pathlib import Path
import gspread
from dotenv import load_dotenv
from fpdf import FPDF

########### DEFINE PATHS ###########
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir / "agents"))  # Add agents folder to path
sys.path.insert(0, str(parent_dir / "prompts"))  # Add prompts folder to path
from job_description import job_description_text

########### GOOGLE SHEETS API ###########
SERVICE_ACCOUNT_FILE = "/Users/daianeklein/Documents/DS/job-applications-tool/h.json"
SPREADSHEET_ID = "1sBj_w8vevulAZmLfLz_mj6CMTl9VA942zfwJ-KF1Dxc"
SHEET_COMPANIES = "companies"

# Load Google Sheets credentials
gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
worksheet = gc.open_by_key(SPREADSHEET_ID).worksheet(SHEET_COMPANIES)

########### LOAD ENV VARIABLES ###########
load_dotenv()

def get_last_id():
    """
    Retrieves the last ID from Column A in 'companies'.
    
    Returns:
        str: The last ID as a string.
    """
    col_values = worksheet.col_values(1)  # Column A (ID)
    
    if len(col_values) > 1:  # Ensure at least one row exists
        return col_values[-1]  # Get the last row's ID
    return None  # No ID found


def save_job_description_as_pdf(job_description, pdf_filename):
# Extract the text variable
    docstring_text = job_description.strip()

    # Initialize PDF object
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add text to PDF
    pdf.multi_cell(0, 10, docstring_text)

    # Save PDF
    pdf.output(f"{pdf_filename}.pdf")

    print(f"PDF saved successfully as '{pdf_filename}.pdf'")

def main():
    # Get last ID from 'companies2'
    last_id = get_last_id()

    if last_id:
        pdf_filename = f"{last_id}.pdf"
        save_job_description_as_pdf(job_description_text, pdf_filename)
    else:
        print("No ID found in 'companies'.")

if __name__ == "__main__":
    main()
