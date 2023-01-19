class CrypticUser:
    def __init__(self, id: str, key: str, avatar: str = "") -> None:
        self.id = id
        self.key = key
        self.avatar = avatar

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"
