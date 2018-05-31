import unittest
import numpy as np

from hqbot import answer_bot


class ImageTestCase(unittest.TestCase):
    """ Tests functions relating to the images """

    def setUp(self):
        self.screen = answer_bot.screen_grab(save=False, location=None)
        self.preprocessed = answer_bot.preprocess_img(self.screen)

    def test_type_img(self):
        """ Test the type returned from `screen_grab()` and `preprocess_img()` """

        self.assertIsInstance(
            self.screen, np.ndarray)

        self.assertIsInstance(
            self.preprocessed, np.ndarray
        )

    def test_img_dimensions(self):
        """ Test the dimensions of the image """
        def image_in_bounds(img, max_width=500, max_height=500):
            width, height, _ = img.shape
            if width > max_width or height > max_height:
                return False
            else:
                return True

        self.assertTrue(image_in_bounds(self.screen))

        width, height, _ = self.screen.shape
        new_width, new_height = self.preprocessed.shape
        check = new_width == width / 2 and new_height == height / 2
        self.assertTrue(check)

    def test_preprocess_img(self):
        """ Test if the images are the same or not """
        self.assertFalse(np.array_equal(self.screen, self.preprocessed))


if __name__ == '__main__':
    unittest.main()
