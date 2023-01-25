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


class UserItem(VFrame):
    def __init__(self, ip: str, port: int):
        super().__init__()
        addShadow(self)

        self.ip: str = ip
        self.port: int = port
        self.id: str = None

        lay = self.layout()

        hlay = QHBoxLayout()
        lay.addLayout(hlay)

        ip_lay = QHBoxLayout()
        hlay.addLayout(ip_lay)
        ip_lay.addWidget(Label("IP Address:", objectName="label"))
        self.ip_address = Label(ip)
        ip_lay.addWidget(self.ip_address)

        hlay.addStretch()

        port_lay = QHBoxLayout()
        hlay.addLayout(port_lay)
        port_lay.addWidget(Label("Port:", objectName="label"))
        self.port = Label(str(port))
        port_lay.addWidget(self.port)

        hlay.addStretch()

        id_lay = QHBoxLayout()
        hlay.addLayout(id_lay)
        id_lay.addWidget(Label("ID:", objectName="label"))
        self.id = Label()
        id_lay.addWidget(self.id)

        hlay.addStretch()

        for l in (ip_lay, port_lay, id_lay):
            l.setSpacing(2)

    def setID(self, id: str):
        self.id = id
        self.id.setText(id)


class Users(Scrollable):
    def __init__(self):
        super().__init__(VFrame, widgetKwargs=dict(objectName="users_list"))
        self.users: dict[tuple[str, int], UserItem] = {}
        self.spacer = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)

    def add_user(self, ip: str, port: int):
        ip_port = (ip, port)
        if ip_port not in self.users:
            lay = self.widgetLayout()
            lay.removeItem(self.spacer)

            item = UserItem(ip, port)
            lay.addWidget(item, 1, Qt.AlignTop)

            lay.addItem(self.spacer)

            self.users[ip_port] = item

    def remove_user(self, ip: str, port: int):
        ip_port = (ip, port)
        if ip_port in self.users:
            lay = self.widgetLayout()
            item = self.users[ip_port]
            lay.removeWidget(item)
            del self.users[ip_port]

    def update(self, ip: str, port: int, id: str):
        ip_port = (ip, port)
        if ip_port in self.users:
            item = self.users[ip_port]
            item.setID(id)

    # def showEvent(self, event: QShowEvent) -> None:
    #     for _ in range(5):
    #         self.add_user("127.0.0.1", 8000 + _)


class UiHandler(CrypticHandler):
    def signin_handler(self, json: Json):
        ...


class UiServer(Server):
    Handler = UiHandler

    def on_start(self):
        print('Started')

    def on_new_client(self, client: UiHandler):
        CrypticServerHome.instance.on_new_client.emit(client)
        print(f"New Client {client.client_address[0]} Connected")
        ...

    def on_client_left(self, client: UiHandler):
        CrypticServerHome.instance.on_client_left.emit(client)
        print(f"Client {client.client_address[0]} left\n")
        ...

    def on_accept(self, sock, addr):
        CrypticServerHome.instance.on_accept.emit(addr)
        print(f"Client {addr} Accepted")
        ...


class CrypticServerHome(VFrame):
    on_new_client = Signal(UiHandler)
    on_client_left = Signal(UiHandler)
    on_accept = Signal(tuple)
    instance: 'CrypticServerHome' = None

    def __init__(self, app: QApplication, server_address:tuple[str, int], **kwargs):
        super().__init__(**kwargs)

        if not CrypticServerHome.instance:
            CrypticServerHome.instance = self

        self.app = app
        self.theme = GreyTheme

        self.destroyed.connect(self.quit)

        self.setWindowTitle("Cryptic Server")
        self.setMinimumHeight(600)

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
            "Connected Users",
            ":access-point",
            objectName="connected",
            iconColor=QColor(self.theme.six),
            iconSize=20,
        )
        self.total_connected.setAttribute(Qt.WA_TransparentForMouseEvents)
        hlay.addWidget(self.total_connected)

        self.total_logged_in = IconTextButton(
            "Logged In Users",
            ":login",
            objectName="logged_in",
            iconColor=QColor(self.theme.six),
            iconSize=20,
        )
        hlay.addWidget(self.total_logged_in)
        self.total_logged_in.setAttribute(Qt.WA_TransparentForMouseEvents)

        theme = QPushButton("Theme")
        hlay.addWidget(theme)
        theme.clicked.connect(self.toggle_theme_dialog)

        self.users_list = Users()
        lay.addWidget(self.users_list)

        self.theme_dialog = ThemeDialog(self, parent=self)

        self.on_new_client.connect(self.on_new_client_slot)
        self.on_client_left.connect(self.on_client_left_slot)
        self.on_accept.connect(self.on_accept_slot)

        self.server = UiServer(server_address)

        self.toggle_server(d=False)

    def update_theme(self):
        icon = QSvgIcon(
            ":cloud" if self.toggle_server_button.isChecked() else ":cloud-off",
            color=self.theme.one,
        )
        self.toggle_server_button.setIcon(icon)

        icon = QSvgIcon(":access-point", color=self.theme.six)
        self.total_connected.setIcon(icon)

        icon = QSvgIcon(":login", color=self.theme.six)
        self.total_logged_in.setIcon(icon)

    def toggle_server(self, toggle: bool = False, d: bool = True):
        self.toggle_server_button.setText(("Start" if toggle else "Stop") + " Server")
        icon = QSvgIcon(":cloud" if toggle else ":cloud-off", color=self.theme.one)
        self.toggle_server_button.setIcon(icon)

        if not d:
            return

        if toggle:
            self.server.serve_forever()
        else:
            self.server._shutdown_gracefully()

    def on_new_client_slot(self, client: UiHandler):
        ...

    def on_client_left_slot(self, client: UiHandler):
        ...

    def on_accept_slot(self, addr: tuple[str, str]):
        ...

    def toggle_theme_dialog(self):
        MOVE_DIALOG_TO_CURSOR(self.theme_dialog)
        self.theme_dialog.show()

    def quit(self):
        self.server._shutdown_gracefully()
