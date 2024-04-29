import pytest
from pydantic import ValidationError

from itzmenu.config.settings import Settings


class TestSettings:

    @staticmethod
    def test_settings_with_valid_mongodb_data():
        settings = Settings(mongo_db_url='mongodb://localhost:27017', mongo_db_name='development')
        assert settings.mongo_db_url == 'mongodb://localhost:27017'
        assert settings.mongo_db_name == 'development'

    @staticmethod
    def test_settings_with_valid_mongodb_srv_data():
        settings = Settings(mongo_db_url='mongodb+srv://localhost:27017', mongo_db_name='development')
        assert settings.mongo_db_url == 'mongodb+srv://localhost:27017'
        assert settings.mongo_db_name == 'development'

    @staticmethod
    def test_settings_with_invalid_mongo_db_url():
        with pytest.raises(ValidationError):
            Settings(mongo_db_url='not a url', mongo_db_name='development')

    @staticmethod
    def test_settings_with_invalid_mongo_db_name():
        with pytest.raises(ValidationError):
            Settings(mongo_db_url='mongodb://localhost:27017', mongo_db_name='a')

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
