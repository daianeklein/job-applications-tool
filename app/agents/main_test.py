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
from prompt_update_professional_skills import update_professional_skills_p

########### GOOGLE API 
from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = '/Users/daianeklein/Documents/DS/job-applications-tool/h.json'
SCOPES = ["https://www.googleapis.com/auth/documents"]
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
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=job_description)  
    ]

    response = llm.invoke(messages)
    return response.content.strip()

############################ UPDATE USING LLM ############################

def update_cv_fields(keywords:str, prompt: str, doc:str) -> str:
    
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=keywords),
        HumanMessage(content=doc),
    ]

    response = llm.invoke(messages)
    response_content = getattr(response, "content", "").strip()

    return response_content if response_content else ""


def replace_fields(old_text, new_text):
    print(f'old text is {old_text} and new text is {new_text}')
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

############################################################################

def main():
    keywords = extract_keywords(p_extract_keywords, job_description_text)

    cv = fetch_cv(doc)
    job_title = fetch_job_title(doc)
    profile_summary = fetch_profile_summary(doc)
    professional_skills = fetch_professional_skills(doc)

    new_job_title = update_cv_fields(keywords, update_job_title_p, cv)
    new_profile_summary = update_cv_fields(keywords, update_profile_summary_p, cv)
    new_professional_skills = update_cv_fields(keywords, update_professional_skills_p, cv)
    
    replace_fields(job_title, new_job_title)
    replace_fields(profile_summary, new_profile_summary)
    replace_fields(professional_skills, new_professional_skills)

if __name__ == '__main__':
    main()

