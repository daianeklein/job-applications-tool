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

from extract_keywords import extract_keywords_prompt
from job_description import job_description_text

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise ValueError('Open AI Key not found')

llm = ChatOpenAI(model_name='gpt-4o', openai_api_key=OPENAI_API_KEY)

def call_openai(prompt:str) -> str:
    """
    Calls OpenAI LLM using LangChain.
    
    Args:
        prompt (str): The text prompt to send to the model.

    Returns:
        str: The response from the OpenAI model.
    """
    messages = [
        SystemMessage(content=extract_keywords_prompt),
        HumanMessage(content=prompt)  
    ]

    # response = llm(messages)
    response = llm.invoke(messages)
    return response.content.strip()

if __name__ == '__main__':
    response = call_openai(job_description_text)
    print("\nOpenAI Response:\n", response)
