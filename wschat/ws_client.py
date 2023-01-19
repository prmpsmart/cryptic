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
    instance: "Client" = None
    URI = ""

    def __init__(self):
        super().__init__()

        assert not Client.instance

        Client.instance = self

        self.actions: dict[str, Action] = {}
        self.signin_args = ()
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

    @classmethod
    def get_client(cls):
        if not cls.instance:
            cls.instance = cls()
        return cls.instance

    def start_client(self, threaded: bool = True):
        if self.started:
            return

        try:
            self.connect(url=self.URI)
            self.start(threaded)

        except ConnectionRefusedError:
            ...

    def on_message(self) -> Json:
        data = self.data

        try:
            _json = Json.from_str(data)
            action = self.actions.get(_json.action.lower())
            if action:
                action.trigger(_json)

        except json.JSONDecodeError as jde:
            print(f"Message Error, {data}")

    def send_json(self, data: Json) -> Json:
        _json = data.to_str()
        return self.send_message(_json)

    def send_action(self, action: str, **kwargs):
        json = Json(action=action, **kwargs)
        self.send_json(json)

    receive_action = add_receiver