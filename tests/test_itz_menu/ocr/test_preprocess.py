import cv2

import itz_menu.ocr.preprocess as preprocess
import numpy as np


class TestPreprocess:

    def test_apply_threshold(self, week_menu: bytes):
        @preprocess.apply_threshold
        def dummy_func(img: bytes) -> bytes:
            return img

        # Apply the apply_threshold decorator through the dummy function
        image = dummy_func(week_menu)

        # Check if the image is grayscale and binary
        image_np = self.__bytes_to_image(image)
        assert np.max(image_np) == 255
        assert np.min(image_np) == 0

    @staticmethod
    def __bytes_to_image(image: bytes):
        return cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
