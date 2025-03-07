from llm_service import LLMService
from text_processing import TextProcessing
from user_interface import UserInterface
from prompts.prompt_extract_keywords import p_extract_keywords
from prompts.prompt_update_job_title import update_job_title_p
from prompts.prompt_update_profile_summary import update_profile_summary_p
from prompts.prompt_update_professional_skills import update_professional_skills_p
from prompts.job_description import job_description_text
from langdetect import detect

def get_language_instruction(text):
    """Determines the language instruction based on detected language."""
    lang = detect(text)
    return "Reply in English." if lang == "en" else "Responda em Português."

def main():
    llm_service = LLMService()
    text_processing = TextProcessing()
    ui = UserInterface()

    language_instruction = get_language_instruction(job_description_text)
    keywords = llm_service.extract_keywords(p_extract_keywords, job_description_text, language_instruction)

    job_title = text_processing.fetch_job_title()
    profile_summary = text_processing.fetch_profile_summary()
    professional_skills = text_processing.fetch_professional_skills()

    new_job_title = llm_service.update_cv_fields(keywords, update_job_title_p, job_title, language_instruction)
    new_profile_summary = llm_service.update_cv_fields(keywords, update_profile_summary_p, profile_summary, language_instruction)
    new_professional_skills = llm_service.update_cv_fields(keywords, update_professional_skills_p, professional_skills, language_instruction)

    # Show dialogs and save changes
    final_job_title = ui.show_edit_dialog("Job Title", job_title, new_job_title)
    if final_job_title != job_title:
        text_processing.doc_service.replace_fields(job_title, final_job_title)

    final_profile_summary = ui.show_edit_dialog("Profile Summary", profile_summary, new_profile_summary)
    if final_profile_summary != profile_summary:
        text_processing.doc_service.replace_fields(profile_summary, final_profile_summary)

    final_professional_skills = ui.show_edit_dialog("Professional Skills", professional_skills, new_professional_skills)
    if final_professional_skills != professional_skills:
        text_processing.doc_service.replace_fields(professional_skills, final_professional_skills)

if __name__ == "__main__":
    main()