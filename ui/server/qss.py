CRYPTIC_QSS = """
CrypticServerHome, Users, #users_list {{
    background: {theme.one};
    border-radius: 5px;
    border: 2px solid {theme.two};
}}

QPushButton, CrypticServerHome > IconTextButton  {{
    min-height: 25px;
    max-height: 25px;
    border-radius: 5px;
    border: 2px solid {theme.four};
    font-weight: bold;
    font-size: 14px;
    padding: 5px;
}}

QPushButton {{
    background: {theme.five};
    color: {theme.one};
}}

QPushButton:hover {{
    background: {theme.four};
    border: 2px solid {theme.three};
}}

QPushButton:checked {{
    background: {theme.three};
    border: 2px solid {theme.two};
}}

CrypticServerHome > IconTextButton {{
    color: {theme.six};
    background: {theme.one};
}}

ThemeBox {{
    font-family: Times New Roman;
    font-size: 15px;
    border-radius: 5px;
    border: 1px solid {theme.one};
    padding-top: 30px;
    max-height: 300px;
    background: {theme.three};
}}

ThemeBox::title {{
    color: {theme.one};
    font-size: 15px;
    font-weight: bold;
    color: {theme.six};
    background: {theme.one};
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 3px 40px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
}}

UserItem {{
    border: 1px solid {theme.one};
    background: {theme.four};
    border-radius: 5px;
}}

UserItem:hover {{
    border: 1px solid {theme.five};
    background: {theme.three};
}}

UserItem Label {{
    font-size: 14px;
    font-family: Times New Roman;
}}

UserItem Label#label {{
    font-weight: bold;
}}

UserItem#closed {{
    background: {theme.one};
}}

UserItem#closed Label {{
    color: {theme.six};
}}



"""
# CRYPTIC_QSS = ''
