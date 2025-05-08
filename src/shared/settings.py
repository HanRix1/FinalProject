from typing import Type
import dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_settings(cls: Type[BaseSettings]) -> BaseSettings:
    dotenv.load_dotenv()
    return cls()


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(str_strip_whitespace=True, env_prefix="database_")

    driver: str = "postgresql"
    async_driver: str = "postgresql+asyncpg"
    name: str
    username: str
    password: str
    host: str

    @property
    def url(self) -> str:
        return (
            f"{self.driver}://{self.username}:{self.password}@{self.host}/{self.name}"
        )

    @property
    def async_url(self) -> str:
        return f"{self.async_driver}://{self.username}:{self.password}@{self.host}/{self.name}"


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(str_strip_whitespace=True, env_prefix="session_")

    secret_key: str
    redis_host: str
    redis_port: int
    ttl: int


class MailSettings(BaseSettings):
    model_config = SettingsConfigDict(str_strip_whitespace=True, env_prefix="mail_")

    username: str
    password: str
    from_mail: str
    port: str
    server: str
    from_name: str
