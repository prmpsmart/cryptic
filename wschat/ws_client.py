import threading
from .ws_commons import *

__all__ = ["Client", "Action", "Json", "Data"]


class Action:
    def __init__(self, action: str):
        self.action = action
        self.receivers: list[Json_Receiver] = []

    def trigger(self, json: Json):
        for receiver in self.receivers:
            receiver(json)

    def add_receiver(self, receiver: Json_Receiver):
        if receiver and receiver not in self.receivers:
            self.receivers.append(receiver)

    def remove_receiver(self, receiver: Json_Receiver):
        if receiver and receiver in self.receivers:
            self.receivers.remove(receiver)

    def __eq__(self, action):
        if isinstance(action, Action):
            action = action.action
        return self.action == action

    @property
    def empty(self):
        return self.receivers == []


class Client(PRMP_WebSocketClient):
    URI = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.actions: dict[str, Action] = {}
        self.signed_in = False

    def add_receiver(self, action: str, receiver: Json_Receiver):
        if action not in self.actions:
            self.actions[action] = Action(action)

        action: Action = self.actions[action]
        action.add_receiver(receiver)

    def remove_receiver(self, action: str, receiver: Json_Receiver):
        if action in self.actions:
            action: Action = self.actions[action]
            action.remove_receiver(receiver)

    def start_client(self, threaded: bool = True):
        if self.started:
            return

        try:
            self.connect(url=self.URI)
            self.start(threaded)

        except ConnectionRefusedError:
            ...

    def thread_start_client(self, *args, **kwargs):
        threading.Thread(target=self.start_client, args=args, kwargs=kwargs).start()

    def on_message(self) -> Json:
        data = self.data

        try:
            _json = Json.from_str(data)
            action = self.actions.get(_json.action.lower())
            if action:
                action.trigger(_json)

        except json.JSONDecodeError as jde:
            LOGGER.debug(f" Message Error, {data}")

    def send_json(self, data: Json) -> Json:
        if self.connected:
            _json = data.to_str()
            return self.send_message(_json)

    def send_action(self, action: str, **kwargs):
        json = Json(action=action, **kwargs)
        return self.send_json(json)
