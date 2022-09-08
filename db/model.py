import json


class Model:
    def __init__(self):
        pass

    def to_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, dump):
        return cls(**json.loads(dump))

    def __str__(self) -> str:
        return self.to_json()

    def content(self) -> dict:
        fields = self.__dict__
        return {name: fields[name] for name in fields if fields[name] is not None}