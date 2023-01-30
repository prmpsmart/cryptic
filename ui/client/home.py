from .side_menu import *
from .room import *


class CrypticHome(HFrame):
    signinSignal = Signal(Json)
    signupSignal = Signal(Json)
    edit_profileSignal = Signal(Json)
    add_recipientSignal = Signal(Json)
    textSignal = Signal(Json)

    def __init__(self, app: QApplication, **kwargs):
        super().__init__(**kwargs)

        self.app = app
        self._user: CrypticClientUser = None
        self.client = CrypticUIClient(log_level=logging.DEBUG)

        for receiver in [
            self.signin,
            self.signup,
            self.text,
            self.edit_profile,
            self.add_recipient,
        ]:
            self.client.add_receiver(receiver.__name__, receiver)

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

    @property
    def user(self) -> CrypticClientUser:
        if not self._user:
            self._user = CrypticUIClientData.user()
        return self._user

    def signup(self, json: Json):
        self.signupSignal.emit(json)

    def signin(self, json: Json):
        self.signinSignal.emit(json)

    def text(self, json: Json):
        self.textSignal.emit(json)

    def edit_profile(self, json: Json):
        self.edit_profileSignal.emit(json)

    def add_recipient(self, json: Json):
        self.add_recipientSignal.emit(json)

    def recipient_item_selected(self, item: RecipientItem):
        self.room_view.recipient_item_selected(item)

    def start_client(self) -> CrypticUIClient:
        if CrypticUIClient.URI and not self.client.started:
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
        CrypticUIClientData.save_data()

    def showEvent(self, event: QShowEvent) -> None:
        self.move(550, 10)
