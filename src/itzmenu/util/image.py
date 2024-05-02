import hashlib


def bytes_to_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_image(path: str) -> bytes:
    with open(path, 'rb') as file:
        return file.read()
