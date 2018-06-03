"""
HQ Bot forked from https://github.com/sushant10/HQ_Bot

Features:
    Grab screenshots from phone screen
    Multithreaded Google Search System

    Reflector 3 or QuickTime Player required
"""

# answering bot for trivia HQ and Cash Show
import os
import sys
import platform
import time
import json
from multiprocessing import Pool
from functools import partial
import urllib.request as urllib2

import cv2
from PIL import Image
from PIL import ImageGrab
from bs4 import BeautifulSoup
import numpy as np

from google import google
from halo import Halo
import pytesseract

from .utils import setup_path
from .utils import get_img_name

if platform.system() == "Windows":
    PATH = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'
    pytesseract.pytesseract.tesseract_cmd = PATH


# for terminal Colors
class Colors:  # pylint: disable=R0903, C0111
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# list of words to clean from the question during google search
REMOVE_WORDS = []

# negative words
NEGATIVE_WORDS = []


def load_json():
    """
    Load the remove and negative words
    that will be used for question parsing
    """

    global REMOVE_WORDS, NEGATIVE_WORDS  # pylint: disable=W0603
    this_dir, _ = os.path.split(__file__)
    settings_path = os.path.join(this_dir, "Data", "settings.json")

    with open(settings_path, "r", encoding="utf8") as settings_file:
        settings = json.loads(settings_file.read())

        REMOVE_WORDS = settings["remove_words"]
        NEGATIVE_WORDS = settings["negative_words"]

        settings_file.close()


def screen_grab(save, location):
    """Takes a screenshot of the user's screen

    Arguments:
        save {bool} -- Whether to save the image
        location {string} -- The location to save the image if `save` is True

    Returns:
        Numpy Array -- The screenshotted image
    """
    if location is not None and not isinstance(location, str):
        raise TypeError("Please provide a string for the location argument.")

    img = ImageGrab.grab(bbox=(20, 260, 520, 700))

    if save:
        img.save(location)

    return np.array(img)


