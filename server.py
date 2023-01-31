from wschat.ws_server import *
from commons import *


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
                response = ""
                if action not in ["signin", "signup"]:
                    if json.id == self.user.id:
                        response = action_handler(json)
                else:
                    response = action_handler(json)

                response = response or INVALID

                response_json = Json(action=action)

                if isinstance(response, Json):
                    response_json.update(response)
                else:
                    response_json.response = response

                print(response_json)

                self.send_json(response_json)

                if action == "signin" and response_json.response == LOGGED_IN:
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

    def send_user_jsons(self):
        if not self.user:
            return

        jsons = list(self.user.jsons)
        for index, json in enumerate(jsons):
            if self.send_json(json):
                del self.user.jsons[index]

    def receive_json(self, json: Json):
        try:
            if not self.send_json(json):
                self.user.add_json(json)
        except Exception as e:
            LOGGER.debug(f" {e} : receive_json")

    # action handlers

    def signup_handler(self, json: Json):
        id = json.id
        key = json.key

        if id and key:
            if id not in Cryptic.USERS:
                Cryptic.create_cryptic(
                    id=id,
                    key=key,
                    avatar=json.avatar,
                )
                response = SIGNED_UP
            else:
                response = ID_UNAVAILABLE

            return response

    def signin_handler(self, json: Json):
        id: str = json.id
        key: str = json.key

        if self.user:
            if id != self.user.id:
                self.user = None
            else:
                return LOGGED_IN

        if not (id in self.server.clients_map and self.user):
            if id and key:
                user = Cryptic.USERS.get(id)

                if user and user.key == key:
                    self.user = user
                    self.server.clients_map[id] = self
                    json = Json(id=id, avatar=user.avatar)
                    json.response = LOGGED_IN
                    return json

    def edit_profile_handler(self, json: Json):
        if not (self.user and json.id == self.user.id):
            return NOT_LOGGED_IN

    def text_handler(self, json: Json):
        if not (self.user and json.id == self.user.id):
            return NOT_LOGGED_IN

        recipient = json.recipient
        user = Cryptic.USERS.get(recipient)

        if user:
            client = self.server.clients_map.get(recipient)
            if client:
                client.receive_json(json)
            else:
                user.add_json(json)

            return Json(
                recipient=json.recipient,
                id=json.id,
                sent=True,
                time=json.time,
            )

    def validate_recipients_handler(self, json: Json):
        print(json)
        recipients = json.recipients
        validations: list[tuple[str, bool]] = []
        for recipient in recipients:
            validations.append((recipient, recipient in Cryptic.USERS))
        return validations

    def add_recipient_handler(self, json: Json):
        if not (self.user and json.id == self.user.id):
            return NOT_LOGGED_IN

        if recipient := Cryptic.USERS.get(json.recipient):
            recipient_json = Json(
                id=self.user.id, avatar=self.user.avatar, response=ADDED
            )
            if recipient_client := self.server.clients_map.get(recipient.id):
                recipient_client.send_json(recipient_json)
            else:
                recipient.add_json(recipient_json)

            return Json(id=recipient.id, avatar=recipient.avatar, response=ADDED)


class CrypticServer(Server):
    Handler = CrypticHandler
