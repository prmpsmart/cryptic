from .side_menu import *
from .recpients import *
from .room import *


class CrypticHome(HFrame):
    def __init__(self, app: QApplication, **kwargs):
        super().__init__(**kwargs)

        self.app = app
        self.theme = GreyTheme

        self.setWindowTitle("Cryptic")
        self.setMinimumHeight(600)

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
