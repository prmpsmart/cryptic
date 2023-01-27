import site

site.addsitedir("../prmp_qt")

from ui.client import *


class CrypticClientApp(QApplication):
    theme_update = Signal()

    def __init__(self):
        super().__init__()
        CrypticUIClientData.load_data()

        self.theme = GreyTheme

        if CrypticUIClientData.THEME:
            self.theme = CrypticUIClientData.THEME

        self.ui = CrypticHome(self)
        self.ui.destroyed.connect(self.quit)
        self.ui.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.update_theme(self.theme)

    def update_theme(self, theme: Theme):
        self.theme = theme
        CrypticUIClientData.THEME = theme
        self.add_style_sheet(CRYPTIC_QSS.format(theme=theme))
        self.theme_update.emit()

    def start(self):
        self.ui.show()
        self.exec()


a = CrypticClientApp()
a.start()
