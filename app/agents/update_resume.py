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
from prompt_update_resume import update_resume_p
from job_description import job_description_text

from get_cv_template import fetch_cv_text
from extract_description_keywords import extract_keywords


#### OPEN AI API KEY
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise ValueError('OPENAI API KEY NOT FOUND')

llm = ChatOpenAI(model_name='gpt-4o', openai_api_key=OPENAI_API_KEY)

### update resume function
def update_resume_with_keywords(keywords:str, resume:str) -> str:
    messages = [
        SystemMessage(content=update_resume_p),
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