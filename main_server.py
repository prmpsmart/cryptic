from server import *

server_address = ("", 8000)
server = CrypticServer(server_address, log_level=logging.INFO)

cryptics = [
    ("mimi", "prmp"),
    ("mirac", "prmp"),
    ("prmp", "prmp"),
]

for cryptic in cryptics:
    Cryptic.create_cryptic(*cryptic)

server.serve_forever(0)
