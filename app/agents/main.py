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
SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('docs', 'v1', credentials=creds)
DOCUMENT_ID = '1pXc4nsuFd5RfQFWimmKaLMxucWiV7WLZDCtP18wbCTE'
doc = service.documents().get(documentId=DOCUMENT_ID).execute()

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

def fetch_job_title(resume:str) -> str:
    """Fetches the job title from the CV document in Google Docs."""
    doc = service.documents().get(documentId=DOCUMENT_ID).execute()
    
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

############################################################################


if __name__ == '__main__':
    print('Keywords are: ')
    keywords = extract_keywords(p_extract_keywords, job_description_text)
    print(f'{keywords}\n\n')

    print('The cv is: ')
    cv = fetch_cv(doc)
    print(f'{cv}\n\n')

    print('The Job Title is: ')
    job_title = fetch_job_title(doc)
    print(job_title)

    print('the new job title is: ')
    new_job_title = update_job_title(keywords, job_title)
    print(new_job_title)