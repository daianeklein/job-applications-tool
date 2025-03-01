import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pathlib import Path

# Define paths
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
prompts_dir = parent_dir / "prompts"
sys.path.insert(0, str(prompts_dir))

from prompt_extract_keywords import p_extract_keywords
from prompt_update_job_title import update_job_title_p
from job_description import job_description_text

from get_cv_template import fetch_cv_text
from extract_description_keywords import extract_keywords

#### OPEN AI API KEY
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise ValueError('OPENAI API KEY NOT FOUND')

llm = ChatOpenAI(model_name='gpt-4o', openai_api_key=OPENAI_API_KEY)

#### extract the job title
def fetch_job_title():
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

### update resume functions
def update_job_title(keywords:str, resume:str) -> str:
    messages = [
        SystemMessage(content=update_job_title_p),
        HumanMessage(content=keywords),
        HumanMessage(content=resume)
    ]

    response = llm.invoke(messages)
    return response.content.strip()





if __name__ == '__main__':
    keywords = extract_keywords(p_extract_keywords, job_description_text)
    print('\n\n-----------\n\n')
    print(keywords)
    print('\n\n-----------\n\n')

    print('\n\n-----------\n\n')
    resume = fetch_cv_text()
    print(resume)
    print('\n\n-----------\n\n')

    cv = update_resume_with_keywords(keywords, resume)
    print('\n\n-----------\n\n')
    print(cv)
    print('\n\n-----------\n\n')