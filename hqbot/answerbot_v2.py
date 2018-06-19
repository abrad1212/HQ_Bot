import os

#import cv2
from PIL import Image
from PIL import ImageFilter
from PIL import ImageGrab

import pytesseract
import numpy as np

try:
    import question
    import search
except ImportError:
    from . import question
    from . import search

def grab_screen(save=False):
    if not isinstance(save, bool):
        raise TypeError("Please provide a boolean for the save argument.")

    img = ImageGrab.grab(bbox=(20, 260, 520, 700))

    if save:
        pass

    return img


def preprocess_img(img):
    if not isinstance(img, Image.Image):
        raise TypeError("Please provide a valid PIL Image for the img argument.")

    resize_width = 250

    img = img.convert("L")
    img = img.point(lambda p: p > 100 and 255)
    img = img.filter(ImageFilter.UnsharpMask())

    w_percent = (resize_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((resize_width, h_size), Image.ANTIALIAS)

    return img


def get_text(img=None):
    if img is not None and not isinstance(img, Image.Image):
        raise TypeError("Please provide a valid image file or `None` for img argument.")

    if img is None:
        img = grab_screen()
        img = preprocess_img(img)

    text = pytesseract.image_to_string(img, lang="eng")
    return text


def cmd_main():
    text = get_text()
    ques, options = question.parse(text)

    try:
        while options is None or len(options) < 3:
            text = get_text()
            ques, options = question.parse(text)
    except KeyboardInterrupt:
        print("Stopping loop")

    simplified, neg = question.simplify(text)
    simplified = question.combine(simplified)
    print("Simplified Question: {}".format(simplified))


if __name__ == "__main__":
    while True:
        KEY_PRESSED = input('Press s to screenshot live game or q to quit:\n')
        if KEY_PRESSED == 's':
            cmd_main()
        elif KEY_PRESSED == 'q':
            break
        else:
            print("Unknown Input")
