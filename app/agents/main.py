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
# def copy_document(original_doc_id: str, new_title: str) -> str:
#     """Creates a copy of the given Google Docs file with a new title and grants access to the user's personal account."""
#     copied_file = {'name': new_title}

#     copied_doc = drive_service.files().copy(fileId=original_doc_id, body=copied_file).execute()

#     if 'id' in copied_doc:
#         new_doc_id = copied_doc['id']
#         print(f"New document created successfully: https://docs.google.com/document/d/{new_doc_id}/edit")

#         # Grant personal Google account access
#         permission = {
#             "type": "user",
#             "role": "writer", 
#             "emailAddress": "daiane.klein22@gmail.com"
#         }
#         drive_service.permissions().create(
#             fileId=new_doc_id,
#             body=permission,
#             sendNotificationEmail=True,  # Sends an email notification to your personal account
#             fields="id"
#         ).execute()

#         return new_doc_id
#     else:
#         raise ValueError("Failed to create a copy of the document.")


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


def update_resume_new_title():
    # New Job Title
    NEW_TITLE = "Lead Data Scientist"

    # Find the start and end index of the existing job title
    EXISTING_TITLE = "Senior Data Analyst | Analytics Engineer"


    # Find the position of the job title
    start_index = None
    end_index = None

    for element in doc.get("body", {}).get("content", []):
        if "paragraph" in element:
            for paragraph_element in element["paragraph"]["elements"]:
                if "textRun" in paragraph_element:
                    text = paragraph_element["textRun"]["content"]
                    if EXISTING_TITLE in text:
                        start_index = paragraph_element["startIndex"]
                        end_index = paragraph_element["endIndex"]
                        break

    # If job title is found, update it
    if start_index and end_index:
        requests = [
            {
                "replaceAllText": {
                    "containsText": {
                        "text": EXISTING_TITLE,
                        "matchCase": True
                    },
                    "replaceText": NEW_TITLE
                }
            }
        ]

        # Send update request
        service.documents().batchUpdate(documentId=UPDATED_DOC_ID, body={"requests": requests}).execute()

        print(f"Job title updated to: {NEW_TITLE}")
    else:
        print("Existing job title not found in the document.")


############################################################################


if __name__ == '__main__':
    # print('Keywords are: ')
    # keywords = extract_keywords(p_extract_keywords, job_description_text)
    # print(f'{keywords}\n\n')

    # print('The cv is: ')
    # cv = fetch_cv(doc)
    # print(f'{cv}\n\n')

    # print('The Job Title is: ')
    # job_title = fetch_job_title(doc)
    # print(job_title)

    # print('the new job title is: ')
    # new_job_title = update_job_title(keywords, job_title)
    # print(new_job_title)

    update_resume_new_title()



