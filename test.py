import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

CREDENTIALS = "./secrets/credentials.json"
TOKEN = "./secrets/token.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

TO = "gcjoaco@gmail.com"  
FROM = "joaquin.gonzalez.c@estudiantes.utec.edu.uy" 
SUBJECT = "Prueba directa API Gmail"
BODY = "Esto es una prueba directa usando el token y la API."

def main():
    creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    service = build("gmail", "v1", credentials=creds)

    msg = MIMEText(BODY)
    msg["to"] = TO
    msg["from"] = FROM
    msg["subject"] = SUBJECT

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    resp = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    print("ENVIADO OK. messageId:", resp.get("id"))

if __name__ == "__main__":
    main()
