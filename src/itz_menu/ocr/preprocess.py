from io import BytesIO

from PIL import Image
import numpy as np
import cv2


def apply_threshold(func):
    """ Apply a threshold to the given image """
    def wrapper(image: bytes, **kwargs) -> bytes:
        cv_img = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
        cv_img_gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        cv_img_threshold = cv2.threshold(cv_img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        processed_image = cv2.imencode(".jpg", cv_img_threshold)[1].tobytes()
        return func(processed_image, **kwargs)
    return wrapper


def crop_image(func):
    """ Crop the given image """
    def wrapper(image: bytes, **kwargs) -> bytes:
        image = Image.open(BytesIO(image))
        # Get the width and height of the image
        width, height = image.size
        # Define the area to be cropped
        area = (120, 350, width-120, height-415)
        # Crop the image
        cropped_image = image.crop(area)
        # Save the cropped image
        cropped_image.save('cropped.jpg')
        # Convert the cropped image back to bytes
        cropped_image_bytes = BytesIO()
        cropped_image.save(cropped_image_bytes, format='JPEG')
        return func(cropped_image_bytes.getvalue(), **kwargs)
    return wrapper
