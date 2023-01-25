import site

site.addsitedir("../prmp_qt")

from ui.server import *

IP = '127.0.0.1'
PORT = 8000


class CrypticServerApp(QApplication):
    theme_update = Signal()

    def __init__(self):
        super().__init__()

        self.ui = CrypticServerHome(self, (IP, PORT))
        self.ui.destroyed.connect(self.quit)

        self.update_theme(self.ui.theme)

    def update_theme(self, theme: Theme):
        self.ui.theme = theme
        self.add_style_sheet(CRYPTIC_QSS.format(theme=theme))
        self.theme_update.emit()

    def start(self):
        self.ui.show()
        self.exec()
    


a = CrypticServerApp()
a.start()
