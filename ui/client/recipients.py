from .commons import *


class StatusItem(SearchableItem, Shadow):
    ICONS: list[QIcon] = []

    def __init__(self):
        SearchableItem.__init__(self)
        Shadow.__init__(self)

        if not StatusItem.ICONS:
            StatusItem.ICONS = [
                QSvgIcon(":clock", color=Qt.white),
                QSvgIcon(":check", color=Qt.white),
            ]

        self.status = IconButton(
            icon=self.ICONS[0],
            iconSize=15,
            border=False,
            clickable=False,
            color=Qt.white,
        )
        self.status.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.status.hide()

        self.time = Label(objectName="time")

    def update_status(self, sent: bool = False):
        self.status.setIcon(self.ICONS[sent])

    def update_time(self, time: int):
        self.time.setText(TIME2STRING(time))


class RecipientItem(Button, StatusItem):
    def __init__(self, recipient_view: "RecipientsView", recipient: Recipient):
        Button.__init__(self)
        StatusItem.__init__(self)

        self.recipient = recipient
        self.recipient_view = recipient_view
        self.clicked.connect(recipient_view.recipient_item_selected)

        self.setMinimumWidth(self.recipient_view.w - 50)
        self.setMaximumWidth(self.recipient_view.w)

        self.setCheckable(True)
        self.setAutoExclusive(True)

        lay = QHBoxLayout(self)

        self.avatar = AvatarButton(mask=51, icon=":user", iconColor=Qt.white)
        self.avatar.setAttribute(Qt.WA_TransparentForMouseEvents)
        lay.addWidget(self.avatar)

        col = QVBoxLayout()
        lay.addLayout(col)

        top_row = QHBoxLayout()
        col.addLayout(top_row)

        self.id = Label(objectName="id")
        top_row.addWidget(self.id)

        top_row.addStretch()

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(3)
        col.addLayout(bottom_row)

        self.text_label = Label(objectName="text")
        bottom_row.addWidget(self.text_label)

        bottom_row.addWidget(self.status, 0, Qt.AlignRight)

        self.unreads = AlignLabel(objectName="unreads")
        bottom_row.addWidget(self.unreads, 0, Qt.AlignRight)

        col.addWidget(self.time, 0, Qt.AlignRight)
        col.setSpacing(0)

        m = 0
        for l in (bottom_row, bottom_row, col):
            l.setContentsMargins(m, m, m, m)
        m = 5
        lay.setContentsMargins(m, m, m, m)

        self.text_label.hide()

        self.load()
        self.avatar_timer_id = self.startTimer(10)

    def update_text(self, text: str):
        self.text_label.setText(text)

    def load(self):
        self.id.setText(self.recipient.id)
        if self.recipient.invalid:
            self.setObjectName("invalid")

        if last_chat := self.recipient.last_chat:
            self.update_time(last_chat.time)
            self.time.show()

            text = last_chat.text

            if last_chat.isMe:
                self.update_status(last_chat.sent)
                self.status.show()
                text = "You: " + text

            else:
                self.status.hide()

            self.update_text(text)
            self.text_label.show()

        else:
            self.time.hide()
            self.text_label.hide()

        if unreads := self.recipient.unreads:
            self.unreads.setText(str(unreads) if unreads < 100 else "99+")
            self.unreads.show()
        else:
            self.unreads.hide()

    def search(self, text: str) -> bool:
        text = text.lower()

        searchables = [
            self.recipient.id,
            *[chat.text for chat in self.recipient.chats],
        ]

        for searchable in searchables:
            if text in searchable.lower():
                return True

        return False

    def timerEvent(self, e: QTimerEvent) -> None:
        if e.timerId() == self.avatar_timer_id:
            self.avatar.setAvatar(self.recipient.avatar, iconColor=Qt.white)
            self.killTimer(self.avatar_timer_id)


class RecipientsList(SearchableList):
    def __init__(self, **kwargs):
        super().__init__(widgetKwargs=dict(objectName="recipients_list"), **kwargs)
        self._widget.layout().setSpacing(5)

    def arrange_items(self, items: list[RecipientItem]) -> list[RecipientItem]:
        return super().arrange_items(items)


class RecipientsView(VFrame, Shadow):
    def __init__(self, home: HFrame, **kwargs):
        VFrame.__init__(self, **kwargs)
        # Shadow.__init__(self)

        self.home = home
        self.client: CrypticUIClient = home.client

        self.home.add_recipientSignal.connect(self.add_recipient_response)

        self.w = 300
        self.setMinimumWidth(self.w)
        self.setMaximumWidth(self.w)

        lay = self.layout()
        m = 5
        lay.setContentsMargins(m, m, m, m)

        top_lay = QHBoxLayout()
        lay.addLayout(top_lay)

        self.search_recipient = LineEdit(placeholder="Add recipient ...")
        self.search_recipient.returnPressed.connect(self.add_recipient)
        top_lay.addWidget(self.search_recipient)

        add_button = IconTextButton(
            icon=":/user-plus",
            iconColor=Qt.white,
            iconSize=40,
            tip="Add Recipient",
        )
        add_button.clicked.connect(self.add_recipient)
        top_lay.addWidget(add_button)

        addShadow(add_button)

        self.recipients_list = RecipientsList()
        lay.addWidget(self.recipients_list)
        self.search_recipient.textEdited.connect(self.recipients_list.search)

        self.recipients = []

        self.fillRecipients()

    @property
    def user(self) -> CrypticClientUser:
        return self.home.user

    def fillRecipients(self):
        items: SearchableItems = []

        for id, recipient in self.user.recipients.items():
            if id not in self.recipients:
                recipient_item = RecipientItem(self, recipient)
                self.recipients.append(id)
                items.append(recipient_item)

        if items:
            self.recipients_list.fillItems(items)

    def recipient_item_selected(self):
        chat_item: RecipientItem = self.sender()
        self.home.recipient_item_selected(chat_item)

    def add_recipient(self):
        id = self.search_recipient.text().strip()

        if self.user:
            if id:
                if id == self.user.id:
                    QMessageBox.information(
                        self, "Add Recipient", "You can't add youself."
                    )
                elif id in self.user.recipients:
                    QMessageBox.information(
                        self, "Add Recipient", "Recipient already added."
                    )
                elif not self.client.connected:
                    QMessageBox.information(self, "Add Recipient", "Not Signed In.")
                else:
                    self.client.add_recipient(id)
                self.search_recipient.clear()
            else:
                QMessageBox.information(self, "Add Recipient", "Input ID.")
        else:
            QMessageBox.information(self, "Add Recipient", "No Signed Up User.")

    def add_recipient_response(self, json: Json):
        QMessageBox.information(self, "Add Recipient", f"'{json.id}' {json.response}")
        if json.response == ADDED:
            self.fillRecipients()
