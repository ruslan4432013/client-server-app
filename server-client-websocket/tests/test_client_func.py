import os
import sys
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from client import create_presence, process_ans
from config.varibales_jim_protocol import RESPONSE, ERROR


class ClientTestCase(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.correct_presence_message = {'action': 'presence',
                                         'time': 1.1,
                                         'user': {'account_name': 'Guest'}}

    async def test_create_presence(self):
        message = await create_presence()
        message['time'] = 1.1
        self.assertEqual(message, self.correct_presence_message)

    async def test_process_ans_200(self):
        result = await process_ans({RESPONSE: 200})
        self.assertEqual(result, '200 : OK')

    async def test_process_ans_400(self):
        result = await process_ans({RESPONSE: 400, ERROR: 'Bad Request'})
        self.assertEqual(result, '400 : Bad Request')

    async def test_process_ans_no_response(self):
        with self.assertRaises(ValueError):
            await process_ans({ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
