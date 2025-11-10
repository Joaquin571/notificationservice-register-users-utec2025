"""Notification service API.

Expone endpoints para:
- Health checks (/health, /healthcheck)
- Envío de mails de bienvenida (/notify/email/welcome)
con autenticación mediante token Bearer.
"""
import logging
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel, EmailStr

from app.settings import settings
from app.services.gmail import send_email, send_admin_new_user_email

# Usamos el logger de uvicorn para que se integre con los logs del servidor
log = logging.getLogger("uvicorn.error")

app = FastAPI(title="Notification Service", version="1.0")


def verify_token(authorization: Optional[str] = Header(None)):
    """Valida el header Authorization con esquema Bearer simple.

    - Requiere un header: Authorization: Bearer <token>
    - Compara el token recibido con settings.notify_api_token
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if token != settings.notify_api_token:
        raise HTTPException(status_code=401, detail="Invalid token")


class WelcomePayload(BaseModel):
    """Payload del correo de bienvenida enviado al usuario."""

    to: EmailStr
    name: str
    phone: str


@app.get("/health")
def health():
    """Health check principal del servicio de notificaciones."""
    return {"status": "ok", "gmail_api_enabled": settings.gmail_api_enabled}


@app.post("/notify/email/welcome")
def notify_email_welcome(payload: WelcomePayload, _=Depends(verify_token)) -> dict:
    """Envía un mail de bienvenida al usuario y notifica al admin (si está configurado)."""
    log.info(
        "📧 welcome -> to=%s name=%s phone=%s",
        payload.to,
        payload.name,
        payload.phone,
    )

    if not settings.gmail_api_enabled:
        # Modo simulación: no llama a Gmail, solo responde ok
        return {"status": "simulated", "to": payload.to}

    # 1) Mail al usuario (comportamiento original)
    result = send_email(payload.to, payload.name, payload.phone)

    # 2) Mail al admin avisando del nuevo usuario (si ADMIN_EMAIL está seteado)
    if getattr(settings, "admin_email", None):
        try:
            send_admin_new_user_email(
                admin_email=settings.admin_email,
                name=payload.name,
                email=payload.to,
                phone=payload.phone,
            )
        except Exception as exc:
            # No rompemos el flujo si falla el mail al admin, solo logueamos
            log.warning("No se pudo enviar mail al admin: %s", exc)

    return result


@app.get("/healthcheck")
def healthcheck():
    """Healthcheck simple usado por Kubernetes / NLB."""
    return {"status": "ok"}
