# app/settings.py
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    gmail_api_enabled: bool = Field(True, alias="GMAIL_API_ENABLED")
    gmail_credentials_file: str = Field("./secrets/credentials.json", alias="GMAIL_CREDENTIALS_FILE")
    gmail_token_file: str = Field("./secrets/token.json", alias="GMAIL_TOKEN_FILE")
    from_email: str = Field(..., alias="FROM_EMAIL")
    notify_api_token: str = Field("dev-secret", alias="NOTIFY_API_TOKEN")
    admin_email: str = Field("", alias="ADMIN_EMAIL")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
