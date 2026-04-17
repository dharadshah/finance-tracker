"""Application settings loaded from .env file."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url            : str
    app_name                : str
    app_version             : str
    debug                   : bool  = False
    groq_api_key            : str
    log_level               : str   = "INFO"
    environment             : str   = "dev"
    langchain_tracing_v2    : bool  = False
    langchain_endpoint      : str   = "https://api.smith.langchain.com"
    langchain_api_key       : str   = ""
    langchain_project       : str   = "finance-tracker"

    model_config = SettingsConfigDict(
        env_file          = ".env",
        env_file_encoding = "utf-8"
    )


settings = Settings()