import hashlib
import sys
from datetime import datetime


def bytes_to_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def timestamp_to_date(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y')


def load_image(path: str) -> bytes:
    with open(path, 'rb') as file:
        return file.read()


def is_test_running():
    return 'pytest' in sys.modules or 'unittest' in sys.modules
