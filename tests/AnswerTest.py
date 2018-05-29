import os
import sys
import unittest
from random import shuffle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import answer_bot
from answer_bot import bcolors

class GoogleWikiTestCase(unittest.TestCase):
    """ Tests for answer_bot """

    def test_question_one(self):
        neg = False

        question = "which of these songs does not feature whistling?"
        options = [
            "Graveyard Whistling",
            "Young Folks",
            "Pumped Up Kicks"
        ]

        shuffle(options)
        simq = ""
        points = []

        simq, neg = answer_bot.simplify_ques(question, debug=True)

        maxo=""
        m = 1
        if neg:
            m =- 1

        points, maxo = answer_bot.google_wiki_faster(simq, options, neg)
        check = maxo[1] == "graveyard whistling"
        self.assertTrue(check)

if __name__ == '__main__':
    unittest.main()
