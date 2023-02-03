from .recipients import *


class ChatItem(StatusItem, VFrame):
    def __init__(self, chats_list: "ChatsList", chat: Chat):
        VFrame.__init__(self, objectName="right" if chat.isMe else "left")
        StatusItem.__init__(self)
        self.chats_list = chats_list

        if not chat.sent:
            self.chats_list.room_view.home.textSignal.connect(self.on_text)

        self.chat = chat

        lay = self.layout()
        m = 0
        lay.setSpacing(m)
        lay.setContentsMargins(m, m, m, m)

        self.text_label = Label(chat.text, objectName="text")
        lay.addWidget(self.text_label)

        # self.text_label = QTextEdit()
        # self.text_label.setPlainText(chat.text)

        self.text_label.setTextInteractionFlags(
            Qt.LinksAccessibleByMouse | Qt.TextSelectableByMouse
        )
        self.text_label.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        )

        if isinstance(self.text_label, Label):
            self.text_label.setWordWrap(True)
            self.text_label.setTextFormat(Qt.RichText)

        self.update_time(chat.time)

        hlay = QHBoxLayout()
        lay.addLayout(hlay)

        hlay.addStretch()

        hlay.addWidget(self.time)

        if chat.isMe:
            self.update_status(chat.sent)
            hlay.addWidget(self.status)
            self.status.show()

        chats_list.resized.connect(self.on_chats_list_resized)

    def on_text(self, json: Json):
        if not self.chat.sent:
            same_recipient = json.recipient == self.chat.recipient
            same_time = json.time == self.chat.time
            same_id = json.id == self.chat.id

            if same_recipient and same_time and same_id:
                self.update_status(True)

    def on_chats_list_resized(self):
        width = self.chats_list._widget.width() * 0.8
        self.setMaximumWidth(width)

    def showEvent(self, event: PySide6.QtGui.QShowEvent) -> None:
        # self.on_chats_list_resized()
        if not self.chat.seen:
            self.chats_list.room_view.home.recipients_view.text_handler(self.chat.json)
            self.chat.seen = True

    def search(self, text: str) -> bool:
        return text.lower() in self.chat.text.lower()


class ChatsList(SearchableList):
    resized = Signal()

    def __init__(self, room_view, **kwargs):
        super().__init__(widgetKwargs=dict(objectName="chats_list"), **kwargs)

        self.room_view = room_view
        self.hide_hbar()
        self.widgetLayout().setSpacing(3)

    def add_chat(self, chat: Chat):
        self.addItem(
            ChatItem(self, chat),
            0,
            (Qt.AlignRight if chat.isMe else Qt.AlignLeft),
        )
        QTimer.singleShot(100, lambda: self.scroll_down(0, self.maximumHeight()))

    def resizeEvent(self, arg__1: PySide6.QtGui.QResizeEvent) -> None:
        self._widget.setMaximumWidth(self.width())
        self.resized.emit()
