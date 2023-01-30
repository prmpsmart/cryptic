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
        if attr in self.__dict__.keys():
            return self.__dict__.get(attr)
        else:
            return self.json[attr]


class Recipient:
    def __init__(self, id: str, avatar: str = "") -> None:
        self.id = id
        self.avatar = avatar
        self.invalid = False
        self.chats: list[Chat] = []

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.id})"

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
        self.recipients: dict[str, Recipient] = {}


class CrypticClientData(Data):
    DB_FILE = os.path.join(os.path.dirname(__file__), "cryptic_client.dump")
    USER: CrypticClientUser = None
    CLIENT: "CrypticClient" = None

    @classmethod
    def user(cls) -> CrypticClientUser:
        if not cls.USER:
            cls.load_data()

        return cls.USER

    @classmethod
    def uri(cls) -> str:
        if not cls.CLIENT:
            return

        if not cls.CLIENT.URI:
            cls.load_data()

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
        self.add_receiver("add_recipient", self.add_recipient_response)
        self.signin_args = ()
        self.signed_in = False

    def __bool__(self):
        return True

    def on_connected(self):
        super().on_connected()
        if user := self.DATA.user():
            self.signin(user.id, user.key)

    def close_socket(self):
        self.signed_in = False
        super().close_socket()

    def send_action(self, action: str, **kwargs):
        json = Json(action=action, **kwargs)
        return self.send_json(json)

    def send_user_action(self, action: str, **kwargs):
        user = self.DATA.user()
        kwargs["id"] = user.id
        return self.send_action(action, **kwargs)

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
                user = self.DATA.user()

                if not isinstance(user, CrypticClientUser):
                    user = CrypticClientUser(
                        self.signin_args[0], key=self.signin_args[1], avatar=json.avatar
                    )
                    self.DATA.USER = user

                else:
                    if json.avatar != user.avatar:
                        user.avatar = json.avatar

                self.signin_args = ()
                self.DATA.save_data()

    def signup(self, id: str, key: int):
        self.send_action(action="signup", id=id, key=key)

    def edit_profile(self, **kwargs):
        self.send_user_action("edit_profile", **kwargs)

    def text(self, **kwargs):
        self.send_user_action("text", **kwargs)

    def add_recipient(self, id: str):
        self.send_user_action("add_recipient", recipient=id)

    def add_recipient_response(self, json: Json):
        if (user := self.DATA.user()) and (json.response == ADDED):
            recipient = Recipient(json.id, json.avatar)
            user.recipients[json.id] = recipient
            self.DATA.save_data()


CrypticClientData.CLIENT = CrypticClient
