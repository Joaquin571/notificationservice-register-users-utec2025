# app/main.py
from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

from app.settings import settings
from app.services.gmail import send_email



log = logging.getLogger("uvicorn.error")
app = FastAPI(title="Notification Service", version="1.0")

def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if token != settings.notify_api_token:
        raise HTTPException(status_code=401, detail="Invalid token")

class WelcomePayload(BaseModel):
    to: EmailStr
    name: str
    phone: str

@app.get("/health")
def health():
    return {"status": "ok", "gmail_api_enabled": settings.gmail_api_enabled}

@app.post("/notify/email/welcome")
def notify_email_welcome(payload: WelcomePayload, _=Depends(verify_token)):
    log.info(f"📧 welcome -> to={payload.to} name={payload.name} phone={payload.phone}")
    if not settings.gmail_api_enabled:
        return {"status": "simulated", "to": payload.to}

    # Llama al helper que envía por Gmail y devuelve el ID real
    result = send_email(payload.to, payload.name, payload.phone)
    # result debe incluir el "id" del mensaje
    return result

@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}
