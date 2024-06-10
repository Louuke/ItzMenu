import hashlib
import base64


def bytes_to_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def bytes_to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode('utf-8')


def load_image(path: str) -> bytes:
    with open(path, 'rb') as file:
        return file.read()
