from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongo_db_url: str = Field(default='mongodb://localhost:27017', pattern=r'^mongodb(.+srv)?://.*')
    mongo_db_name: str = Field(default='development', min_length=3)

    model_config = SettingsConfigDict(env_file='settings.env', env_file_encoding='utf-8')
