from client import *
from ..ui_commons import *
from . import resources
from .qss import CRYPTIC_QSS


class CrypticUIClientData(CrypticClientData):
    THEME: Theme = None

    @classmethod
    def on_save(cls) -> str:
        cls.DATA.theme = cls.THEME

    @classmethod
    def on_load(cls) -> str:
        cls.THEME = cls.DATA.theme


class CrypticUIClient(CrypticClient):
    DATA = CrypticUIClientData

    def __init__(self, signal: Signal, **kwargs):
        super().__init__(**kwargs)

        self.signal = signal

    def on_connected(self):
        super().on_connected()

        self.signal.emit()
        if user := self.DATA.user():
            if user.id and user.key:
                self.signin(user.id, user.key)

    def on_closed(self):
        super().on_closed()
        self.signal.emit()


CrypticUIClientData.CLIENT = CrypticUIClient
