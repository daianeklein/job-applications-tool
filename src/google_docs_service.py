from googleapiclient.discovery import build
from config import CREDS
from langdetect import detect
from prompts.job_description import job_description_text

class GoogleDocsService:
    def __init__(self):
        self.service = build("docs", "v1", credentials=CREDS)
        self.document_id = self._set_document_id()

    def _set_document_id(self):
        job_lang = detect(job_description_text)
        return (
            "1dQbQJZ38b-570-7_Rwgcl6HOPS5vE6-hWhDXAU-NmlM"
            if job_lang == "pt"
            else "1pXc4nsuFd5RfQFWimmKaLMxucWiV7WLZDCtP18wbCTE"
        )

    def get_document(self):
        """Fetches the entire Google Doc content."""
        return self.service.documents().get(documentId=self.document_id).execute()

    def fetch_job_title(self):
        """Extracts job title from Google Docs."""
        doc = self.get_document()
        content = doc.get("body", {}).get("content", [])
        return content[2]["paragraph"]["elements"][0]["textRun"]["content"].strip() if content else ""

    def fetch_profile_summary(self):
        """Extracts profile summary from Google Docs."""
        doc = self.get_document()
        content = doc.get("body", {}).get("content", [])
        return content[6]["paragraph"]["elements"][0]["textRun"]["content"].strip() if content else ""

    def fetch_professional_skills(self):
        """Extracts professional skills from Google Docs."""
        doc = self.get_document()
        content = doc.get("body", {}).get("content", [])
        return content[9]["paragraph"]["elements"][2]["textRun"]["content"].strip() if content else ""

    def replace_fields(self, old_text, new_text):
        """Replaces a field's text in Google Docs."""
        requests = [
            {
                "replaceAllText": {
                    "containsText": {"text": old_text, "matchCase": True},
                    "replaceText": new_text,
                }
            }
        ]
        self.service.documents().batchUpdate(documentId=self.document_id, body={"requests": requests}).execute()
