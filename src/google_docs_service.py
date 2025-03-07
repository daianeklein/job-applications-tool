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

    def fetch_cv(self):
        doc = self.service.documents().get(documentId=self.document_id).execute()
        text = []
        for element in doc.get("body", {}).get("content", []):
            if "paragraph" in element:
                for paragraph_element in element["paragraph"]["elements"]:
                    if "textRun" in paragraph_element:
                        text.append(paragraph_element["textRun"]["content"])
        return "".join(text)

    def fetch_field(self, index: int):
        doc = self.service.documents().get(documentId=self.document_id).execute()
        content = doc.get("body", {}).get("content", [])
        return content[index]["paragraph"]["elements"][0]["textRun"]["content"].strip()

    def replace_fields(self, old_text, new_text):
        requests = [
            {
                "replaceAllText": {
                    "containsText": {"text": old_text, "matchCase": True},
                    "replaceText": new_text,
                }
            }
        ]
        self.service.documents().batchUpdate(documentId=self.document_id, body={"requests": requests}).execute()
