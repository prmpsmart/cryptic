from ..ui_commons import *


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

        self.value = LineEdit(placeholder=holder)
        self.value.setDisabled(True)
        hlay.addWidget(self.value)

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

            self.value.setEchoMode(QLineEdit.Password)

            self.eye = Button(icon=self.eye_icon, iconSize=20)
            self.eye.setCheckable(True)
            self.eye.setToolTip("Show")
            self.eye.toggled.connect(self.toggle_eye)
            hlay.insertWidget(1, self.eye)

    def toggle_action(self, toggle: bool):
        icon = self.check_icon if toggle else self.edit_icon
        tip = "Save" if toggle else "Edit"
        self.action.setIcon(icon)
        self.value.setEnabled(toggle)
        self.action.setToolTip(tip)

        if not toggle:
            attr = self.title.text().lower().replace(" :", "")

    def toggle_eye(self, toggle: bool):
        icon = self.eye_off_icon if toggle else self.eye_icon
        tip = "Hide" if toggle else "Show"
        echo = QLineEdit.Normal if toggle else QLineEdit.Password

        self.value.setEchoMode(echo)
        self.eye.setIcon(icon)
        self.value.setEnabled(toggle)
        self.eye.setToolTip(tip)


class SideMenu(Expandable, VFrame, Shadow):
    def __init__(self, home):
        VFrame.__init__(self)
        Expandable.__init__(self, max_width=250, min_width=50)
        Shadow.__init__(self)

        lay = self.layout()
        m = 5
        lay.setContentsMargins(m, m, m, m)

        hlay = QHBoxLayout()
        lay.addLayout(hlay)

        hlay.addStretch()

        color = QColor("white")

        self.avatar = AvatarButton(
            icon=":user-2", iconSize=40, mask=30, iconColor=color
        )
        self.avatar.clicked.connect(self.toggle)
        hlay.addWidget(self.avatar)
        addShadow(self.avatar)

        self.profile = VFrame()
        self.profile.hide()
        profile_lay = self.profile.layout()
        m = 0
        profile_lay.setContentsMargins(m, m, m, m)
        lay.addWidget(self.profile)

        self.image = ImageLabel(default=QSvgPixmap(":user-2", color).toImage())
        profile_lay.addWidget(self.image)

        self.id = Detail(title="ID :", holder="ID of this client.")
        profile_lay.addWidget(self.id)

        self.key = Detail(title="Key :", holder="Key of this client.", hide=True)
        profile_lay.addWidget(self.key)

        profile_lay.addStretch()

        theme_box = ThemeBox(home)
        profile_lay.addWidget(theme_box)

        self.stretch = QSpacerItem(
            0, 20, QSizePolicy.Ignored, QSizePolicy.MinimumExpanding
        )
        self.layout().addSpacerItem(self.stretch)

    def toggle(self):
        if not self.expanded:
            self.profile.show()
            self.layout().removeItem(self.stretch)
        super().toggle()

    def finished(self):
        if not self.expanded:
            self.profile.hide()
            self.layout().addSpacerItem(self.stretch)
