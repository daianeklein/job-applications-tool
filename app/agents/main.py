import os
import sys
import openai
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pathlib import Path

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

########### GOOGLE API 
from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = '/Users/daianeklein/Documents/DS/job-applications-tool/h.json'
SCOPES = ["https://www.googleapis.com/auth/documents"]
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('docs', 'v1', credentials=creds)
DOCUMENT_ID = '1pXc4nsuFd5RfQFWimmKaLMxucWiV7WLZDCtP18wbCTE'
UPDATED_DOC_ID = '1eNYKZsh5-GjGfUDPRrvR9pMCuJeZbdSQ0XCDQu2yp4Q'
doc = service.documents().get(documentId=DOCUMENT_ID).execute()
updated_doc = service.documents().get(documentId=UPDATED_DOC_ID).execute()


########### OPEN AI
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise ValueError('OPENAI API KEY NOT FOUND')

# Initialize OpenAI Chat Model
llm = ChatOpenAI(model_name='gpt-4o', openai_api_key=OPENAI_API_KEY)

############################ GET CV TEMPLATE ############################

def fetch_cv(document):
    text = []
    for element in document.get("body", {}).get("content", []):
        if "paragraph" in element:
            for paragraph_element in element["paragraph"]["elements"]:
                if "textRun" in paragraph_element:
                    text.append(paragraph_element["textRun"]["content"])
    return "".join(text)

############################################################################

############################ EXTRACT KEYWORDS ############################
def extract_keywords(prompt: str, job_description:str) -> str:
    """
    Calls OpenAI LLM using LangChain to extract keywords from a job description.

    Args:
        prompt (str): The job description text.

    Returns:
        str: Extracted keywords.
    """
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=job_description)  
    ]

    response = llm.invoke(messages)
    return response.content.strip()

############################################################################

############################ JOB TITLE ############################

def fetch_job_title(doc:str) -> str:
    """Fetches the job title from the CV document in Google Docs."""    
    content = doc.get("body", {}).get("content", [])
    
    job_title = None
    paragraph_count = 0  # Track which paragraph we're processing

    for element in content:
        if "paragraph" in element:
            paragraph_count += 1  # Increment for each paragraph
            
            # The second paragraph should be the job title
            if paragraph_count == 2:
                for paragraph_element in element["paragraph"]["elements"]:
                    if "textRun" in paragraph_element:
                        job_title = paragraph_element["textRun"]["content"].strip()
                break  # Stop after finding the second paragraph

    return job_title

def update_job_title(keywords:str, job_title:str) -> str:
    messages = [
        SystemMessage(content=update_job_title_p),
        HumanMessage(content=keywords),
        HumanMessage(content=job_title)
    ]

    response = llm.invoke(messages)
    return response.content.strip()


def update_resume_new_title(new_title: str, existing_title: str):
    # Find the position of the job title
    start_index = None
    end_index = None

    for element in doc.get("body", {}).get("content", []):
        if "paragraph" in element:
            for paragraph_element in element["paragraph"]["elements"]:
                if "textRun" in paragraph_element:
                    text = paragraph_element["textRun"]["content"]
                    if existing_title in text:
                        start_index = paragraph_element["startIndex"]
                        end_index = paragraph_element["endIndex"]
                        break

    # If job title is found, update it
    if start_index and end_index:
        requests = [
            {
                "replaceAllText": {
                    "containsText": {
                        "text": existing_title,
                        "matchCase": True
                    },
                    "replaceText": new_title
                }
            }
        ]

        # Send update request
        service.documents().batchUpdate(documentId=UPDATED_DOC_ID, body={"requests": requests}).execute()

        print(f"Job title updated to: {new_title}")
    else:
        print("Existing job title not found in the document.")

############################################################################

############################ PROFILE SUMMARY ############################

def fetch_profile_summary(doc:str) -> str:
    """Fetches the profile summary from the CV document in Google Docs."""    
    content = doc.get("body", {}).get("content", [])
    
    profile_summary = None
    paragraph_count = 0  # Track which paragraph we're processing

    for element in content:
        if "paragraph" in element:
            paragraph_count += 1  # Increment for each paragraph
            
            if paragraph_count == 6:
                for paragraph_element in element["paragraph"]["elements"]:
                    if "textRun" in paragraph_element:
                        if paragraph_element["textRun"]["content"]:
                            profile_summary = paragraph_element["textRun"]["content"]
                            break

    return profile_summary

def get_profile_summary_llm(keywords:str, profile_summary:str) -> str:
    messages = [
        SystemMessage(content=update_profile_summary_p),
        HumanMessage(content=keywords),
        HumanMessage(content=profile_summary)
    ]

    response = llm.invoke(messages)
    return response.content.strip()



############################################################################


def update_resume_text(existing_text: str, new_text: str, document_id: str, service):
    """
    Updates any text in the Google Docs document.

    Args:
        existing_text (str): The text to be replaced.
        new_text (str): The new text to replace the existing one.
        document_id (str): The ID of the Google Docs document.
        service: The Google Docs API service instance.
    """
    # Retrieve the document
    doc = service.documents().get(documentId=document_id).execute()

    # Check if the existing text is in the document
    found = False
    for element in doc.get("body", {}).get("content", []):
        if "paragraph" in element:
            for paragraph_element in element["paragraph"]["elements"]:
                if "textRun" in paragraph_element:
                    text = paragraph_element["textRun"]["content"]
                    if existing_text in text:
                        found = True
                        break
    
    # If found, create the request
    if found:
        requests = [
            {
                "replaceAllText": {
                    "containsText": {
                        "text": existing_text,
                        "matchCase": True
                    },
                    "replaceText": new_text
                }
            }
        ]

        # Send update request
        service.documents().batchUpdate(
            documentId=document_id, body={"requests": requests}
        ).execute()

        print("Text Updated")
    else:
        print(f"Text '{existing_text}' not found in the document.")



############################################################################

if __name__ == '__main__':
    # Extract keywords from job description
    keywords = extract_keywords(p_extract_keywords, job_description_text)
    
    # Fetch necessary sections from the document
    cv = fetch_cv(doc)
    job_title = fetch_job_title(doc)
    profile_summary = fetch_profile_summary(doc)

    # Generate new content
    new_job_title = update_job_title(keywords, job_title)
    new_profile_summary = get_profile_summary_llm(keywords, profile_summary)

    # Define text replacements as a list of tuples
    text_updates = [
        (job_title, new_job_title),
        (profile_summary, new_profile_summary)
    ]

    # Loop over updates to apply them dynamically
    for existing_text, new_text in text_updates:
        update_resume_text(
            existing_text=existing_text,
            new_text=new_text,
            document_id=UPDATED_DOC_ID,
            service=service
        )



