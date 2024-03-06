import cv2

import itz_menu.ocr.preprocessing as preprocessing
import numpy as np


class TestPreprocessing:

    def test_threshold(self, week_menu: bytes):
        image_bytes = preprocessing.threshold(week_menu)
        image = self.__bytes_to_image(image_bytes)
        assert np.max(image) == 255
        assert np.min(image) == 0

    @staticmethod
    def __bytes_to_image(image: bytes):
        return cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
