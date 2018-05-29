import os
import sys
import unittest
from random import shuffle
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import answer_bot

class ImageTestCase(unittest.TestCase):
    """ Tests functions relating to the images """
    def setUp(self):
        self.screen = answer_bot.screen_grab(save=False, location=None)
        self.preprocessed = answer_bot.preprocess_img(self.screen)

    def test_type_img(self):
        """
        Test the type returned from `screen_grab()` and `preprocess_img()`
        """

        self.assertIsInstance(
            self.screen, np.ndarray)

        self.assertIsInstance(
            self.preprocessed, np.ndarray
        )

    def test_img_dimensions(self):
        """ Test the dimensions of the image """
        def imageInBounds(img, maxWidth=500, maxHeight=500):
            width, height, _ = img.shape
            if width > maxWidth or height > maxHeight:
                return False
            else:
                return True

        self.assertTrue(imageInBounds(self.screen))

        width, height, _ = self.screen.shape
        newWidth, newHeight = self.preprocessed.shape
        check = newWidth == width/2 and newHeight == height/2
        self.assertTrue(check)

    def test_preprocess_img(self):
        """ Test if the images are the same or not """
        self.assertFalse(np.array_equal(self.screen, self.preprocessed))

if __name__ == '__main__':
    unittest.main()