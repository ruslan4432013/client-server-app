import os
import sys
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from server import process_client_message
from config.varibales_jim_protocol import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE


class ServerTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.error_msg = {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }

        self.success_msg = {
            RESPONSE: 200
        }

    def test_no_action(self):
        message_without_action = {
            TIME: 1.1,
            USER: {ACCOUNT_NAME: 'Guest'}
        }

        self.assertEqual(process_client_message(message_without_action), self.error_msg)

    def test_unknown_action(self):
        message_with_unknown_action = {ACTION: 'Unknown', TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}
        self.assertEqual(process_client_message(message_with_unknown_action), self.error_msg)

    def test_without_time(self):
        message_without_time = {ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}}
        self.assertEqual(process_client_message(message_without_time), self.error_msg)

    def test_without_user(self):
        message_without_user = {ACTION: PRESENCE, TIME: '1.1'}
        self.assertEqual(process_client_message(message_without_user), self.error_msg)

    def test_unknown_user(self):
        message_with_unknown_user = {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Unknown'}}

        self.assertEqual(process_client_message(message_with_unknown_user), self.error_msg)

    def test_success_check(self):
        message = {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}

        self.assertEqual(process_client_message(message), self.success_msg)


if __name__ == '__main__':
    unittest.main()
