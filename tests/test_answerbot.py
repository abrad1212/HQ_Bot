import urllib.request as urllib2
import pytest
import numpy as np

from hqbot import answerbot

SIMPLIFY_QUES_DATA = [
    # question, clean_question, neg
    (
        "Which of these countries is NOT in Scandinavia?",
        "countries scandinavia?",
        True),
    (
        "The hottest multiplayer video game this year was designed by which famous gamer?",
        "hottest multiplayer video game year was designed famous gamer?",
        False
    ),
    (
        "Which of these state names is NOT a Native American word or phrase?",
        "state names native american word or phrase?",
        True
    ),
    (
        "Which pathogen is identifed by abnormally folded, \
            transmissible proteins causing rare and fatal diseases?",
        "pathogen identifed abnormally folded, transmissible proteins causing rare fatal diseases?",
        False
    )
]

def test_screen_grab():
    assert isinstance(answerbot.screen_grab(save=False, location=None), np.ndarray)

    with pytest.raises(TypeError):
        answerbot.screen_grab(save=False, location=5)


def test_preprocess_img():
    img = answerbot.screen_grab(save=False, location=None)
    assert isinstance(answerbot.preprocess_img(img), np.ndarray)


def test_preprocess_img_exception():
    with pytest.raises(TypeError):
        answerbot.preprocess_img(img=None)


def test_read_screen():
    assert isinstance(answerbot.read_screen(), str)


def test_parse_question():
    question, options = answerbot.parse_question(save=False)
    assert isinstance(question, str)
    assert isinstance(options, list)


@pytest.mark.parametrize("question,clean_question,neg", SIMPLIFY_QUES_DATA)
def test_simplify_ques(question, clean_question, neg):
    processed_question, actual_neg = answerbot.simplify_ques(question, debug=True)
    assert processed_question == clean_question and actual_neg == neg

    with pytest.raises(TypeError):
        answerbot.simplify_ques(question=[])


@pytest.mark.parametrize("link", [
    "https://wikipedia.org/",
    "https://en.wikipedia.org/wiki/HQ_Trivia",
    "https://google.com/"
])
def test_get_page(link):
    assert isinstance(answerbot.get_page(link), bytes)

    with pytest.raises((urllib2.URLError, urllib2.HTTPError, ValueError)):
        answerbot.get_page("4584")
