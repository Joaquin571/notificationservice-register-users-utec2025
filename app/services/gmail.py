# app/services/gmail_service.py
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.settings import settings

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def send_email(to_email: str, name: str, phone: str) -> dict:
    try:
        creds = Credentials.from_authorized_user_file(settings.gmail_token_file, SCOPES)
        service = build("gmail", "v1", credentials=creds)

        subject = f"¡Bienvenido, {name}!"
        body = f"Hola {name}, tu registro fue exitoso. Tu número es {phone}."
        msg = MIMEText(body)
        msg["to"] = to_email
        msg["from"] = settings.from_email   # misma cuenta que autorizó el token o alias verificado
        msg["subject"] = subject

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        resp = service.users().messages().send(userId="me", body={"raw": raw}).execute()
        # resp incluye el id del mensaje
        return {"status": "sent", "id": resp.get("id")}
    except HttpError as e:
        # Propagamos el error para que FastAPI responda 500 con el detalle
        raise
