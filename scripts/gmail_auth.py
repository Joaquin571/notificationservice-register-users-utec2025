from __future__ import print_function
import os, pathlib
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

BASE = pathlib.Path(__file__).resolve().parents[1]
cred_file = os.getenv("GMAIL_CREDENTIALS_FILE", str(BASE / "secrets" / "credentials.json"))
token_file = os.getenv("GMAIL_TOKEN_FILE", str(BASE / "secrets" / "token.json"))

def main():
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(cred_file, SCOPES)
            creds = flow.run_local_server(port=0)
        os.makedirs(os.path.dirname(token_file), exist_ok=True)
        with open(token_file, "w") as token:
            token.write(creds.to_json())
    print("Token guardado en:", token_file)

if __name__ == "__main__":
    main()
