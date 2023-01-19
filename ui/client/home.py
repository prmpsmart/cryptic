from ..ui_commons import *

class SideMenu(Expandable, VFrame, Shadow):
    def __init__(self, *args):
        VFrame.__init__(self)
        Expandable.__init__(self, max_width=170, min_width=45)
        Shadow.__init__(self)

        lay = self.layout()

        details_frame = HFrame()
        details_lay = details_frame.layout()

        lay.addWidget(details_frame)

        self.avatar = AvatarButton(icon=":/user-2")
        details_lay.addWidget(self.avatar)




class CrypticClientUI(HFrame):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setWindowTitle('Cryptic')
        self.setMinimumSize(500, 500)

        lay = self.layout()

        self.side_menu = SideMenu(self)
        lay.addWidget(self.side_menu)
