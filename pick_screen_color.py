from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class App(QApplication):
    def __init__(self):
        super().__init__()
        self.ui = QWidget()
        QVBoxLayout(self.ui)

        self.ui.destroyed.connect(self.quit)
        self.theme()

    def theme(self):
        l = self.ui.layout()

        self.color = QPushButton("Color name")
        l.addWidget(self.color)
        self.color.clicked.connect(self.startT)

        self.text = QTextEdit()
        l.addWidget(self.text)

        self.colors = []
        self.id = 0

    def startT(self):
        if self.id:
            self.killTimer(self.id)
        self.colors.clear()
        self.id = self.startTimer(2000)

    def timerEvent(self, event: QTimerEvent) -> None:
        screen = self.primaryScreen()
        r = screen.availableGeometry()
        r = r.x(), r.y(), r.width(), r.height()

        pm = screen.grabWindow(0, *r).toImage()
        cur = QCursor.pos()
        pix = pm.pixel(cur)
        color = QColor(pix)
        self.update_color(color)

    def update_color(self, color: QColor):
        if len(self.colors) == 6:
            self.killTimer(self.id)
            self.id = 0
        else:
            self.colors.append(color.name())
        self.text.setText(str(self.colors))

    def start(self):
        self.ui.show()
        self.exec()


a = App()
a.start()
