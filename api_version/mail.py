import os
import base64
import mimetypes
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.message import EmailMessage

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def send_email_with_attachment(to_email, subject, body, file_path):
    # Load credentials from token.json
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # Build Gmail service
    service = build("gmail", "v1", credentials=creds)

    # Create an email message
    message = EmailMessage()
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    # Attach file
    if file_path:
        content_type, encoding = mimetypes.guess_type(file_path)
        main_type, sub_type = content_type.split("/", 1) if content_type else ("application", "octet-stream")

        with open(file_path, "rb") as file:
            message.add_attachment(file.read(), maintype=main_type, subtype=sub_type, filename=os.path.basename(file_path))

    # Encode message in base64
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # Send email
    send_message = {"raw": encoded_message}
    try:
        service.users().messages().send(userId="me", body=send_message).execute()
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

# Example usage
# send_email_with_attachment("adarshsir321@gmail.com", "Test Email", "Hello, this is a test email with a PDF attachment.", "report.pdf")
