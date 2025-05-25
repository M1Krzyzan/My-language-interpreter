from src.ast.types import Type


class TypedValue:
    def __init__(self, type: Type, value: int | float | bool | str):
        self.value = value
        self.type = type
