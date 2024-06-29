from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource
import re


class Settings(BaseSettings):
    service_host: str = Field(default='127.0.0.1', description='host to run the service on')
    service_port: int = Field(default=8000, description='port to run the service on')
    service_secret: str = Field(default='SECRET', min_length=6)
    service_public_address: str = Field(default='http://localhost:8000')

    mongodb_url: str = Field(default='mongodb://localhost:27017', pattern=r'^mongodb(.+srv)?://.*')
    mongodb_name: str = Field(default='test', min_length=3)
    mail_smtp_host: str = Field(default='localhost')
    mail_smtp_port: int = Field(default=587, ge=1, le=65535)
    mail_smtp_user: str = Field(default='user')
    mail_smtp_password: str = Field(default='password')
    mail_smtp_tls: bool = Field(default=True)
    mail_smtp_starttls: bool = Field(default=False)
    mail_smtp_skip_login: bool = Field(default=False)

    log: str = Field(default='info', description='log level')

    model_config = SettingsConfigDict(env_file='settings.env', env_file_encoding='utf-8', cli_parse_args=True)

    def __str__(self):
        truncated_url = re.sub(r'(?<=://).+@', 'XXX:XXX@', self.mongodb_url)
        return f'mongodb_url={truncated_url}, mongodb_name={self.mongodb_name}'


settings = Settings()
