class Theme:
    def __init__(self, colors: list[str]) -> None:
        self.one, self.two, self.three, self.four, self.five, self.six = colors


RedTheme = Theme(["#612622", "#923931", "#c05045", "#d99590", "#e5b9b6", "#f1dcd9"])

GreenTheme = Theme(["#50632b", "#789440", "#9dbb61", "#c3d69f", "#d7e3bf", "#eaf1df"])

PurpleTheme = Theme(["#54426a", "#7d649e", "#aa9abf", "#ccc2da", "#ddd6e5", "#edeaf1"])

BlueTheme = Theme(["#205867", "#30859a", "#4aacc5", "#91cddb", "#b7dde8", "#dbeef4"])

OrangeTheme = Theme(["#9b4a09", "#ea700d", "#f59c56", "#f9c49a", "#fbd8bc", "#fceadc"])

YellowTheme = Theme(["#7e6000", "#bf9000", "#ffc000", "#fed966", "#ffe59a", "#fff2cd"])

GreyTheme = Theme(["#595959", "#7f7f7f", "#a5a5a5", "#bfbfbf", "#d8d8d8", "#f2f2f2"])

Themes = [
    RedTheme,
    GreenTheme,
    PurpleTheme,
    BlueTheme,
    OrangeTheme,
    YellowTheme,
    GreyTheme,
]
