from enum import Enum, auto

class TokenType(Enum):

    IF_KEYWORD = auto()
    ELSE_KEYWORD = auto()
    WHILE_KEYWORD = auto()
    FOREACH_KEYWORD = auto()
    RETURN_KEYWORD = auto()
    AS_KEYWORD = auto()
    VOID_KEYWORD = auto()
    INT_KEYWORD = auto()
    FLOAT_KEYWORD = auto()
    STRING_KEYWORD = auto()
    DICT_KEYWORD = auto()
    NULL_KEYWORD = auto()

    LEFT_ROUND_BRACKET = auto()
    RIGHT_ROUND_BRACKET = auto()
    LEFT_SQUARE_BRACKET = auto()
    RIGHT_SQUARE_BRACKET = auto()
    LEFT_CURLY_BRACKET = auto()
    RIGHT_CURLY_BRACKET = auto()

    COMMA = auto()
    COLON = auto()
    SEMICOLON = auto()

    PLUS_OPERATOR = auto()
    MINUS_OPERATOR = auto()
    MULTIPLICATION_OPERATOR = auto()
    DIVISION_OPERATOR = auto()
    MODULO_OPERATOR = auto()
    NEGATION_OPERATOR = auto()
    NULLABLE_OPERATOR = auto()

    OR_OPERATOR = auto()
    AND_OPERATOR = auto()
    LESS_THAN_OPERATOR = auto()
    LESS_THAN_OR_EQUAL_OPERATOR = auto()
    GREATER_THAN_OPERATOR = auto()
    GREATER_THAN_OR_EQUAL_OPERATOR = auto()
    EQUAL_OPERATOR = auto()
    NOT_EQUAL_OPERATOR = auto()

    ASSIGNMENT = auto()
    IDENTIFIER = auto()
    STRING_LITERAL = auto()
    INT_LITERAL = auto()
    FLOAT_LITERAL = auto()
    EOF = auto()


class Token:
    def __init__(self, type_: TokenType, value: str = "", position: int = 0):
        self.type = type_
        self.value = value
        self.position = position  # Can help with debugging

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, pos={self.position})"


