from src.ast.types import Type


class TypedVariable:
    def __init__(self, name: str, type: Type, value: int | float | bool | str):
        self.name = name
        self.value = value
        self.type = type
