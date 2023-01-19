from .ws_commons import *


class ClientHandler(PRMP_WebSocketHandler):
    def __init__(self, socket, addr, server: "Server"):
        super().__init__(socket, addr, server)

    def on_connected(self):
        ...

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

    def __init__(self, server_address: tuple[str, int], **kwargs) -> None:
        super().__init__(server_address, self.Handler, **kwargs)

    def on_start(self):
        print(f"\nServer started at {TIME()}")

    def on_new_client(self, client):
        print(f"New Client {client.client_address[0]} Connected")

    def on_client_left(self, client):
        print(f"Client {client.client_address[0]} left")

    def on_accept(self, sock, addr):
        print(f"Client {addr} Accepted")
