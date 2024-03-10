import hashlib
from datetime import datetime


def bytes_to_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def timestamp_to_date(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y')
