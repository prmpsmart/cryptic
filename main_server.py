from server import Cryptic, CrypticServer

server_address = ("", 8000)
server = CrypticServer(server_address)

cryptics = [
    ("mimi", "prmp"),
    ("mimi", "prmp"),
    ("mimi", "prmp"),
]

for cryptic in cryptics:
    Cryptic.create_cryptic(*cryptic)

server.serve_forever(0)
