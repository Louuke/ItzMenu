import requests

from itzmenu_extractor.config.settings import Settings
from itzmenu_extractor.util.image import bytes_to_base64


def image_to_string(image: bytes) -> str:
    # Create payload
    payload = {
        "requests": [
            {
                "image": {"content": bytes_to_base64(image)},
                "features": [
                    {"type": "DOCUMENT_TEXT_DETECTION"}
                ]
            }
        ]
    }
    # Post to API
    req = requests.post(url="https://vision.googleapis.com/v1/images:annotate",
                        json=payload,
                        params={"key": Settings().google_cloud_vision_api_key},
                        timeout=10)
    response = req.json()
    return response['responses'][0]['fullTextAnnotation']['text']
