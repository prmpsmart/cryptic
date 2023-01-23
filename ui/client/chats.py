from .recpients import *


class ChatItem(StatusItem, VFrame):
    def __init__(self, chats_list: "ChatsList", chat: Chat):
        VFrame.__init__(self, objectName="right" if chat.isMe else "left")
        StatusItem.__init__(self)
        self.chats_list = chats_list

        self.chat = chat

        lay = self.layout()
        m = 0
        lay.setSpacing(m)
        lay.setContentsMargins(m, m, m, m)

        self.text_label.setSizePolicy(POLICY)
        self.text_label.setContentsMargins(0, 0, 0, 0)
        self.text_label.setWordWrap(True)
        self.text_label.setTextFormat(Qt.RichText)
        self.text_label.setTextInteractionFlags(
            Qt.LinksAccessibleByMouse | Qt.TextSelectableByMouse
        )

        self.update_text(chat.text)
        self.update_time(chat.time)

        lay.addWidget(self.text_label)

        hlay = QHBoxLayout()
        lay.addLayout(hlay)

        hlay.addStretch()

        hlay.addWidget(self.time)

        if chat.isMe:
            self.update_status(chat.sent)
            hlay.addWidget(self.status)
            self.status.show()

        chats_list.resized.connect(self.on_chats_list_resized)

    def on_chats_list_resized(self):
        width = self.chats_list._widget.width() * 0.8
        self.setMaximumWidth(width)

    def showEvent(self, event: PySide6.QtGui.QShowEvent) -> None:
        self.on_chats_list_resized()

    def search(self, text: str) -> bool:
        return text.lower() in self.chat.text.lower()


class ChatsList(SearchableList):
    resized = Signal()

    def __init__(self, room_view, **kwargs):
        super().__init__(
            reverse=0, widgetKwargs=dict(objectName="chats_list"), **kwargs
        )

        self.room_view = room_view
        self.hide_hbar()
        self.widgetLayout().setAlignment(Qt.AlignBottom)

    def add(self, item: ChatItem):
        super().add(
            item,
            stretch=1,
            alignment=(Qt.AlignRight if item.chat.isMe else Qt.AlignLeft)
            | Qt.AlignBottom,
        )

    def add_chat(self, chat: Chat):
        self.addItem(ChatItem(self, chat))

        QTimer.singleShot(100, lambda: self.scroll_down(0, self.maximumHeight()))

    def resizeEvent(self, arg__1: PySide6.QtGui.QResizeEvent) -> None:
        self._widget.setMaximumWidth(self.width())
        self.resized.emit()

    def fill(self, items: list[ChatItem]):
        items = self.arrange_items(items)

        for item in items:
            self.widgetLayout().addWidget(
                item,
                1,
                Qt.AlignBottom | (Qt.AlignRight if item.chat.isMe else Qt.AlignLeft),
            )


class ChatsView(VFrame, Shadow):
    def __init__(self, ui: HFrame):
        VFrame.__init__(self)
        Shadow.__init__(self)

        self.setMinimumWidth(400)
