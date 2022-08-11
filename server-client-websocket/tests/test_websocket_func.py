import asyncio
import os
import sys
import unittest
import websockets

sys.path.append(os.path.join(os.getcwd(), '..'))
from server import Server
from utils.message_processing import send_message, get_message
from config.varibales_jim_protocol import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR


# Создаем эхо-обработчик, который отправляет полученное сообщение обратно для веб-сокета
async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)


class WebSocketTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.good_message = {
            ACTION: PRESENCE,
            TIME: 111111.111111,
            USER: {
                ACCOUNT_NAME: 'Guest'
            }
        }

        self.bad_message = {
            ACTION: PRESENCE,
            TIME: 111111.111111,
            USER: {
                ACCOUNT_NAME: 'Unknown'
            }
        }

        self.test_dict_recv_ok = {RESPONSE: 200}
        self.test_dict_recv_err = {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._initialize_ws())

    def tearDown(self) -> None:
        self.websocket_client.close()
        self.websocket_server.close()

    async def _initialize_ws(self):
        test_name = self.id().split('.')[-1]

        match test_name:
            case 'test_send_message':
                self.websocket_server = await websockets.serve(echo, 'localhost', 8765)

            case _:
                self.websocket_server = await websockets.serve(Server.ws_handler, 'localhost', 8765)
        self.websocket_client = await websockets.connect("ws://localhost:8765")

    async def test_send_message(self):

        await send_message(self.websocket_client, self.good_message)

        response = await get_message(self.websocket_client)

        self.assertEqual(response, self.good_message)

        with self.assertRaises(ValueError):
            await send_message(self.websocket_client, 'Bad message')
            await get_message(self.websocket_client)

    async def test_get_message_ok(self):

        await send_message(self.websocket_client, self.good_message)
        good_response = await get_message(self.websocket_client)
        self.assertEqual(good_response, self.test_dict_recv_ok)

    async def test_get_message_bad(self):
        await send_message(self.websocket_client, self.bad_message)
        bad_response = await get_message(self.websocket_client)
        self.assertEqual(bad_response, self.test_dict_recv_err)


if __name__ == '__main__':
    unittest.main()
