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
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.cryptics: list[Recipient] = []


class CrypticClientData(Data):
    DB_FILE = os.path.join(os.path.dirname(__file__), "cryptic_client.dump")
    USER: CrypticClientUser = None
    CLIENT: "CrypticClient" = None

    @classmethod
    def user(cls) -> CrypticClientUser:
        if cls.USER:
            return cls.USER
        data = cls.data()
        if data:
            return data.user

    @classmethod
    def uri(cls) -> str:
        if not cls.CLIENT:
            return

        if cls.CLIENT.URI:
            return cls.CLIENT.URI

        data = cls.data()
        if data:
            cls.CLIENT.URI = data.uri
            return cls.CLIENT.URI

    @classmethod
    def on_save(cls):
        ...

    @classmethod
    def on_load(cls):
        ...

    @classmethod
    def save_data(cls):
        cls.DATA = Json(user=cls.USER)
        if cls.CLIENT:
            cls.DATA.uri = cls.CLIENT.URI
        cls.on_save()
        cls.save()

    @classmethod
    def load_data(cls) -> str:
        if data := cls.data():
            cls.USER = data.user
            if cls.CLIENT:
                cls.CLIENT.URI = data.uri
            cls.on_load()


class CrypticClient(Client):
    DATA = CrypticClientData

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_receiver("signin", self.signin_response)
        self.signin_args = ()

    def on_connected(self):
        super().on_connected()

        if user := self.DATA.user():
            if not self.signed_in:
                self.signin(user.id, user.key)

    def falsify_variables(self):
        super().falsify_variables()
        self.signed_in = False

    def send_action(self, action: str, **kwargs):
        json = Json(action=action, **kwargs)
        return self.send_json(json)

    def signin(self, id: str, key: str):
        if self.signin_args:
            return

        self.signed_in = False
        self.signin_args = id, key
        self.send_action(action="signin", id=id, key=key)

    def signin_response(self, json: Json):
        if self.signin_args:
            if json.response == LOGGED_IN:

                self.signed_in = True
                if user := self.DATA.user() and json.avatar:
                    user.avatar = json.avatar

                else:
                    user = CrypticClientUser(
                        self.signin_args[0], key=self.signin_args[1], avatar=json.avatar
                    )
                    self.DATA.USER = user

                self.signin_args = ()
                self.DATA.save_data()

    def signup(self, id: str, key: int):
        self.send_action(action="signup", id=id, key=key)

    def edit_profile(self, **kwargs):
        self.send_action("edit_profile", **kwargs)

    def text(self, **kwargs):
        self.send_action("text", **kwargs)


CrypticClientData.CLIENT = CrypticClient
