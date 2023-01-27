from wschat.ws_server import *
from commons import *
import datetime

INVALID = "Invalid inputs"


class CrypticServerUser(CrypticUser):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.jsons: list[Json] = []

    def add_json(self, json: Json):
        self.jsons.append(json)


class Cryptic:
    USERS: dict[str, CrypticServerUser] = {}

    @classmethod
    def create_cryptic(cls, id: str, *args, **kwargs) -> CrypticServerUser:
        if id not in cls.USERS:
            user = CrypticServerUser(id, *args, **kwargs)
            cls.USERS[id] = user
            return user


class CrypticHandler(ClientHandler):
    def __init__(self, *args) -> None:
        self.user: CrypticServerUser = None
        super().__init__(*args)

    def on_message(self):
        data = self.data

        try:
            json = Json.from_str(data)
        except Json.JSONDecodeError as jde:
            LOGGER.debug(f" Message Error, {data}")

        if json and json.action:
            action = json.action.lower()
            action_handler = getattr(self, f"{action}_handler", None)

            if action_handler:
                if action not in ["signin", "signup"]:
                    response = "Invalid ID"
                    if json.id == self.user.id:
                        response = action_handler(json)
                else:
                    response = action_handler(json)

                response_json = Json(action=action)

                if isinstance(response, Json):
                    response_json.update(response)
                else:
                    response_json.response = response

                self.send_json(response_json)

                if action == "signin":
                    self.send_user_jsons()

            else:
                unsupported = f" Action {action} is not supported."
                LOGGER.debug(unsupported)

                if not self.send_json(Json(response=unsupported)):
                    LOGGER.debug(" Send : Client disconnected.")
                    self.keep_alive = False

        elif json == False:
            if not self.send_json(Json(response=f"Invalid Data")):
                LOGGER.debug(" Send : Client disconnected.")
                self.keep_alive = False

        elif json == None:
            LOGGER.debug(" Recv : Client disconnected.")
            self.keep_alive = False

    # action handlers

    def signup_handler(self, json: Json):
        id = json.id
        key = json.key

        response = INVALID

        if id and key:
            if id not in Cryptic.USERS:
                Cryptic.create_cryptic(
                    id=id,
                    key=key,
                    avatar=json.avatar,
                )
                response = "Signed Up"
            else:
                response = "ID isn't available"

        return response

    def signin_handler(self, json: Json):
        id: str = json.id
        key: str = json.key

        response = INVALID

        if not (id in self.server.clients_map or self.user):
            if id and key:
                user = Cryptic.USERS.get(id)

                if user and user.key == key:
                    self.user = user
                    response = "Logged In"
                    self.server.clients_map[id] = self

        return response

    def send_user_jsons(self):
        if not self.user:
            return

        jsons = list(self.user.jsons)
        for index, json in enumerate(jsons):
            if self.send_json(json):
                del self.user.jsons[index]

    def edit_profile_handler(self, json: Json):
        response = INVALID
        return response

    def text_handler(self, json: Json):
        recipient = json.recipient

        user = Cryptic.USERS.get(recipient)
        if user:
            client = self.server.clients_map.get(recipient)
            if client:
                client.receive_json(json)
            else:
                user.add_json(json)

        return Json(recipient=json.recipient, sender=json.sender, sent=True)

    def receive_json(self, json: Json):
        try:
            if not self.send_json(json):
                self.user.add_json(json)
        except Exception as e:
            print(e, "receive_json")


class CrypticServer(Server):
    Handler = CrypticHandler
