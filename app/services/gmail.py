# app/services/gmail_service.py
import base64
import logging
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.settings import settings

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

log = logging.getLogger("uvicorn.error")


def _build_gmail_service():
    """
    Crea y devuelve el cliente de la API de Gmail usando el token
    configurado en settings.gmail_token_file.
    """
    creds = Credentials.from_authorized_user_file(settings.gmail_token_file, SCOPES)
    return build("gmail", "v1", credentials=creds)


def send_email(to_email: str, name: str, phone: str) -> dict:
    """
    Envía el correo de bienvenida al usuario.
    Si falla la llamada a Gmail API, se propaga el HttpError (FastAPI responderá 500).
    """
    try:
        service = _build_gmail_service()

        subject = f"¡Bienvenido, {name}!"
        body = f"Hola {name}, tu registro fue exitoso. Tu número es {phone}."

        msg = MIMEText(body)
        msg["to"] = to_email
        msg["from"] = settings.from_email  # misma cuenta que autorizó el token o alias verificado
        msg["subject"] = subject

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        resp = service.users().messages().send(userId="me", body={"raw": raw}).execute()
        # resp incluye el id del mensaje
        return {"status": "sent", "id": resp.get("id")}
    except HttpError:
        # Propagamos el error para que FastAPI responda 500 con el detalle
        raise


def send_admin_new_user_email(admin_email: str, name: str, email: str, phone: str) -> dict:
    """
    Envía un correo al administrador avisando que se creó una nueva cuenta.

    A diferencia de send_email (usuario), acá NO queremos romper el flujo
    si falla el envío, así que atrapamos el HttpError y solo lo registramos.
    """
    if not admin_email:
        # Si no hay mail de admin configurado, no hacemos nada.
        log.warning("ADMIN_EMAIL no configurado; se omite notificación al administrador.")
        return {"status": "skipped", "reason": "admin_email_not_configured"}

    try:
        service = _build_gmail_service()

        subject = "Nuevo usuario registrado"
        body = (
            "Se ha creado una nueva cuenta de usuario.\n\n"
            f"Nombre: {name}\n"
            f"Email: {email}\n"
            f"Teléfono: {phone}\n"
        )

        msg = MIMEText(body)
        msg["to"] = admin_email
        msg["from"] = settings.from_email
        msg["subject"] = subject

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        resp = service.users().messages().send(userId="me", body={"raw": raw}).execute()

        return {"status": "sent", "id": resp.get("id")}
    except HttpError as e:
        # No tiramos 500, solo logueamos el problema.
        log.warning("No se pudo enviar mail al admin: %s", e)
        return {"status": "error", "detail": str(e)}
