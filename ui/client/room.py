from .chats import *


class HF(HFrame, Shadow):
    def __init__(self, room_view: "RoomView", h=60, **kwargs):
        HFrame.__init__(self, **kwargs)
        Shadow.__init__(self)

        self.h = h
        self.room_view = room_view
        self.set_h(h)

    def set_h(self: QWidget, h):
        self.setMinimumHeight(h)
        self.setMaximumHeight(h)


class ChatSearchDialog(Dialog):
    def __init__(self, textEdited: Callable[[str], None], **kwargs):
        super().__init__(add_shadow=1, **kwargs)

        lay = self.windowLayout()
        self.windowFrame().setStyleSheet("background: white;")

        self.search = LineEdit(placeholder="Search chats ...")
        self.search.textEdited.connect(textEdited)
        lay.addWidget(self.search)


class Header(HF):
    def __init__(self, *args, **kwargs):
        HF.__init__(self, *args, h=55, **kwargs)

        lay = self.layout()

        m = 0
        lay.setContentsMargins(5, m, 5, m)
        lay.setSpacing(10)

        self.chat_search_dialog: ChatSearchDialog = None

        self.avatar = AvatarButton(
            mask=45, icon=":user", clickable=False, iconColor=Qt.white
        )
        lay.addWidget(self.avatar)

        col = QVBoxLayout()
        col.setContentsMargins(5, 10, 5, 10)
        col.setSpacing(2)
        lay.addLayout(col)

        self.id = Label(objectName="id")
        col.addWidget(self.id)

        lay.addStretch()

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(5)
        lay.addLayout(row)

        row.addStretch()

        self.notification = IconTextButton(
            icon=":bell-off",
            checkable=True,
            iconSize=60,
            tip="Notification",
            iconColor=Qt.white,
        )
        self.notification.toggle()
        self.notification.toggled.connect(self.toggle_notification)
        self.notification.clicked.connect(self.delete_recipient)
        row.addWidget(self.notification)
        addShadow(self.notification)

        search = IconTextButton(
            icon=":search", iconSize=60, tip="Search", iconColor=Qt.white
        )
        search.clicked.connect(self.toggle_chat_search_dialog)
        row.addWidget(search)
        addShadow(search)

    def load(self):
        icon = id = ""
        if recipient_item := self.room_view.recipient_item:
            recipient = recipient_item.recipient
            id = recipient.id
            if recipient.avatar:
                icon = recipient_item.avatar.icon()

        if icon:
            self.avatar.setIcon(icon)
        self.id.setText(id)

    def delete_recipient(self):
        if recipient_item := self.room_view.recipient_item:
            user: CrypticClientUser = self.room_view.home.user

            recipient = recipient_item.recipient
            del user.recipients[recipient.id]

            self.room_view.recipient_item = None
            self.load()
            self.room_view.home.recipients_view.fillRecipients()
            self.room_view.chats_list.deleteItems()

    def toggle_notification(self, toggled: bool):
        self.notification.setIcon(":bell-off" if toggled else ":bell")

    def toggle_chat_search_dialog(self):
        if not self.chat_search_dialog:
            self.chat_search_dialog = ChatSearchDialog(
                self.room_view.chats_list.search, parent=self.window()
            )

        MOVE_DIALOG_TO_CURSOR(self.chat_search_dialog, True)


class Footer(HF):
    def __init__(self, *args, **kwargs):
        HF.__init__(self, *args, h=55, **kwargs)

        lay = self.layout()
        m = 5
        lay.setSpacing(m)
        lay.setContentsMargins(m, m, m, m)

        self.text_input = TextInput(
            self, min_height=40, max_height=200, callback=self.on_send
        )
        lay.addWidget(self.text_input)

        send = IconTextButton(icon=":send", iconSize=60, tip="Send", iconColor=Qt.white)
        send.clicked.connect(self.on_send)
        lay.addWidget(send)
        addShadow(send)

    def on_send(self):
        recipient_item = self.room_view.recipient_item
        if recipient_item:
            recipient = recipient_item.recipient
            if text := self.text_input.text:
                json = Json(
                    recipient=recipient.id,
                    time=TIME(),
                    id=self.room_view.home.user.id,
                    text=text,
                )
                recipient.add_chat(json)
                chat = recipient.chats[json.time]
                self.room_view.chats_list.add_chat(chat)
                self.room_view.home.client.text(json)
            else:
                QMessageBox.information(self, "Text Input", "Input text first.")
        else:
            QMessageBox.information(self, "Choose Recipient", "Choose recipient first.")

        self.text_input.clear()

    def showEvent(self, event: QShowEvent) -> None:
        self.text_input.setTextInputSize()


class RoomView(VFrame):
    def __init__(self, home: HFrame, **kwargs):
        VFrame.__init__(self, **kwargs)
        self.home = home

        self.recipient_item: RecipientItem = None
        self.setMinimumWidth(400)

        self.home.textSignal.connect(self.text_handler)

        lay = self.layout()
        lay.setSpacing(0)

        m = 0
        lay.setContentsMargins(m, m, m, m)

        self.header = Header(self)
        lay.addWidget(self.header)

        self.chats_list = ChatsList(self)
        lay.addWidget(self.chats_list)

        self.footer = Footer(self)
        lay.addWidget(self.footer)

        self.chats_time: list[int] = []

    @property
    def recipient(self) -> Recipient:
        if self.recipient_item:
            return self.recipient_item.recipient

    def recipient_item_selected(self, recipient_item: RecipientItem):
        if recipient_item == self.recipient_item:
            return

        self.chats_time.clear()

        self.recipient_item = recipient_item
        self.header.load()

        times = list(recipient_item.recipient.chats.keys())
        times.sort()

        self.chats_list.deleteItems()

        for time in times:
            self.chats_time.append(time)
            chat = recipient_item.recipient.chats[time]
            self.chats_list.add_chat(chat)

    def text_handler(self, json: Json):
        if (
            self.recipient
            and (user := self.home.user)
            and (recipient := json.recipient)
            and (id := json.id)
            and (time := json.time)
        ):
            ids = (recipient, id)
            if (
                (user.id in ids)
                and (self.recipient.id in ids)
                and (time not in self.chats_time)
            ):
                chat = self.recipient.chats[time]
                self.chats_list.add_chat(chat)

        # self.chats_list.add_chat(chat)
