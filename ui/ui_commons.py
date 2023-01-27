from prmp_qt import *
from .theme import *


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


class ThemeButton(QPushButton):
    def __init__(self, theme: Theme, home: HFrame):
        super().__init__()
        self.home = home
        self.theme = theme
        self.theme_style()

    def theme_style(self):
        border = (
            self.home.app.theme.six
            if self.theme == self.home.app.theme
            else self.home.app.theme.one
        )

        self.setStyleSheet(
            """
            ThemeButton {{
                min-height: 50px;
                max-height: 50px;
                border-radius: 10px;
                border: 2px solid {border};
                background: {theme.one}
            }}
            ThemeButton:hover {{
                background: {theme.three}
            }}
            ThemeButton:pressed {{
                background: {theme.two}
            }}
        """.format(
                theme=self.theme, border=border
            )
        )

        self.clicked.connect(self.change_theme)

    def change_theme(self):
        self.home.app.update_theme(self.theme)


class ThemeBox(QGroupBox):
    def __init__(self, home):
        super().__init__("Theme")

        theme_lay = QGridLayout(self)

        row = col = 0
        for index, theme in enumerate(Themes):
            tb = ThemeButton(theme, home)
            col = index % 2
            theme_lay.addWidget(tb, row, col)

            if index and col:
                row += 1
