from src.llm_service import LLMService
from src.text_processing import TextProcessing
from src.user_interface import UserInterface
from prompts.prompt_extract_keywords import p_extract_keywords
from prompts.prompt_update_job_title import update_job_title_p
from prompts.prompt_update_profile_summary import update_profile_summary_p
from prompts.prompt_update_professional_skills import update_professional_skills_p
from prompts.job_description import job_description_text

def main():
    llm_service = LLMService()
    text_processing = TextProcessing()
    ui = UserInterface()

    keywords = llm_service.extract_keywords(p_extract_keywords, job_description_text, "Reply in English.")

    job_title = text_processing.fetch_job_title()
    profile_summary = text_processing.fetch_profile_summary()
    professional_skills = text_processing.fetch_professional_skills()

    new_job_title = llm_service.update_cv_fields(keywords, update_job_title_p, job_title, "Reply in English.")
    new_profile_summary = llm_service.update_cv_fields(keywords, update_profile_summary_p, profile_summary, "Reply in English.")
    new_professional_skills = llm_service.update_cv_fields(keywords, update_professional_skills_p, professional_skills, "Reply in English.")

    ui.show_edit_dialog("Job Title", job_title, new_job_title)
    ui.show_edit_dialog("Profile Summary", profile_summary, new_profile_summary)
    ui.show_edit_dialog("Professional Skills", professional_skills, new_professional_skills)

if __name__ == "__main__":
    main()
