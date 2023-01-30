LOGGED_IN = "Logged In"
NOT_LOGGED_IN = "Not Logged In"
SIGNED_UP = "Signed Up"
INVALID = "Invalid inputs"
ID_UNAVAILABLE = "ID Not Available"
ADDED = "Added Successfully"


class CrypticUser:
    def __init__(self, id: str, key: str, avatar: str = "") -> None:
        self.id = id
        self.key = key
        self.avatar = avatar

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"

    def __bool__(self):
        return True
