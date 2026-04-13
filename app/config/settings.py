"""Application settings loaded from .env file."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url  : str
    app_name      : str
    app_version   : str
    debug         : bool = False
    groq_api_key  : str
    log_level     : str  = "INFO"
    environment   : str  = "dev"

    model_config = {"env_file": ".env"}


settings = Settings()