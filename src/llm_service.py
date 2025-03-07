from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY

class LLMService:
    def __init__(self, model_name="gpt-4o"):
        self.llm = ChatOpenAI(model_name=model_name, openai_api_key=OPENAI_API_KEY)

    def extract_keywords(self, prompt: str, job_description: str, language_instruction: str) -> str:
        messages = [
            SystemMessage(content=f"{prompt}\n\n{language_instruction}"),
            HumanMessage(content=job_description),
        ]
        response = self.llm.invoke(messages)
        return response.content.strip()

    def update_cv_fields(self, keywords: str, prompt: str, current_content: str, language_instruction: str) -> str:        
        formatted_input = f"""Keywords from Job Description:
{keywords}

Current Content:
{current_content}"""

        messages = [
            SystemMessage(content=f"{prompt}\n\n{language_instruction}"),
            HumanMessage(content=formatted_input)
        ]
        
        response = self.llm.invoke(messages)
        print(f'LLM Response: {response.content}')
        return response.content.strip() if response else ""
