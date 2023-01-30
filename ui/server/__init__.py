from ..ui_commons import *
from .qss import CRYPTIC_QSS
from . import resources
from server import *


class ThemeDialog(Dialog):
    def __init__(self, home, *args, **kwargs):
        super().__init__(*args, **kwargs)

        lay = self.windowLayout()
        theme = ThemeBox(home)
        lay.addWidget(theme)


IP_PORT = tuple[str, int]


class UserItem(VFrame):
    def __init__(self, ip_port: IP_PORT):
        super().__init__()
        addShadow(self)

        self.ip_port: IP_PORT = ip_port
        self.id: str = None

        lay = self.layout()

        hlay = QHBoxLayout()
        lay.addLayout(hlay)

        ip_lay = QHBoxLayout()
        hlay.addLayout(ip_lay)
        ip_lay.addWidget(Label("IP Address:", objectName="label"))

        self.ip_address = Label(ip_port[0])
        ip_lay.addWidget(self.ip_address)

        hlay.addStretch()

        port_lay = QHBoxLayout()
        hlay.addLayout(port_lay)
        port_lay.addWidget(Label("Port:", objectName="label"))

        self.port = Label(str(ip_port[1]))
        port_lay.addWidget(self.port)

        hlay.addStretch()

        id_lay = QHBoxLayout()
        hlay.addLayout(id_lay)
        id_lay.addWidget(Label("ID:", objectName="label"))

        self.id_lbl = Label()
        id_lay.addWidget(self.id_lbl)

        hlay.addStretch()

        for l in (ip_lay, port_lay, id_lay):
            l.setSpacing(2)

    def setID(self, id: str):
        self.id = id
        self.id_lbl.setText(id)


class Users(Scrollable):
    def __init__(self):
        super().__init__(VFrame, widgetKwargs=dict(objectName="users_list"))
        self.users: dict[tuple[str, int], UserItem] = {}
        self.spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

    def add_user(self, ip_port: IP_PORT):
        if ip_port not in self.users:
            lay = self.widgetLayout()
            lay.removeItem(self.spacer)

            item = UserItem(ip_port)
            lay.addWidget(item)

            lay.addItem(self.spacer)
            self.users[ip_port] = item

    def remove_user(self, ip_port: IP_PORT):
        if ip_port in self.users:
            lay = self.widgetLayout()

            item = self.users[ip_port]
            lay.removeWidget(item)
            item.deleteLater()

            self.widget().update()
            self.update()

            del self.users[ip_port]

    def update_item(self, ip_port: IP_PORT, id: str):
        if ip_port in self.users:
            item = self.users[ip_port]
            item.setID(id)


class UiHandler(CrypticHandler):
    def signin_handler(self, json: Json):
        response = super().signin_handler(json)
        if self.user:
            CrypticServerHome.instance.on_new_signin.emit(self)

        return response


class UiServer(Server):
    Handler = UiHandler

    def on_close(self):
        super().on_close()
        CrypticServerHome.instance.update_server_button(False)

    def on_new_client(self, client: UiHandler):
        super().on_new_client(client)
        CrypticServerHome.instance.on_new_client.emit(client)

    def on_client_left(self, client: UiHandler):
        super().on_client_left(client)
        CrypticServerHome.instance.on_client_left.emit(client)


class CrypticServerHome(VFrame):
    on_new_client = Signal(UiHandler)
    on_new_signin = Signal(UiHandler)
    on_client_left = Signal(UiHandler)
    instance: "CrypticServerHome" = None

    def __init__(self, app: QApplication, server_address: tuple[str, int], **kwargs):
        super().__init__(**kwargs)

        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        if not CrypticServerHome.instance:
            CrypticServerHome.instance = self

        self.app = app
        self.server_address = server_address
        self.server: UiServer = None

        self.setWindowTitle("Cryptic Server")
        self.setMinimumHeight(300)

        lay = self.layout()
        m = 5
        lay.setContentsMargins(m, m, m, m)
        lay.setSpacing(m)

        hlay = QHBoxLayout()
        lay.addLayout(hlay)

        self.toggle_server_button = QPushButton()
        self.toggle_server_button.setCheckable(True)
        self.toggle_server_button.setIconSize(QSize(20, 20))
        self.toggle_server_button.setCursor(Qt.PointingHandCursor)
        self.toggle_server_button.toggled.connect(self.toggle_server)
        hlay.addWidget(self.toggle_server_button)

        hlay.addStretch()

        self.total_connected = IconTextButton(
            "Connected: 0",
            ":access-point",
            objectName="connected",
            iconColor=QColor(app.theme.six),
            iconSize=20,
        )
        self.total_connected.setAttribute(Qt.WA_TransparentForMouseEvents)
        hlay.addWidget(self.total_connected)

        self.total_logged_in = IconTextButton(
            "Logged_In: 0",
            ":login",
            objectName="logged_in",
            iconColor=QColor(app.theme.six),
            iconSize=20,
        )
        hlay.addWidget(self.total_logged_in)
        self.total_logged_in.setAttribute(Qt.WA_TransparentForMouseEvents)

        theme = QPushButton("Theme")
        hlay.addWidget(theme)
        theme.clicked.connect(self.toggle_theme_dialog)

        self.users_list = Users()
        lay.addWidget(self.users_list)

        self.app.theme_dialog = ThemeDialog(self, parent=self)

        self.on_new_client.connect(self.on_new_client_slot)
        self.on_client_left.connect(self.on_client_left_slot)
        self.on_new_signin.connect(self.on_new_signin_slot)

        self.update_server_button(False)

    def update_theme(self):
        icon = QSvgIcon(
            ":cloud" if self.toggle_server_button.isChecked() else ":cloud-off",
            color=self.app.theme.one,
        )
        self.toggle_server_button.setIcon(icon)

        icon = QSvgIcon(":access-point", color=self.app.theme.six)
        self.total_connected.setIcon(icon)

        icon = QSvgIcon(":login", color=self.app.theme.six)
        self.total_logged_in.setIcon(icon)

    def update_server_button(self, toggle: bool):
        self.toggle_server_button.setText(
            ("Start" if not toggle else "Stop") + " Server"
        )
        icon = QSvgIcon(
            ":cloud" if not toggle else ":cloud-off", color=self.app.theme.one
        )
        self.toggle_server_button.setIcon(icon)

    def toggle_server(self, toggle: bool = False):
        if toggle:
            if not self.server:
                self.server = UiServer(self.server_address, log_level=logging.INFO)
            self.server.serve_forever()

        else:
            if self.server.started:
                self.server.close()
                self.server = None

        self.update_server_button(toggle)

    def on_new_signin_slot(self, client: UiHandler):
        self.users_list.update_item(client.client_address, client.user.id)

    def on_new_client_slot(self, client: UiHandler):
        self.users_list.add_user(client.client_address)

    def on_client_left_slot(self, client: UiHandler):
        self.users_list.remove_user(client.client_address)

    def toggle_theme_dialog(self):
        MOVE_DIALOG_TO_CURSOR(self.app.theme_dialog)
        self.app.theme_dialog.show()

    def showEvent(self, event: QShowEvent) -> None:
        if self.server and self.server.started:
            return

        self.move(20, 10)
        QTimer.singleShot(1000, lambda: self.toggle_server_button.toggle())
        # for _ in range(5):
        # self.add_user(("127.0.0.1", 8000 + _))

    def closeEvent(self, event: QCloseEvent) -> None:
        self.toggle_server(False)
