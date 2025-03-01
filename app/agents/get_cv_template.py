from google.oauth2 import service_account
from googleapiclient.discovery import build

#auth
SERVICE_ACCOUNT_FILE = '/Users/daianeklein/Documents/DS/job-applications-tool/h.json'
SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

#Docs API Servoce
service = build('docs', 'v1', credentials=creds)

#cv template
DOCUMENT_ID = '1pXc4nsuFd5RfQFWimmKaLMxucWiV7WLZDCtP18wbCTE'
doc = service.documents().get(documentId=DOCUMENT_ID).execute()

print("Document Title:", doc["title"])


def extract_text(document):
    text = []
    for element in document.get("body", {}).get("content", []):
        if "paragraph" in element:
            for paragraph_element in element["paragraph"]["elements"]:
                if "textRun" in paragraph_element:
                    text.append(paragraph_element["textRun"]["content"])
    return "".join(text)

document_text = extract_text(doc)
print("\nDocument Content:\n", document_text)