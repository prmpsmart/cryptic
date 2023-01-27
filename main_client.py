from client import *
import signal

client = CrypticClient(log_level=logging.INFO)
client.URI = "ws://localhost:8000"

client.start_client()


def receiver(json: Json):
    print(json)


def action():
    action = "signup"
    client.add_receiver(action, receiver)
    json = Json(action=action, id="mimi", key="prmp")
    # client.send_json(json)

    action = "signin"
    client.add_receiver(action, receiver)
    json = Json(action=action, id="mimi", key="prmp")
    client.send_json(json)

    print(json)


client.on_connected = action


def close_sig_handler(signal: signal.Signals, frame):
    global c
    c += 1
    # os.system(f'{os.sys.executable} {os.sys.argv[0]}')

    print(f"Exiting in {STOP}: {c}", end="\r")

    if c > STOP:
        client.send_close(reason="Test")
        client.shutdown()
        exit()
    else:
        action()


c = 1
STOP = 2

signal.signal(signal.SIGINT, close_sig_handler)

while 1:
    ...
