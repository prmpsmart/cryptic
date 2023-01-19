from client import CrypticClient, Json
import signal

client = CrypticClient()
client.URI = "ws://localhost:8000"

client.start_client()

c = 1
STOP = 3


def receiver(json: Json):
    print(json)


def action():
    action = "signin"
    action = "signin"
    action = "signup"

    client.add_receiver(action, receiver)
    json = Json(action=action, id="mimI", key="prmp")
    client.send_json(json)


def close_sig_handler(signal: signal.Signals, frame):
    global c
    c += 1
    # os.system(f'{os.sys.executable} {os.sys.argv[0]}')

    action()

    print(f"Exiting in {STOP}: {c}", end="\r")

    if c > STOP:
        client.send_close(reason="Test")
        client.shutdown()
        exit()


signal.signal(signal.SIGINT, close_sig_handler)

while 1:
    ...
