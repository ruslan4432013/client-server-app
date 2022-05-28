"""Unit-тесты клиента"""

import sys
import os
import unittest

from config.errors import ServerError, ReqFieldMissingError

sys.path.append(os.path.join(os.getcwd(), '..'))
from config.varibales_jim_protocol import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from client import create_presence, process_response_ans


class TestClass(unittest.TestCase):
    def test_def_presense(self):
        test = create_presence()
        test[TIME] = 1.1

        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_200_ans(self):
        self.assertEqual(process_response_ans({RESPONSE: 200}), '200 : OK')

    def test_400_ans(self):
        with self.assertRaises(ServerError):
            process_response_ans({RESPONSE: 400, ERROR: 'Bad Request'})

    def test_no_response(self):
        self.assertRaises(ReqFieldMissingError, process_response_ans, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
