import os
import sys
import openai
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
from job_description import job_description_text

# Load OpenAI API Key
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise ValueError('OPENAI API KEY NOT FOUND')

# Initialize OpenAI Chat Model
llm = ChatOpenAI(model_name='gpt-4o', openai_api_key=OPENAI_API_KEY)

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

if __name__ == '__main__':
    keywords = extract_keywords(p_extract_keywords, job_description_text)
    print("\nExtracted Keywords:\n", keywords)
