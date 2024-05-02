import io

import numpy as np
from PIL import Image

import itzmenu.ocr.preprocess as preprocess
import itzmenu.ocr.extractor as extractor


class TestPreprocess:

    def test_convert_to_grayscale(self, week_menu: bytes):
        @preprocess.convert_to_grayscale
        def dummy_func(img: bytes) -> bytes:
            return img

        # Apply the apply_threshold decorator through the dummy function
        image = dummy_func(week_menu)

        # Load the image and convert it to a numpy array
        pimage = Image.open(io.BytesIO(image)).convert('L')
        image_np = np.array(pimage)

        # Check if it is a grayscale image
        assert len(image_np.shape) == 2

        tolerance = 20
        # Check if the image is thresholded correctly
        unique_colors = np.unique(image_np)
        black_range = range(0, tolerance + 1)
        white_range = range(255 - tolerance, 256)
        assert all(color in black_range or color in white_range for color in unique_colors)

    def test_crop_table(self, week_menu: bytes):
        @preprocess.crop_table
        def dummy_func(img: bytes) -> bytes:
            return img

        pimage_org = Image.open(io.BytesIO(week_menu))
        with_org, height_org = pimage_org.size

        # Apply the crop_main_image_content decorator through the dummy function
        image = dummy_func(week_menu)

        pimage_cropped = Image.open(io.BytesIO(image))
        with_cropped, height_cropped = pimage_cropped.size

        # Check if the image is cropped correctly
        assert with_org > with_cropped
        assert height_org > height_cropped

        jpg_image = io.BytesIO()
        pimage_cropped.save(jpg_image, 'JPEG')
        assert extractor.period_of_validity(jpg_image.getvalue()) is None

    def test_parse_validity_parameter(self, week_menu: bytes):
        @preprocess.parse_validity_parameter
        def dummy_func(img: bytes, *args, **kwargs):
            validity_period = kwargs.get('validity_period')
            assert img == week_menu
            assert len(args) == 0
            assert validity_period is not None
            assert validity_period == (1708297200, 1708729199)
        dummy_func(week_menu)

    def test_remove_no_holidays(self, week_menu: bytes):
        @preprocess.crop_table
        def dummy_func_1(img: bytes) -> bytes:
            return img
        cropped_image = dummy_func_1(week_menu)
        pimage_cropped = Image.open(io.BytesIO(cropped_image))

        @preprocess.parse_validity_parameter
        @preprocess.crop_table
        @preprocess.remove_holidays
        def dummy_func2(img: bytes):
            return img
        no_holidays_image = dummy_func2(week_menu)
        pimage_no_holidays = Image.open(io.BytesIO(no_holidays_image))

        # Check if the width of the images is the same
        assert pimage_cropped.size[0] == pimage_no_holidays.size[0]
        # Check if the height of the image is reduced, because rows are removed
        assert pimage_cropped.size[1] > pimage_no_holidays.size[1]

    def test_remove_holidays(self, week_menu_holiday: bytes):
        @preprocess.crop_table
        def dummy_func_1(img: bytes) -> bytes:
            return img

        cropped_image = dummy_func_1(week_menu_holiday)
        pimage_cropped = Image.open(io.BytesIO(cropped_image))

        @preprocess.parse_validity_parameter
        @preprocess.crop_table
        @preprocess.remove_holidays
        def dummy_func2(img: bytes):
            return img
        no_holidays_image = dummy_func2(week_menu_holiday)
        pimage_no_holidays = Image.open(io.BytesIO(no_holidays_image))

        # Check if the width of the images less than the original image
        assert pimage_cropped.size[0] > pimage_no_holidays.size[0]
        # Check if the height of the image is reduced, because rows are removed
        assert pimage_cropped.size[1] > pimage_no_holidays.size[1]


