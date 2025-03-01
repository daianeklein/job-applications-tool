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
from job_description import job_description_text

from get_cv_template import fetch_cv_text
from extract_description_keywords import extract_keywords

fetch_cv_text()

if __name__ == '__main__':
    cv = extract_keywords(job_description_text)
    print(cv)