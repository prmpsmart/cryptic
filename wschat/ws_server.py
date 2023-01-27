from .ws_commons import *


class ClientHandler(PRMP_WebSocketHandler):
    def __init__(self, socket, addr, server: "Server"):
        super().__init__(socket, addr, server)

    def on_message(self):
        ...

    def on_ping(self):
        ...

    def on_pong(self):
        ...

    def on_closed(self):
        ...

    def send_json(self, data: Json) -> int:
        _json = data.to_str()
        return self.send_message(_json)


class Server(PRMP_WebSocketServer):
    Handler = ClientHandler
    allow_reuse_address = True
