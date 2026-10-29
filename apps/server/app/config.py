from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    mongodb_uri: SecretStr | None = None
    mongodb_database: str = "baseball_mental"
    enable_kbo_probe: bool = False
