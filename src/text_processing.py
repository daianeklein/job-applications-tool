from src.google_docs_service import GoogleDocsService

class TextProcessing:
    def __init__(self):
        self.doc_service = GoogleDocsService()

    def fetch_job_title(self):
        """Returns the job title extracted from Google Docs."""
        return self.doc_service.fetch_job_title()

    def fetch_profile_summary(self):
        """Returns the profile summary extracted from Google Docs."""
        return self.doc_service.fetch_profile_summary()

    def fetch_professional_skills(self):
        """Returns the professional skills extracted from Google Docs."""
        return self.doc_service.fetch_professional_skills()
