from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import re


class Settings(BaseSettings):
    log_level: str = Field(default='INFO', pattern=r'^(NOTSET|DEBUG|INFO|WARNING|ERROR|CRITICAL)$')
    mongo_db_url: str = Field(default='mongodb://localhost:27017', pattern=r'^mongodb(.+srv)?://.*')
    mongo_db_name: str = Field(default='development', min_length=3)
    mongo_db_test_name: str = Field(default='test', min_length=3)

    model_config = SettingsConfigDict(env_file='settings.env', env_file_encoding='utf-8')

    def __str__(self):
        truncated_url = re.sub(r'(?<=://).+@', 'XXX:XXX@', self.mongo_db_url)
        return f'mongo_db_url={truncated_url}, mongo_db_name={self.mongo_db_name}, ' \
               f'mongo_db_test_name={self.mongo_db_test_name}'
