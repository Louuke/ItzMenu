import pytest
from pydantic import ValidationError

from itzmenu_extractor.config.settings import Settings


class TestSettings:

    @staticmethod
    def test_settings_with_valid_ocr_check_interval():
        settings = Settings(ocr_check_interval=3600)
        assert settings.ocr_check_interval == 3600

    @staticmethod
    def test_settings_with_invalid_ocr_check_interval():
        with pytest.raises(ValidationError):
            Settings(ocr_check_interval=0)

    @staticmethod
    def test_settings_with_valid_ocr_save_images():
        settings = Settings(ocr_save_images=True)
        assert settings.ocr_save_images is True
        settings = Settings(ocr_save_images='True')
        assert settings.ocr_save_images is True
        settings = Settings(ocr_save_images='true')
        assert settings.ocr_save_images is True
        settings = Settings(ocr_save_images='false')
        assert settings.ocr_save_images is False

    @staticmethod
    def test_settings_with_invalid_ocr_save_images():
        with pytest.raises(ValidationError):
            Settings(ocr_save_images='not a bool')

    @staticmethod
    def test_settings_with_valid_google_cloud_vision_api_key():
        settings = Settings(google_cloud_vision_api_key='api_key')
        assert settings.google_cloud_vision_api_key == 'api_key'

    @staticmethod
    def test_settings_with_valid_google_cloud_vision_enabled():
        settings = Settings(google_cloud_vision_enabled=True)
        assert settings.google_cloud_vision_enabled is True
        settings = Settings(google_cloud_vision_enabled='True')
        assert settings.google_cloud_vision_enabled is True
        settings = Settings(google_cloud_vision_enabled='true')
        assert settings.google_cloud_vision_enabled is True
        settings = Settings(google_cloud_vision_enabled='false')
        assert settings.google_cloud_vision_enabled is False

    @staticmethod
    def test_settings_with_invalid_log_level():
        with pytest.raises(ValidationError):
            Settings(log_level='INVALID')

    @staticmethod
    def test_settings_with_valid_log_level():
        level = ('NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        for lev in level:
            settings = Settings(log_level=lev)
            assert settings.log_level == lev

    @staticmethod
    def test_settings_with_valid_itzmenu_host():
        settings = Settings(itzmenu_host='http://localhost:8000')
        assert settings.itzmenu_host == 'http://localhost:8000'
        settings = Settings(itzmenu_host='https://itzmenu.com')
        assert settings.itzmenu_host == 'https://itzmenu.com'

    @staticmethod
    def test_settings_with_invalid_itzmenu_host():
        with pytest.raises(ValidationError):
            Settings(itzmenu_host='invalid_host')
