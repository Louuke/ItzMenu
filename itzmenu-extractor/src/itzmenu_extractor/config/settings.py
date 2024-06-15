from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import re


class Settings(BaseSettings):
    log_level: str = Field(default='INFO', pattern=r'^(NOTSET|DEBUG|INFO|WARNING|ERROR|CRITICAL)$')
    itz_menu_user_email: str = Field(default='')
    itz_menu_user_password: str = Field(default='')
    itz_menu_host: str = Field(default='http://localhost:8000',
                               pattern=r'^http(s)?://[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(:[0-9]+)?$')
    ocr_check_interval: int = Field(default=3600, ge=1)
    ocr_save_images: bool = Field(default=False)
    google_cloud_vision_api_key: str = Field(default='')
    google_cloud_vision_enabled: bool = Field(default=False)

    model_config = SettingsConfigDict(env_file='settings.env', env_file_encoding='utf-8')

    def __str__(self):
        truncated_password = re.sub(r'[a-zA-Z0-9-]+', 'XXX', self.itz_menu_user_password)
        truncated_api_key = re.sub(r'[a-zA-Z0-9-]+', 'XXX', self.google_cloud_vision_api_key)
        return f'Settings(log_level={self.log_level}, itz_menu_user_email={self.itz_menu_user_email}, ' \
               f'itz_menu_user_password={truncated_password}, itz_menu_host={self.itz_menu_host}, ' \
               f'ocr_check_interval={self.ocr_check_interval}, ocr_save_images={self.ocr_save_images}, ' \
               f'google_cloud_vision_api_key={truncated_api_key}, ' \
               f'google_cloud_vision_enabled={self.google_cloud_vision_enabled})'
