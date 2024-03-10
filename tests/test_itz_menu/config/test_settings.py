import pytest
from pydantic import ValidationError

from itz_menu.config.settings import Settings


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
    def test_settings_with_valid_menu_check_interval():
        settings = Settings(menu_check_interval=3600)
        assert settings.menu_check_interval == 3600

    @staticmethod
    def test_settings_with_invalid_menu_check_interval():
        with pytest.raises(ValidationError):
            Settings(menu_check_interval=0)
