import logging
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    database_url: str
    app_name: str
    app_version: str
    debug: bool = False

    model_config = {"env_file": ".env"}


settings = Settings()