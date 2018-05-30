import os
import sys
import unittest
from random import shuffle

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import answer_bot


class GoogleWikiTestCase(unittest.TestCase):
    """ Tests for answer_bot """

    def test_question_one(self):
        """ Test `google_wiki_faster()` """
        neg = False

        question = "which of these songs does not feature whistling?"
        options = [
            "Graveyard Whistling",
            "Young Folks",
            "Pumped Up Kicks"
        ]

        shuffle(options)
        simq = ""

        simq, neg = answer_bot.simplify_ques(question, debug=True)

        maxo = ""

        _, maxo = answer_bot.google_wiki_faster(simq, options, neg)
        check = maxo[1] == "graveyard whistling"
        self.assertTrue(check)

    def test_simplify_ques_neg(self):
        """ Test if `simplify_ques` correctly returns neg """

        question = "Which of these countries is NOT in Scandinavia?"
        _, neg = answer_bot.simplify_ques(question, debug=True)

        check = neg is True
        self.assertTrue(check)

    def test_split_string(self):
        """ Test `split_string()` """

        ques = "when was google formed?"
        expected = ["when", "was", "google", "formed"]

        words = answer_bot.split_string(ques)
        check = expected == words and isinstance(words, list)
        self.assertTrue(check)


if __name__ == '__main__':
    unittest.main()
