from wschat.client import *

class AmeboUserClient(PRMP_WebSocketClient):
    instance: "AmeboUserClient" = None

    def __init__(self):
        super().__init__()

        assert not AmeboUserClient.instance

        AmeboUserClient.instance = self

        self.actions: dict[str, Action] = {}
        self.signin_args = ()

    def add_receiver(self, action: str, receiver: R):
        if action not in self.actions:
            self.actions[action] = Action(action)

        action: Action
        action = self.actions[action]
        action.add_receiver(receiver)

    def remove_receiver(self, action: str, receiver: R):
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
            self.connect(url=URI)
            self.start(threaded)
        except ConnectionRefusedError:
            ...

    def on_connected(self):
        if user := AmeboClientData.user():
            print(user)
            if not user.status:
                AmeboUserClient.get_client().signin(user.unique_id, user.password)

    def on_message(self) -> Json:
        data = self.data

        try:
            _json = Json.from_str(data)
            action = self.actions.get(_json.action.lower())
            if action:
                action.trigger(_json)

        except json.JSONDecodeError as jde:
            print(f"Message Error, {data}")

    def on_closed(self):
        if user := AmeboClientData.user():
            user.status = False
            user.last_seen = TIME()

    def send_json(self, data: Json) -> Json:
        _json = data.to_str()
        return self.send_message(_json)

    def send_action(self, action: str, **kwargs):
        json = Json(action=action, **kwargs)
        self.send_json(json)

    def signin(self, unique_id: str, password: int):
        self.send_action(action="signin", unique_id=unique_id, password=password)
        self.signin_args = unique_id, password
        self.add_receiver("signin", self.signin_response)

    def signin_response(self, json: Json):
        if json.response == 200 and self.signin_args:
            data = dict(
                id=json.id,
                created_at=json.created_at,
                display_name=json.display_name,
                description=json.description,
                avatar=json.avatar,
                unique_id=json.unique_id,
                password=json.password,
                status=json.status,
            )
            if user := AmeboClientData.user():
                user.__dict__.update(data)
            else:
                user = AmeboUser(**data)
                AmeboClientData.USER = user
            AmeboClientData.save()

    def signup(self, unique_id: str, password: int):
        self.send_action(action="signup", unique_id=unique_id, password=password)

    def edit_user_profile_info(self, **kwargs):
        self.send_action("edit_user_profile_info", **kwargs)

if __name__ == "__main__":
    a = AmeboUserClient()
    s = a.start_client()
    c = 0

    def close_sig_handler(signal: signal.Signals, frame):
        global c
        # os.system(f'{os.sys.executable} {os.sys.argv[0]}')
        a.send_json(Json(action="signin"))
        c += 1

        if c == 5:
            a.send_close(reason="Test")
            a.shutdown()
            exit()

    signal.signal(signal.SIGINT, close_sig_handler)

    while 1:
        ...
