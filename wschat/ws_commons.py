from typing import *
import datetime, time, json, os, pickle
from .prmp_websockets import *


def GET_BY_ATTR(
    sequence: Union[list, dict],
    validator: Callable[[Any], Any] = None,
    **attrs_values: dict[str, Any],
):
    """
    return object in sequence whose named attribute is equal to the given value.
    """
    if isinstance(sequence, dict):
        sequence = sequence.values()

    l = len(attrs_values)
    for obj in sequence:
        count = 0
        for attr, value in attrs_values.items():
            val = getattr(obj, attr, None)
            if val and validator:
                val = validator(val)

            if val == value:
                count += 1
            else:
                break

        if count == l:
            return obj


def GET(dict: dict, key: str):
    if isinstance(key, str):
        key = key.lower()
    return dict.get(key, None)


class Json(dict):
    response: int
    JSONDecodeError = json.JSONDecodeError

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, attr, value):
        self[attr] = value

    @classmethod
    def from_str(self, string: str):
        return json.loads(string or "{}", object_hook=Json)

    def to_str(self):
        return json.dumps(self)


Json_Receiver = Callable[[Json], None]
LOWER_VALIDATOR = lambda dn: str(dn).lower()


class Data:
    DATA = None
    DB_FILE = "data.dump"

    @classmethod
    def file(cls, mode: str):
        return open(cls.DB_FILE, mode)

    @classmethod
    def rfile(cls):
        # print("reading file")
        return cls.file("rb")

    @classmethod
    def wfile(cls):
        # print("writing file")
        return cls.file("wb")

    @classmethod
    def load(cls):
        try:
            data = pickle.load(cls.rfile())
            cls.DATA = Json(data)
        except Exception as e:
            print(f"Data Read Error: {e}")

    @classmethod
    def save(cls):
        data = cls.data()
        if isinstance(data, Json):
            data = dict(data)

        file = cls.wfile()
        pickle.dump(data, file)

    @classmethod
    def data(cls):
        if not cls.DATA:
            cls.load()

        return cls.DATA
