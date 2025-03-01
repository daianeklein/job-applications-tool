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

from extract_keywords_from_job_description import extract_keywords
from job_description import job_description_text
from adapt_keywords_into_resume import adapt_keywords_into_resume_prompt
import get_cv_template

# Load OpenAI API Key
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise ValueError('Open AI Key not found')

# Initialize OpenAI Chat Model
llm = ChatOpenAI(model_name='gpt-4o', openai_api_key=OPENAI_API_KEY)

def adapt_resume(keywords: str, cv_template: str) -> str:
    messages = [
        SystemMessage(content=adapt_keywords_into_resume_prompt),
        HumanMessage(keywords),
        HumanMessage(content=cv_template)  
    ]

    response = llm.invoke(messages)
    return response.content.strip()

if __name__ == '__main__':
    # keywords = extract_keywords(job_description_text) 
    # print("\nExtracted Keywords:\n", keywords)
    adapted_resume = adapt_resume(extract_keywords, get_cv_template)
    print(adapted_resume)







# if __name__ == '__main__':
#     keywords = extract_keywords(job_description_text)
#     print("\nExtracted Keywords:\n", keywords)
