from prmp_qt import *
from .qss import CRYPTIC_QSS
from .theme import *
from . import resources


class Dialog(RoundDialog):
    def __init__(self, *args, **kwargs):
        self.opened = False
        super().__init__(*args, **kwargs)

    def showEvent(self, _: QShowEvent) -> None:
        self.opened = True


def MOVE_DIALOG_TO_CURSOR(dialog: Dialog, *args, **kwargs):
    MOVE_TO_CURSOR(dialog, *args, **kwargs)

    if not dialog.opened:
        MOVE_TO_CURSOR(dialog, *args, **kwargs)


POLICY = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
