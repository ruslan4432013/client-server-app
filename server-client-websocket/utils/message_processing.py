import json

from websockets.legacy.client import WebSocketClientProtocol
from config.settings import ENCODING
from utils.decorators import Log


@Log()
async def get_message(client: WebSocketClientProtocol):
    encoded_response = await client.recv()
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


@Log()
async def send_message(websocket: WebSocketClientProtocol, message):
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    await websocket.send(encoded_message)
