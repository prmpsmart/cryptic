CRYPTIC_QSS = """
CrypticHome, RoomView, ChatsView, ChatsList, #chats_list {{
    background: {theme.one};
}}

SideMenu {{
    border-top-right-radius: 5px;
    border-bottom-right-radius: 5px;
    background: {theme.three};
}}

RecipientsView, RecipientsList, #recipients_list {{
    border-radius: 5px;
    background: {theme.two};
}}

RoomView {{
    border-top-left-radius: 5px;
    border-bottom-left-radius: 5px;
    border-left: 1px solid {theme.three};
}}


SideMenu AvatarButton {{
    background: {theme.one};
    border-radius: 20px;
    max-width: 40px;
    max-height: 40px;
}}

SideMenu AvatarButton:hover {{
    background: {theme.three};
}}

SideMenu AvatarButton:pressed {{
    background: {theme.two};
}}

SideMenu ImageLabel {{
    background: {theme.two};
    min-height: 120px;
}}

Detail {{
    border-radius: 5px;
    border: 1px solid {theme.one};
}}

Label, LineEdit, QGroupBox {{
    font-family: Times New Roman;
}}

Detail LeftAlignLabel, SideMenu QGroupBox::title {{
    color: {theme.one};
    font-size: 15px;
    font-weight: bold;
}}

Detail LineEdit {{
    font-size: 15px;
    border-radius: 5px;
    min-height: 25px;
    background: {theme.six};
    color: {theme.one};
    padding: 5px;
}}

Detail Button {{
    border: 1px solid {theme.two};
    border-radius: 10px;
    max-width: 20px;
    max-height: 20px;
}}

Detail Button:pressed {{
    border: 1px solid {theme.six};
}}

SideMenu QGroupBox {{
    font-size: 15px;
    border-radius: 5px;
    border: 1px solid {theme.one};
    padding-top: 30px;
    max-height: 250px;
    background: {theme.three};
}}

SideMenu QGroupBox::title {{
    color: {theme.six};
    background: {theme.one};
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 3px 98px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
}}

RecipientsView LineEdit {{
    font-size: 18px;
    font-family: Times New Roman;
    border: none;
    border-bottom: 2px solid {theme.five};
    background: {theme.one};
    color: {theme.six};
    padding: 5px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
}}

RecipientsView IconTextButton {{
    background: {theme.one};
    border-radius: 15px;
    border: 3px solid {theme.five};
    max-width: 25px;
}}

RecipientsView IconTextButton:hover {{
    background: {theme.two};
    border: 3px solid {theme.two};
}}

RecipientsView IconTextButton:pressed {{
    background: {theme.one};
}}

RecipientItem {{
    min-height: 65px;
    max-height: 65px;
    border-radius: 5px;
    background: {theme.two};
}}

RecipientItem:hover {{
    background: {theme.three};
    border: 1px solid {theme.one};
}}

RecipientItem:checked, RecipientItem:pressed {{
    background: {theme.three};
    border: 1px solid {theme.one};
}}

RecipientItem#invalid {{
    background: {theme.one};
    border: 1px solid {theme.two};
}}

RecipientItem#invalid:hover {{
    background: {theme.one};
}}

RecipientItem#invalid:checked, RecipientItem#invalid:pressed {{
    border: 1px solid {theme.five};
}}

RecipientItem AvatarButton, Header AvatarButton {{
    border-radius: 20px;
    max-width: 50px;
}}

RecipientItem Label {{
    min-width: 30px;
    font-family: Times New Roman;
    font-size: 15px;
    color: {theme.six};
}}

RecipientItem Label#id {{
    font-size: 20px;
    font-weight: bold;
}}

RecipientItem Label#time {{
    font-size: 13px;
}}

RecipientItem Label#text {{
    font-size: 14px;
}}

RecipientItem Label#unreads {{
    font-size: 12px;
    background: {theme.six};
    color: {theme.one};
    border-radius: 5px;
}}

Header {{
    background: {theme.three};
    border-top-left-radius: 5px;

}}

Header Label#id {{
    font-size: 25px;
    color: {theme.one};
    color: black;
}}

Header IconTextButton, Footer IconTextButton {{
    border-radius: 15px;
    max-width: 25px;
    background: {theme.four};
}}

Header IconTextButton:hover, Footer IconTextButton:hover {{
    background: {theme.five};
}}

Header IconTextButton:pressed, Footer IconTextButton:pressed {{
    background: {theme.three};
}}

ChatSearchDialog LineEdit {{
    padding: 5px;
    border: none;
    border-bottom: 2px solid #e1e1e1;
    border-radius: 5px;
}}


Footer {{
    background: {theme.three};
    border-bottom-left-radius: 5px;
}}


TextInput {{
    border: none;
    font-size: 14px;
    padding-top: 5px;
    border-bottom: 1px solid {theme.one};
}}

ChatItem {{
    border: 1px solid {theme.five};
    background: {theme.two};
    border-radius: 5px;
    padding: 5px;
}}

ChatItem Label#text {{
    font-size: 15px;
}}

ChatItem#left {{
    border: 1px solid {theme.five};
    background: {theme.four};
}}

"""
# CRYPTIC_QSS = ''
