import hashlib
from pathlib import Path

import pandas as pd
import pytest
from unittest.mock import patch
from argparse import Namespace

from itzmenu_api.persistence.enums import WeekDay
from itzmenu_extractor.jobs import Executor


@pytest.fixture()
def week_menu_df(week_menu_csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(week_menu_csv_path)
    df.columns = df.columns.map(lambda x: WeekDay.find_by_value(x), na_action='ignore')
    df.set_index(df.columns[0], inplace=True)
    return df


def test_executor_starts_and_stops_scheduler():
    args = Namespace(log='info', preload=[])
    with patch('itzmenu_extractor.jobs.BlockingScheduler') as MockScheduler:
        executor = Executor(args)
        executor.start()
        MockScheduler.return_value.start.assert_called_once()
        executor.stop()
        MockScheduler.return_value.shutdown.assert_called_once()


def test_executor_preloads_menu_with_valid_filename():
    args = Namespace(log='info', preload=['valid.jpg'])
    with patch('itzmenu_extractor.jobs.image.load_image') as MockLoadImage, \
            patch('itzmenu_extractor.jobs.Executor.process_image') as MockProcessImage:
        executor = Executor(args)
        executor.preload_menu()
        MockLoadImage.assert_called_once_with('valid.jpg')
        MockProcessImage.assert_called_once()


def test_executor_preloads_menu_with_invalid_filename():
    args = Namespace(log='info', preload=['invalid'])
    with patch('itzmenu_extractor.jobs.log.warning') as MockLogWarning:
        executor = Executor(args)
        executor.preload_menu()
        MockLogWarning.assert_called_once_with('Invalid filename: invalid')


def test_executor_fetches_menu_and_processes_image():
    args = Namespace(log='info', preload=[])
    with patch('itzmenu_extractor.jobs.MenuClient') as MockMenuClient, \
            patch('itzmenu_extractor.jobs.Executor.process_image') as MockProcessImage:
        executor = Executor(args)
        executor.fetch_menu()
        MockMenuClient.return_value.get_week_menu.assert_called_once()
        MockProcessImage.assert_called_once()


def test_executor_processes_image_and_skips_existing_menu():
    args = Namespace(log='info', preload=[])
    with patch('itzmenu_extractor.jobs.ItzMenuClient') as MockItzMenuClient, \
            patch('itzmenu_extractor.jobs.log.info') as MockLogInfo:
        executor = Executor(args)
        MockItzMenuClient.return_value.get_menu_by_id_or_checksum.return_value = True
        executor.process_image(b'image_bytes')
        MockItzMenuClient.return_value.get_menu_by_id_or_checksum.assert_called_once()
        checksum = hashlib.sha256(b'image_bytes').hexdigest()
        MockLogInfo.assert_called_once_with(f'Menu with checksum {checksum} already exists')


def test_executor_processes_image_and_handles_extraction_failure_1():
    args = Namespace(log='info', preload=[])
    with patch('itzmenu_extractor.jobs.extractor.period_of_validity', return_value=None), \
            patch('itzmenu_extractor.jobs.ItzMenuClient') as MockItzMenuClient, \
            patch('itzmenu_extractor.jobs.log.warning') as MockLogWarning:
        executor = Executor(args)
        MockItzMenuClient.return_value.get_menu_by_id_or_checksum.return_value = None
        executor.process_image(b'image_bytes')
        MockLogWarning.assert_called_once_with('Failed to extract menu from image')


def test_executor_processes_image_and_handles_extraction_failure_2():
    args = Namespace(log='info', preload=[])
    with patch('itzmenu_extractor.jobs.extractor.period_of_validity', return_value=(1708297200, 1708729199)), \
            patch('itzmenu_extractor.jobs.extractor.img_to_dataframe', return_value=None), \
            patch('itzmenu_extractor.jobs.ItzMenuClient') as MockItzMenuClient, \
            patch('itzmenu_extractor.jobs.log.warning') as MockLogWarning:
        executor = Executor(args)
        MockItzMenuClient.return_value.get_menu_by_id_or_checksum.return_value = None
        executor.process_image(b'image_bytes')
        MockLogWarning.assert_called_once_with('Failed to extract menu from image')


def test_executor_processes_image_success(week_menu: bytes, week_menu_df: pd.DataFrame):
    args = Namespace(log='info', preload=[])
    with patch('itzmenu_extractor.jobs.extractor.period_of_validity', return_value=(1708297200, 1708729199)), \
            patch('itzmenu_extractor.jobs.extractor.img_to_dataframe', return_value=week_menu_df), \
            patch('itzmenu_extractor.jobs.ItzMenuClient') as MockItzMenuClient, \
            patch('itzmenu_extractor.jobs.log.info') as MockLogInfo:
        executor = Executor(args)
        MockItzMenuClient.return_value.get_menu_by_id_or_checksum.return_value = None
        executor.process_image(week_menu)
        MockItzMenuClient.return_value.create_menu.assert_called_once()
