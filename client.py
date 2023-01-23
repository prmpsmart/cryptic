from wschat.ws_client import *
from wschat.ws_commons import *
from commons import *
import os


class Chat:
    def __init__(self, cc: "Recipient", json: Json):
        self.cc = cc
        self.json = json
        self.seen = False
        self.sent = False

        # Json keys for Recipient
        #   recipient
        #   sender
        #   text
        #   time

    @property
    def isMe(self):
        return self.cc.id == self.json.sender

    def __getattr__(self, attr: str):
        if attr in self.__dict__:
            return self.__dict__.get(attr)
        else:
            return self.json[attr]


class Recipient:
    def __init__(self, id: str, avatar: str = "") -> None:
        self.id = id
        self.avatar = avatar
        self.invalid = False
        self.chats: list[Chat] = []

    @property
    def last_chat(self):
        if self.chats:
            return self.chats[-1]

    @property
    def unreads(self):
        uns = filter(lambda k: k.recipient == self.id and not k.seen, self.chats)
        return len(list(uns))

    def add_chat(self, json: Json):
        self.chats.append(Chat(self, json))


class CrypticClientUser(CrypticUser):
    def __init__(self, *args) -> None:
        super().__init__(*args)

        self.cryptics: list[Recipient] = []


class CrypticClient(Client):
    URI = "ws://localhost:8000"

    def on_connected(self):
        print("Connected to Server")

        if user := CrypticData.user():
            if not user.signed_in:
                self.get_client().signin(user.id, user.key)

    def signin(self, id: str, key: str):
        self.signed_in = False
        self.send_action(action="signin", id=id, key=key)
        self.signin_args = id, key
        self.receive_action("signin", self.signin_response)

    def signin_response(self, json: Json):
        if "success" in json.response.lower() and self.signin_args:
            data = dict(
                id=json.id,
                key=json.key,
                avatar=json.avatar,
            )
            self.signed_in = True

            if user := CrypticData.user():
                user.__dict__.update(data)

            else:
                user = CrypticClientUser(**data)
                CrypticData.DATA = user

            CrypticData.save()

    def signup(self, id: str, key: int):
        self.send_action(action="signup", id=id, key=key)

    def edit_profile(self, **kwargs):
        self.send_action("edit_profile", **kwargs)


class CrypticData(Data):
    DB_FILE = os.path.join(os.path.dirname(__file__), "cryptic.dump")

    @classmethod
    def user(cls) -> CrypticClientUser:
        return cls.data()
