import os
import time

import pickle
from rake_nltk import Metric, Rake


def load_words():
    word_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "Data",
        "words.pkl"
    )
    with open(word_path, "rb") as words_file:
        words = pickle.load(words_file)
        words_file.close()

    return words


def parse(text):
    if not isinstance(text, str):
        raise TypeError("Please provide a string for the text argument.")

    lines = text.splitlines()
    ques = ""
    options = []
    flag = False

    for line in lines:
        if not flag:
            ques = ques + " " + line
        if '?' in line:
            flag = True
            continue
        if flag:
            if line != '':
                options.append(line)

    ques = ques.lstrip()
    return ques, options


def simplify(ques):
    if not isinstance(ques, str):
        raise TypeError("Please provide a string for the question argument.")

    stime = time.time()
    stop = load_words()
    neg = False

    ques_split = ques.lower().split()
    for word in ques_split:
        if word in stop:
            neg = True

    rake = Rake(ranking_metric=Metric.WORD_FREQUENCY)
    rake.extract_keywords_from_text(ques)

    print("Simplify Question Elapsed Time: {}".format(time.time() - stime))

    return rake.get_ranked_phrases(), neg


def combine(simplified):
    if not isinstance(simplified, (list, tuple)):
        raise TypeError("Please provide a list or tuple for the simplified argument.")

    return ' '.join([x.lower() for x in simplified]) + "?"


def split(source):
    """Split string

    Arguments:
        source {string} -- The string to be split

    Returns:
        string -- Split string
    """
    if not isinstance(source, str):
        raise TypeError("Please provide a string for the `source` argument.")

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
