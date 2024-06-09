from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import re


class Settings(BaseSettings):
    mongo_db_url: str = Field(default='mongodb://localhost:27017', pattern=r'^mongodb(.+srv)?://.*')
    mongo_db_name: str = Field(default='development', min_length=3)
    mail_smtp_host: str = Field(default='localhost')
    mail_smtp_port: int = Field(default=587, ge=1, le=65535)
    mail_smtp_user: str = Field(default='user')
    mail_smtp_password: str = Field(default='password')
    mail_smtp_tls: bool = Field(default=True)
    mail_smtp_starttls: bool = Field(default=False)
    mail_smtp_skip_login: bool = Field(default=False)
    service_secret: str = Field(default='SECRET', min_length=6)
    service_host: str = Field(default='http://localhost:8000')

    model_config = SettingsConfigDict(env_file='settings.env', env_file_encoding='utf-8')

    def __str__(self):
        truncated_url = re.sub(r'(?<=://).+@', 'XXX:XXX@', self.mongo_db_url)
        return f'mongo_db_url={truncated_url}, mongo_db_name={self.mongo_db_name}'


settings = Settings()
