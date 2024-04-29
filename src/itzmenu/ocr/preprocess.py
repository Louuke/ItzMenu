from io import BytesIO
import logging as log

from PIL import Image
import numpy as np
import cv2

from itzmenu.time import is_holiday


def apply_threshold(func):
    """ Apply a threshold to the given image """
    def wrapper(image: bytes, **kwargs) -> bytes:
        cv_img = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
        cv_img_gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        cv_img_threshold = cv2.threshold(cv_img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        processed_image = cv2.imencode(".jpg", cv_img_threshold)[1].tobytes()
        return func(processed_image, **kwargs)
    return wrapper


def crop_main_image_content(func):
    """ Crop the main content of the image excluding the header and footer """
    def wrapper(image: bytes, *args, **kwargs) -> bytes:
        image = Image.open(BytesIO(image))
        # Get the width and height of the image
        width, height = image.size
        if width != 3508 or height != 2479:
            log.error(f'Image has unexpected dimensions: {width}x{height}')

        # Define the area to be cropped
        area = (118, 345, width - 118, height - 414)
        # Crop the image
        cropped_image = image.crop(area)
        cropped_image_bytes = __image_to_bytes(cropped_image)
        return func(cropped_image_bytes, *args, **kwargs)
    return wrapper


def __concat_images_horizontally(images: list[Image]) -> Image:
    """ Concatenate a list of images horizontally """
    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights)
    new_image = Image.new('RGB', (total_width, max_height))
    x_offset = 0
    for img in images:
        new_image.paste(img, (x_offset, 0))
        x_offset += img.size[0]
    return new_image


def __concat_images_vertically(images: list[Image]) -> Image:
    """ Concatenate a list of images vertically """
    widths, heights = zip(*(i.size for i in images))
    max_width = max(widths)
    total_height = sum(heights)
    new_image = Image.new('RGB', (max_width, total_height))
    y_offset = 0
    for img in images:
        new_image.paste(img, (0, y_offset))
        y_offset += img.size[1]
    return new_image


def hide_holidays(image: bytes, validity_period: tuple[int, int]) -> bytes:
    """
    Hide days when the cafeteria is closed because of holidays
    :param image: The image to process
    :param validity_period: The period of validity of the menu
    :return: The processed image
    """
    image = Image.open(BytesIO(image))
    # Get the width and height of the image
    # Define width of the columns
    columns = [437, 567, 567, 567, 567, 567]
    # Crop the image into horizontal parts
    parts = []
    for i, width in enumerate(columns):
        area = (sum(columns[:i]), 0, sum(columns[:i + 1]), image.height)
        parts.append(image.crop(area))
    # Determine which days of the work week are holidays
    holidays = [is_holiday(time) for time in range(validity_period[0], validity_period[1], 86400)]
    # Concatenate the images of the days when the cafeteria is open
    no_holiday_columns = [parts[i + 1] for i, holiday in enumerate(holidays) if not holiday]
    no_holiday_columns.insert(0, parts[0])
    horizontal_image = __concat_images_horizontally(no_holiday_columns)
    # Define height of the rows
    rows = [255, 189, 248, 248, 248, 248, 284]
    # Crop the image into vertical parts
    parts = []
    for i, height in enumerate(rows):
        if i != 1:
            area = (0, sum(rows[:i]), horizontal_image.width, sum(rows[:i + 1]))
            parts.append(horizontal_image.crop(area))
    return __image_to_bytes(__concat_images_vertically(parts))


def __image_to_bytes(image: Image) -> bytes:
    """ Convert an image to bytes """
    image_bytes = BytesIO()
    image.save(image_bytes, format='JPEG')
    return image_bytes.getvalue()
