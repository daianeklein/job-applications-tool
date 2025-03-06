import os
import sys
import openai
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pathlib import Path
from langdetect import detect
import tkinter as tk
from tkinter import ttk

########### PROMPTS
# Define paths
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
prompts_dir = parent_dir / "prompts"
sys.path.insert(0, str(prompts_dir))

from prompt_extract_keywords import p_extract_keywords
from job_description import job_description_text
from prompt_update_job_title import update_job_title_p
from prompt_update_profile_summary import update_profile_summary_p
from prompt_update_professional_skills import update_professional_skills_p

########### GOOGLE API 
from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = '/Users/daianeklein/Documents/DS/job-applications-tool/h.json'
SCOPES = ["https://www.googleapis.com/auth/documents"]
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('docs', 'v1', credentials=creds)

# Detect job description language
job_lang = detect(job_description_text)
if job_lang == 'pt':
    DOCUMENT_ID = '1dQbQJZ38b-570-7_Rwgcl6HOPS5vE6-hWhDXAU-NmlM'
else:
    DOCUMENT_ID = '1pXc4nsuFd5RfQFWimmKaLMxucWiV7WLZDCtP18wbCTE'

doc = service.documents().get(documentId=DOCUMENT_ID).execute()

# DOCUMENT_ID = '1pXc4nsuFd5RfQFWimmKaLMxucWiV7WLZDCtP18wbCTE'
# doc = service.documents().get(documentId=DOCUMENT_ID).execute()


########### OPEN AI
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise ValueError('OPENAI API KEY NOT FOUND')

# Initialize OpenAI Chat Model
llm = ChatOpenAI(model_name='gpt-4o', openai_api_key=OPENAI_API_KEY)

############################  ############################

def fetch_cv(document):
    text = []
    for element in document.get("body", {}).get("content", []):
        if "paragraph" in element:
            for paragraph_element in element["paragraph"]["elements"]:
                if "textRun" in paragraph_element:
                    text.append(paragraph_element["textRun"]["content"])
    return "".join(text)

def fetch_job_title(doc: str) -> str:
    content = doc.get("body", {}).get("content", [])

    job_title = content[2]['paragraph']['elements'][0]['textRun']['content']

    return job_title.strip()

def fetch_profile_summary(doc: str) -> str:
    content = doc.get("body", {}).get("content", [])

    profile_summary = content[6]['paragraph']['elements'][0]['textRun']['content']

    return profile_summary.strip()

def fetch_professional_skills(doc: str) -> str:
    content = doc.get("body", {}).get("content", [])

    professional_skills = content[9]['paragraph']['elements'][2]['textRun']['content']

    return professional_skills.strip()

############################ KEYWORDS ############################
def extract_keywords(prompt: str, job_description:str) -> str:
    """
    Calls OpenAI LLM using LangChain to extract keywords from a job description.

    Args:
        prompt (str): The job description text.

    Returns:
        str: Extracted keywords.
    """

    language_instruction = "Responda em português." if job_lang == 'pt' else "Reply in English."


    messages = [
        SystemMessage(content=f"{prompt}\n\n{language_instruction}"),
        HumanMessage(content=job_description)  
    ]

    response = llm.invoke(messages)
    return response.content.strip()

############################ UPDATE USING LLM ############################

def update_cv_fields(keywords:str, prompt: str, doc:str) -> str:

    language_instruction = "Responda em português." if job_lang == 'pt' else "Reply in English."

    messages = [
        SystemMessage(content=f"{prompt}\n\n{language_instruction}"),
        HumanMessage(content=keywords),
        HumanMessage(content=doc),
    ]

    response = llm.invoke(messages)
    response_content = getattr(response, "content", "").strip()

    return response_content if response_content else ""


def replace_fields(old_text, new_text):
    requests = [
        {
            "replaceAllText": {
                "containsText": {
                    "text": old_text,
                    "matchCase": True
                },
                "replaceText": new_text
            }
        }
    ]

    service.documents().batchUpdate(documentId=DOCUMENT_ID, body={"requests": requests}).execute()

def show_edit_dialog(field_name: str, current_value: str, new_value: str) -> str:
    """
    Shows a dialog window for the user to review and optionally edit the new value.
    
    Args:
        field_name (str): Name of the field being edited (e.g., "Job Title")
        current_value (str): The current value in the document
        new_value (str): The LLM-generated new value
        
    Returns:
        str: The final value to use (either the LLM-generated value or user-modified value)
    """
    # Create the dialog window
    dialog = tk.Tk()
    dialog.title(f"Review {field_name}")
    dialog.geometry("600x400")
    
    # Create and pack the widgets
    tk.Label(dialog, text=f"Current {field_name}:", font=("Arial", 10, "bold")).pack(pady=5)
    tk.Label(dialog, text=current_value).pack(pady=5)
    
    tk.Label(dialog, text=f"Suggested {field_name}:", font=("Arial", 10, "bold")).pack(pady=5)
    tk.Label(dialog, text=new_value).pack(pady=5)
    
    tk.Label(dialog, text="Edit if needed:", font=("Arial", 10, "bold")).pack(pady=5)
    edit_field = ttk.Entry(dialog, width=50)
    edit_field.insert(0, new_value)
    edit_field.pack(pady=10)
    
    # Variable to store the result
    result = {"value": new_value}
    
    def on_accept():
        result["value"] = edit_field.get()
        dialog.destroy()
    
    def on_cancel():
        result["value"] = current_value
        dialog.destroy()
    
    # Create buttons
    button_frame = ttk.Frame(dialog)
    button_frame.pack(pady=20)
    
    ttk.Button(button_frame, text="Accept", command=on_accept).pack(side=tk.LEFT, padx=10)
    ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT)
    
    # Run the dialog
    dialog.mainloop()
    
    return result["value"]

def update_with_confirmation(old_text: str, new_text: str, field_name: str) -> None:
    """
    Updates a field in the document after getting user confirmation/modification.
    
    Args:
        old_text (str): The current text in the document
        new_text (str): The LLM-generated new text
        field_name (str): Name of the field being updated
    """
    final_text = show_edit_dialog(field_name, old_text, new_text)
    if final_text != old_text:  # Only update if the text has changed
        replace_fields(old_text, final_text)

def main():
    keywords = extract_keywords(p_extract_keywords, job_description_text)

    cv = fetch_cv(doc)
    job_title = fetch_job_title(doc)
    profile_summary = fetch_profile_summary(doc)
    professional_skills = fetch_professional_skills(doc)

    new_job_title = update_cv_fields(keywords, update_job_title_p, cv)
    new_profile_summary = update_cv_fields(keywords, update_profile_summary_p, cv)
    new_professional_skills = update_cv_fields(keywords, update_professional_skills_p, cv)
    
    update_with_confirmation(job_title, new_job_title, "Job Title")
    update_with_confirmation(profile_summary, new_profile_summary, "Profile Summary")
    update_with_confirmation(professional_skills, new_professional_skills, "Professional Skills")

if __name__ == '__main__':
    main()

