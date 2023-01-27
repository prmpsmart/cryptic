from .side_menu import *
from .room import *


class ActionHandler:
    signinSignal = Signal(bool)
    signupSignal = Signal(bool)
    textSignal = Signal(Json)
    edit_profileSignal = Signal(str)

    def __init__(self, home: "CrypticHome") -> None:
        for name in ["signin", "signup", "text", "edit_profile"]:
            receiver = getattr(self, name)
            home.client.add_receiver(name, receiver)
        self.home = home

    def signup(self, json: Json):
        QMessageBox.information(self, "Sign Up", json.response)
        self.signupSignal.emit(json.response == "Signed Up")

    def signin(self, json: Json):
        QMessageBox.information(self, "Sign In", json.response)
        self.signinSignal.emit(json.response == "Logged In")
        self.home.clientStatusSignal.emit()

    def text(self, json: Json):
        self.textSignal.emit(json)

    def edit_profile(self, json: Json):
        QMessageBox.information(self, "Profile Edit", json.response)
        self.edit_profileSignal.emit(json.response)


class CrypticHome(HFrame):

    clientStatusSignal = Signal()

    def __init__(self, app: QApplication, **kwargs):
        super().__init__(**kwargs)

        self.app = app
        self._user: CrypticClientUser = None
        self.client = CrypticUIClient(self.clientStatusSignal, log_level=logging.INFO)
        self.action_handler = ActionHandler(self)

        self.setWindowTitle("Cryptic")
        self.setMinimumHeight(700)

        lay = self.layout()
        m = 0
        lay.setContentsMargins(m, m, m, m)
        lay.setSpacing(5)

        self.side_menu = SideMenu(self)
        lay.addWidget(self.side_menu)

        self.recipients_view = RecipientsView(self)
        lay.addWidget(self.recipients_view)

        self.room_view = RoomView(self)
        lay.addWidget(self.room_view)

        self.setMinimumWidth(
            self.side_menu.minimumWidth()
            + self.recipients_view.minimumWidth()
            + self.room_view.minimumWidth()
            + lay.spacing() * 2
        )

    def recipient_item_selected(self, item: RecipientItem):
        self.room_view.recipient_item_selected(item)

    @property
    def user(self) -> CrypticClientUser:
        if not self._user:
            self._user = CrypticUIClientData.user()
        return self._user

    def start_client(self) -> CrypticUIClient:
        if CrypticUIClient.URI:
            try:
                self.client.thread_start_client()
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Connection Error",
                    f"Server connection error {e}, check the Server URI - {CrypticUIClient.URI}",
                )

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.client.started:
            self.client.close("Client UI Closing")

    def showEvent(self, event: QShowEvent) -> None:
        self.move(550, 10)
        if not self.client.started:
            QTimer.singleShot(500, self.start_client)
            ...
