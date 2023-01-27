from .commons import *


class Detail(VFrame):
    def __init__(self, title: str, holder: str = "", hide: bool = False):
        super().__init__()

        lay = self.layout()
        m = 5
        lay.setContentsMargins(m, m, m, m)

        self.title = LeftAlignLabel(text=title)
        lay.addWidget(self.title)

        hlay = QHBoxLayout()
        lay.addLayout(hlay)

        self.valueEdit = LineEdit(placeholder=holder)
        self.valueEdit.setDisabled(True)
        hlay.addWidget(self.valueEdit)

        self.edit_icon = QIcon(":edit")
        self.check_icon = QIcon(":check")

        self.action = Button(icon=self.edit_icon, iconSize=20)
        self.action.setCheckable(True)
        self.action.setToolTip("Edit")
        self.action.toggled.connect(self.toggle_action)
        hlay.addWidget(self.action)

        if hide:
            self.eye_icon = QIcon(":eye")
            self.eye_off_icon = QIcon(":eye-off")

            self.valueEdit.setEchoMode(QLineEdit.Password)

            self.eye = Button(icon=self.eye_icon, iconSize=20)
            self.eye.setCheckable(True)
            self.eye.setToolTip("Show")
            self.eye.toggled.connect(self.toggle_eye)
            hlay.insertWidget(1, self.eye)

    def setValue(self, value: str):
        self.valueEdit.setText(value)

    def value(self):
        return self.valueEdit.text()

    def toggle_action(self, toggle: bool):
        icon = self.check_icon if toggle else self.edit_icon
        tip = "Save" if toggle else "Edit"
        self.action.setIcon(icon)
        self.valueEdit.setEnabled(toggle)
        self.action.setToolTip(tip)

        if not toggle:
            attr = self.title.text().lower().replace(" :", "")

    def toggle_eye(self, toggle: bool):
        icon = self.eye_off_icon if toggle else self.eye_icon
        tip = "Hide" if toggle else "Show"
        echo = QLineEdit.Normal if toggle else QLineEdit.Password

        self.valueEdit.setEchoMode(echo)
        self.eye.setIcon(icon)
        self.valueEdit.setEnabled(toggle)
        self.eye.setToolTip(tip)


