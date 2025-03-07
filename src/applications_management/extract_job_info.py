import sys
import os
from pathlib import Path
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure API key is available
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI API KEY NOT FOUND")

# Define paths
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent

# Import job description and prompt
sys.path.insert(0, str(parent_dir / "prompts"))
from job_description import job_description_text
from prompt_extract_role_information import extract_role_information_p

# Initialize OpenAI Chat Model
llm = ChatOpenAI(model_name='gpt-4o', openai_api_key=OPENAI_API_KEY)

def extract_job_info(prompt: str, job_description: str) -> dict:
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=job_description)
    ]

    response = llm.invoke(messages)
    extracted_data = response.content.strip()
    print(f'\n\n{extracted_data}\n\n')

    return extracted_data

if __name__ == "__main__":
    job_info = extract_job_info(extract_role_information_p, job_description_text)
    print(job_info)
