import site
site.addsitedir('../prmp_qt')

from ui.client import *


class CrypticClientApp(QApplication):
    def __init__(self):
        super().__init__()

        # threading.Thread(target=AmeboClientData.load).start()

        self.add_style_sheet(CRYPTIC_QSS)

        self.ui = CrypticClientUI()
        # self.ui = AmeboUI_R()
        self.ui.destroyed.connect(self.quit)

    def start(self):
        self.ui.show()
        self.exec()


a = CrypticClientApp()
a.start()