class SideMenu(Expandable, VFrame, Shadow):
    def __init__(self, home):
        VFrame.__init__(self)
        Expandable.__init__(self, max_width=250, min_width=50)
        Shadow.__init__(self)

        self.home = home
        self.client: CrypticUIClient = home.client

        home.clientStatusSignal.connect(self.update_status)

        lay = self.layout()
        m = 5
        lay.setContentsMargins(m, m, m, m)

        hlay = QHBoxLayout()
        lay.addLayout(hlay)

        color = "white"

        hlay.addStretch()

        self.status = AvatarButton(
            icon=":cloud-off", iconSize=40, mask=30, iconColor=color
        )
        self.status.clicked.connect(self.toggle)
        hlay.addWidget(self.status)
        addShadow(self.status)

        self.profile = Scrollable(VFrame, widgetKwargs=dict(objectName="profile_list"))
        self.profile.hide()
        profile_lay = self.profile.widgetLayout()
        m = 0
        profile_lay.setContentsMargins(m, m, m, m)
        lay.addWidget(self.profile)

        self.image = ImageLabel(default=QSvgPixmap(":user-2", color).toImage())
        profile_lay.addWidget(self.image)

        self.id = Detail(title="ID :", holder="ID of this client.")
        profile_lay.addWidget(self.id)

        self.key = Detail(title="Key :", holder="Key of this client.", hide=True)
        profile_lay.addWidget(self.key)

        hlay = QHBoxLayout()
        profile_lay.addLayout(hlay)

        self.sign = QCheckBox("Sign")
        hlay.addWidget(self.sign, 0, Qt.AlignTop)
        hlay.setContentsMargins(2, 2, 5, 2)

        hlay.addStretch()

        signin = TextButton(text="Sign In")
        addShadow(signin)
        signin.clicked.connect(self.signin)
        signin.hide()
        hlay.addWidget(signin)

        signup = TextButton(text="Sign Up")
        addShadow(signup)
        signup.clicked.connect(self.signup)
        signup.hide()
        hlay.addWidget(signup)

        self.sign.toggled.connect(signin.setVisible)
        self.sign.toggled.connect(signup.setVisible)

        profile_lay.addStretch()

        theme = QCheckBox("Theme")
        profile_lay.addWidget(theme)

        theme_box = ThemeBox(home)
        theme_box.hide()
        profile_lay.addWidget(theme_box)
        theme.toggled.connect(theme_box.setVisible)

        self.server_uri = QCheckBox("Server URI")
        profile_lay.addWidget(self.server_uri)

        frame = HFrame()
        frame.hide()
        self.server_uri.toggled.connect(frame.setVisible)
        profile_lay.addWidget(frame)
        lay = frame.layout()

        self.uri = LineEdit(placeholder="ws://localhost:8000")
        lay.addWidget(self.uri)

        save_uri = TextButton(text="Save URI")
        addShadow(save_uri)
        save_uri.clicked.connect(self.save_uri)
        lay.addWidget(save_uri)

        self.status_text = Label()
        profile_lay.addWidget(self.status_text)

        self.spacerItem = QSpacerItem(
            0, 20, QSizePolicy.Ignored, QSizePolicy.MinimumExpanding
        )
        self.layout().addSpacerItem(self.spacerItem)

        self.load()
        self.toggle()

    def update_status(self):
        text = "Not Connected."
        if self.client.started:
            text = "Connecting..."
        elif self.client.connected:
            text = "Connected To Server."
        elif self.client.signed_in:
            text = "Signed In"
            self.status.setIcon(":cloud")

        self.status_text.setText(text)

    def load(self):
        if user := self.home.user:
            self.setSign(user.id, user.key)
        else:
            self.sign.setChecked(True)

        self.update_status()

    def setSign(self, id: str, key: str):
        self.id.setValue(id)
        self.key.setValue(key)

    def save_uri(self):
        uri = self.uri.text()
        if uri == CrypticUIClient.URI:
            return

        try:
            CrypticUIClient.parse_url(uri)
            CrypticUIClient.URI = uri
            CrypticUIClientData.save_data()
            QMessageBox.information(
                self, "Server URI Saved", "Server URI saved successfully."
            )

        except Exception as e:
            QMessageBox.information(
                self, "Invalid Server URI", f"The URI inputed is invalid.\n{e}"
            )

    def sign_check(self):
        id = self.id.value()
        key = self.key.value()

        if not CrypticUIClient.URI:
            QMessageBox.information(
                self, "Invalid Server URI", "Server URI is not set."
            )
            return

        if not (id and key):
            QMessageBox.information(self, "Invalid Inputs", "Input ID and Key.")
            return

        return id, key

    @property
    def client_connected(self) -> bool:
        if not self.client.connected:
            self.home.start_client()
        return self.client.connected

    def signup(self):
        if id_key := self.sign_check():
            if self.client_connected:
                self.client.signup(*id_key)

    def signin(self):
        if id_key := self.sign_check():
            if self.client_connected:
                self.client.signin(*id_key)

    def toggle(self):
        if not self.expanded:
            self.profile.show()
            self.layout().removeItem(self.spacerItem)
        super().toggle()

    def finished(self):
        if not self.expanded:
            self.profile.hide()
            self.layout().addSpacerItem(self.spacerItem)

    def showEvent(self, event: QShowEvent) -> None:
        if not self.home._user:
            id = "mimi"
            key = "prmp"
            self.setSign(id, key)

        if not CrypticUIClient.URI:
            self.uri.setText("ws://localhost:8000")
            self.server_uri.setChecked(True)
