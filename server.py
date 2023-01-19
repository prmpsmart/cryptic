from wschat.ws_server import *
from commons import *
import datetime


class CrypticServerUser(CrypticUser):
    def __init__(self, *args) -> None:
        super().__init__(*args)

        self.jsons: list[Json] = []


class Cryptic:
    users: dict[str, CrypticServerUser] = {}

    @classmethod
    def create_cryptic(cls, id: str, *args, **kwargs) -> CrypticUser:
        if id not in cls.users:
            user = CrypticUser(id, *args, **kwargs)
            cls.users[id] = user
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
            print(f"Message Error, {data}")

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
                response_json.response = response
                self.send_json(response_json)

            else:
                unsupported = f"Action {action} is not supported."
                print(unsupported)

                if not self.send_json(Json(response=unsupported)):
                    print("Send : Client disconnected.")
                    self.keep_alive = False

        elif json == False:
            if not self.send_json(Json(response=f"Invalid Data")):
                print("Send : Client disconnected.")
                self.keep_alive = False

        elif json == None:
            print("Recv : Client disconnected.")
            self.keep_alive = False

    # action handlers

    def signup_handler(self, json: Json):
        id = json.id
        key = json.key

        response = "Invalid inputs."

        if id and key:
            if id not in Cryptic.users:
                user = Cryptic.create_cryptic(
                    id=id,
                    key=key,
                    avatar=json.avatar,
                )
                self.user = user
                response = "Created Successfully."
            else:
                response = "ID isn't available."

        return response

    def signin_handler(self, json: Json):
        id: str = json.id
        key: str = json.key

        response = "Invalid inputs."

        if not self.user:
            if id and key:
                user = Cryptic.users.get(id)

                if user and user.key == key:
                    self.user = user
                    response = "Logged in Successfully."

        return response

    def send_user_jsons(self):
        jsons = list(self.user.jsons)
        for index, json in enumerate(jsons):
            if self.send_json(json):
                del self.user.jsons[index]

    def edit_profile_handler(self, json: Json):
        response = "Invalid inputs."

        return response

    def text_handler(self, json: Json):
        response = "Invalid inputs."

        return response


class CrypticServer(Server):
    Handler = CrypticHandler

    def on_start(self):
        print(f"\nServer started at {datetime.datetime.now()}\n")

    def on_new_client(self, client):
        print(f"New Client {client.client_address[0]} Connected")
        ...

    def on_client_left(self, client):
        print(f"Client {client.client_address[0]} left\n")
        ...

    def on_accept(self, sock, addr):
        # print(f"Client {addr} Accepted")
        ...
