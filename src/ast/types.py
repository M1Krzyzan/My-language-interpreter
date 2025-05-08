from enum import Enum, auto


class Type(Enum):
    IntType = auto()
    FloatType = auto()
    BoolType = auto()
    StringType = auto()
    VoidType = auto()

    def __eq__(self, other):
        return self.value == other.value

    def __str__(self):
        return self.name