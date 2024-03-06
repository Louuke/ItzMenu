import numpy as np
import cv2


def image_converter(func):
    def wrapper(image: bytes) -> bytes:
        cv_image = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
        img_arr = func(cv_image)
        return cv2.imencode(".jpg", img_arr)[1].tobytes()
    return wrapper


@image_converter
def threshold(image: bytes) -> bytes:
    """ Apply a threshold to the given image """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
