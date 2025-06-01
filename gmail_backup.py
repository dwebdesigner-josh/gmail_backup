import os
import re
import base64
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# SCOPES for reading Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
SENDER_EMAIL = 'example@example.com'  # Replace with actual sender email
ATTACHMENTS_DIR = 'attachments'
TEXT_DIR = 'email_texts'

os.makedirs(ATTACHMENTS_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)

def sanitize_filename(filename):
    # Replace invalid Windows filename characters with underscore
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

def get_email_messages(service, query):
    messages = []
    request = service.users().messages().list(userId='me', q=query)
    while request is not None:
        response = request.execute()
        messages.extend(response.get('messages', []))
        request = service.users().messages().list_next(request, response)
    return messages


def get_email_detail(service, msg_id):
    return service.users().messages().get(userId='me', id=msg_id).execute()

def extract_email_body(payload):
    body = ''
    if 'parts' in payload:
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain':
                data = part['body'].get('data')
                if data:
                    body += base64.urlsafe_b64decode(data).decode('utf-8')
    else:
        data = payload['body'].get('data')
        if data:
            body = base64.urlsafe_b64decode(data).decode('utf-8')
    return body

def save_email_text(text, filename):
    path = os.path.join(TEXT_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

def download_attachments(service, msg, msg_id):
    for part in msg['payload'].get('parts', []):
        filename = part.get('filename')
        body = part.get('body', {})
        if filename and 'attachmentId' in body:
            safe_filename = sanitize_filename(filename)  # sanitize filename
            path = os.path.join(ATTACHMENTS_DIR, safe_filename)

            if os.path.exists(path):
                print(f"Skipping {safe_filename}, already downloaded.")
                continue  # skip this attachment and continue loop

            att_id = body['attachmentId']
            att = service.users().messages().attachments().get(
                userId='me', messageId=msg_id, id=att_id).execute()
            data = base64.urlsafe_b64decode(att['data'])

            with open(path, 'wb') as f:
                f.write(data)
                print(f"Saved attachment: {safe_filename}")
def main():
    service = authenticate_gmail()
    query = f'from:{SENDER_EMAIL}'
    messages = get_email_messages(service, query)

    for msg_data in messages:
        msg_id = msg_data['id']
        msg = get_email_detail(service, msg_id)

        payload = msg.get('payload', {})
        headers = payload.get('headers', []) if payload else []

        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        date_raw = next((h['value'] for h in headers if h['name'] == 'Date'), None)

        try:
            date_parsed = datetime.strptime(date_raw[:-6], '%a, %d %b %Y %H:%M:%S')
            date_str = date_parsed.strftime('%Y-%m-%d_%H-%M-%S')
        except Exception:
            date_str = "unknown_date"

        filename = f"{date_str}_{msg_id}.txt"
        body = f"Subject: {subject}\n\n" + extract_email_body(payload)
        save_email_text(body, filename)
        download_attachments(service, msg, msg_id)
        print(f"Saved email text: {filename}")


if __name__ == '__main__':
    main()