def preprocess_img(img):
    """Preprocess image

    Arguments:
        img {Numpy Array} -- The image to be preprocessed

    Returns:
        Numpy Array -- The preprocessed image
    """
    if not isinstance(img, np.ndarray):
        raise TypeError('Please provide a valid image as a numpy array for preprocessing.')

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = cv2.threshold(gray, 0, 255,
                         cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    gray = cv2.resize(gray, (0, 0), fx=0.5, fy=0.5)
    return gray


def read_screen(save=False):
    """Takes a screenshot and processes the image.
    Then feeds the image to Google Tesseract OCR

    Returns:
        String -- The string(s) found in the image
    """

    spinner = Halo(text='Reading screen', spinner='bouncingBar')
    spinner.start()

    if save:
        screenshot_file = get_img_name()
    else:
        screenshot_file = None

    image = screen_grab(save, location=screenshot_file)
    gray = preprocess_img(image)

    # load the image as a PIL/Pillow image, apply OCR, and then delete the temporary file
    text = pytesseract.image_to_string(Image.fromarray(gray))

    spinner.succeed()
    spinner.stop()
    return text


def parse_question(save=False):
    """Gets the question and options from Tesseract

    Returns:
        String -- The retrieved question
        List -- The options retrived from the screen
    """

    text = read_screen(save)
    lines = text.splitlines()
    question = ""
    options = list()
    flag = False

    for line in lines:
        if not flag:
            question = question + " " + line
        if '?' in line:
            flag = True
            continue
        if flag:
            if line != '':
                options.append(line)

    return question, options


def simplify_ques(question, debug=False):
    """Preprocesses the question for the Google Search
    Removes all `REMOVE_WORDS` from the question

    Arguments:
        question {string} -- Original question

    Keyword Arguments:
        debug {bool} -- Whether to load json for debugging (default: {False})

    Returns:
        String -- The preprocessed question
        Bool -- Whether the question contains a `NEGATIVE_WORD`
    """
    if not isinstance(question, str):
        raise TypeError('Please provide a string for a question.')

    if debug is True:
        load_json()

    neg = False
    qwords = question.lower().split()
    for i in qwords:
        if i in NEGATIVE_WORDS:
            neg = True

    cleanwords = [word for word in qwords if word.lower() not in REMOVE_WORDS]
    temp = ' '.join(cleanwords)

    clean_question = ""
    for letter in temp:
        if letter != "?" or letter != "\"" or letter != "\'":
            clean_question = clean_question + letter

    return clean_question.lower(), neg


def smart_answer(content, qwords):
    """Answer by combining two words

    Arguments:
        content {bytes} -- The HTML of the webpage to search for `qwords`
        qwords {list} -- List of string containg each word of the question

    Returns:
        int -- The points calculated
    """

    zipped = zip(qwords, qwords[1:])
    points = 0
    for element in zipped:
        if content.count(element[0] + " " + element[1]) != 0:
            points += 1000
            print(points)
    return points


def split_string(source):
    """Split string

    Arguments:
        source {string} -- The string to be split

    Returns:
        string -- Split string
    """

    splitlist = ",!-.;/?@ #"
    output = []
    atsplit = True
    for char in source:
        if char in splitlist:
            atsplit = True
        else:
            if atsplit:
                output.append(char)
                atsplit = False
            else:
                output[-1] = output[-1] + char
    return output


def get_page(link):
    """Get a webpage

    Arguments:
        link {string} -- The website to read the HTML from.

    Returns:
        Bytes -- The HTML retrieved from the link
    """
    try:
        if link.find('mailto') != -1:
            return ''

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
        req = urllib2.Request(link, headers=headers)
        html = urllib2.urlopen(req).read()
        return html
    except (urllib2.URLError, urllib2.HTTPError, ValueError) as error:
        raise error

def process_search(option, sim_ques, neg, points):
    """The worker function for processing each option's search

    Arguments:
        option {string} -- The option to search Google for
        sim_ques {string} -- The question that is being processed and searched with `option`
        neg {bool} -- Whether the question contains a word from `NEGATIVE_WORDS`
        points {list} -- The point list being shared with all workers

    Returns:
        List -- Contains all the options and the one with the highest score
    """

    option = option.lower()
    original = option
    option += " wiki"

    search_wiki = google.search(option, 1)
    link = search_wiki[0].link

    content = get_page(link)
    soup = BeautifulSoup(content, "lxml")
    page = soup.get_text().lower()

    maxp = -sys.maxsize
    maxo = ""
    temp = 0

    words = split_string(sim_ques)

    for word in words:
        temp = temp + page.count(word)

    temp += smart_answer(page, words)

    if neg:
        temp *= -1

    points.append(temp)
    if temp > maxp:
        maxp = temp
        maxo = original

    return [points, maxo]


def google_wiki_faster(sim_ques, options, neg):
    """Googles the individual options' wikipedia page and
    finds each occurence of each word in the question.
    Then adds them up for that question's points.

    Arguments:
        sim_ques {string} -- The preprocessed question
        options {array_like} -- A list of options
        neg {bool} -- Whether the question contains a word from `NEGATIVE_WORDS`

    Returns:
        List -- Contains each option with their respective score
        String -- The highest scoring option
    """

    spinner = Halo(text='Googling and searching Wikipedia', spinner='dots2')
    spinner.start()

    points = list()
    maxo = ""

    pool = Pool(processes=3)

    process = partial(process_search, sim_ques=sim_ques,
                      neg=neg, points=points)
    points = pool.map(process, options)

    pool.close()
    pool.join()

    maxo = ""
    max_val = -sys.maxsize
    for option in points:
        val = option[0][0]
        if val > max_val:
            maxo = option
            max_val = val

    spinner.succeed()
    spinner.stop()
    return points, maxo


def get_points_live_v2(save=False):
    """ Handles all the logic to screenshot a live game
    with faster a faster execution time then `get_points_live()`"""

    start_time = time.time()

    neg = False

    parse_question_time = time.time()
    question, options = parse_question(save)
    print('Parse Question Elapsed Time: {} seconds'.format(
        time.time() - parse_question_time))

    simq = ""
    points = []

    simq, neg = simplify_ques(question)

    maxo = ""
    modifier = 1
    if neg:
        modifier = - 1

    google_start_time = time.time()
    try:
        points, maxo = google_wiki_faster(simq, options, neg)
    except IndexError as error:
        print("Sorry nothing could be searched")
        print("Error: {}".format(error))
    print('Google Search Elapsed Time: {} seconds'.format(
        time.time() - google_start_time))

    print("\n" + Colors.UNDERLINE + question + Colors.ENDC + "\n")
    for point, option in zip(points, options):
        if maxo[1] == option.lower():
            option = Colors.OKGREEN + option + Colors.ENDC
        else:
            option = Colors.FAIL + option + Colors.ENDC
        print(option + " { points: " + Colors.BOLD +
              str(point[0][0] * modifier) + Colors.ENDC + " } \n")

    print('Total Elapsed Time: {}'.format(time.time() - start_time))


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Flags for options")
    parser.add_argument('-s', action='store_true',
                        help="Whether the image of the question should be saved")
    args = parser.parse_args()

    setup_path()

    load_json()
    while True:
        key_pressed = input('Press s to screenshot live game or q to quit:\n')
        if key_pressed == 's':
            get_points_live_v2(save=args.s)
        elif key_pressed == 'q':
            break
        else:
            print(Colors.FAIL + "\nUnknown input" + Colors.ENDC)


if __name__ == "__main__":
    main()
