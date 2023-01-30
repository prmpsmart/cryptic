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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_connected(self):
        super().on_connected()

        if user := self.DATA.user():
            if user.id and user.key:
                self.signin(user.id, user.key)


CrypticUIClientData.CLIENT = CrypticUIClient
