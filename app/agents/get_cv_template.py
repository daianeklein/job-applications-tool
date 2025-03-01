from google.oauth2 import service_account
from googleapiclient.discovery import build

# Auth
SERVICE_ACCOUNT_FILE = '/Users/daianeklein/Documents/DS/job-applications-tool/h.json'
SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Docs API Service
service = build('docs', 'v1', credentials=creds)

DOCUMENT_ID = '1pXc4nsuFd5RfQFWimmKaLMxucWiV7WLZDCtP18wbCTE'

def fetch_cv_text():
    """Fetches the CV document content and extracts text."""
    doc = service.documents().get(documentId=DOCUMENT_ID).execute()

    def extract_text(document):
        text = []
        for element in document.get("body", {}).get("content", []):
            if "paragraph" in element:
                for paragraph_element in element["paragraph"]["elements"]:
                    if "textRun" in paragraph_element:
                        text.append(paragraph_element["textRun"]["content"])
        return "".join(text)

    return extract_text(doc)


if __name__ == '__main__':
    document_text = fetch_cv_text()
    print("\nDocument Content:\n", document_text)
