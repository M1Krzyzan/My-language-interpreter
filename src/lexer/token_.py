from enum import Enum, auto
from typing import Union

from src.lexer.position import Position


class TokenType(Enum):
    IF_KEYWORD = auto()
    ELIF_KEYWORD = auto()
    ELSE_KEYWORD = auto()
    WHILE_KEYWORD = auto()
    RETURN_KEYWORD = auto()
    BREAK_KEYWORD = auto()
    CONTINUE_KEYWORD = auto()
    TO_KEYWORD = auto()
    FUNC_KEYWORD = auto()
    INT_KEYWORD = auto()
    FLOAT_KEYWORD = auto()
    STRING_KEYWORD = auto()
    BOOL_KEYWORD = auto()
    EXCEPTION_KEYWORD = auto()
    CATCH_KEYWORD = auto()
    TRY_KEYWORD = auto()
    THROW_KEYWORD = auto()

    LEFT_ROUND_BRACKET = auto()
    RIGHT_ROUND_BRACKET = auto()
    LEFT_SQUARE_BRACKET = auto()
    RIGHT_SQUARE_BRACKET = auto()
    LEFT_CURLY_BRACKET = auto()
    RIGHT_CURLY_BRACKET = auto()

    DOT = auto()
    COMMA = auto()
    COLON = auto()
    SEMICOLON = auto()

    PLUS_OPERATOR = auto()
    MINUS_OPERATOR = auto()
    MULTIPLICATION_OPERATOR = auto()
    DIVISION_OPERATOR = auto()
    MODULO_OPERATOR = auto()
    NEGATION_OPERATOR = auto()

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
    BOOLEAN_LITERAL = auto()
    COMMENT = auto()
    ETX = auto()


class Symbols:
    keywords = {
        "if": TokenType.IF_KEYWORD,
        "elif": TokenType.ELIF_KEYWORD,
        "else": TokenType.ELSE_KEYWORD,
        "while": TokenType.WHILE_KEYWORD,
        "return": TokenType.RETURN_KEYWORD,
        "break": TokenType.BREAK_KEYWORD,
        "continue": TokenType.CONTINUE_KEYWORD,
        "to": TokenType.TO_KEYWORD,
        "func": TokenType.FUNC_KEYWORD,
        "int": TokenType.INT_KEYWORD,
        "float": TokenType.FLOAT_KEYWORD,
        "string": TokenType.STRING_KEYWORD,
        "bool": TokenType.BOOL_KEYWORD,
        "exception": TokenType.EXCEPTION_KEYWORD,
        "throw": TokenType.THROW_KEYWORD,
        "try": TokenType.TRY_KEYWORD,
        "catch": TokenType.CATCH_KEYWORD,
        "or": TokenType.OR_OPERATOR,
        "and": TokenType.AND_OPERATOR,
        "not": TokenType.NEGATION_OPERATOR,
    }

    single_char = {
        "(": TokenType.LEFT_ROUND_BRACKET,
        ")": TokenType.RIGHT_ROUND_BRACKET,
        "[": TokenType.LEFT_SQUARE_BRACKET,
        "]": TokenType.RIGHT_SQUARE_BRACKET,
        "{": TokenType.LEFT_CURLY_BRACKET,
        "}": TokenType.RIGHT_CURLY_BRACKET,
        ".": TokenType.DOT,
        ",": TokenType.COMMA,
        ":": TokenType.COLON,
        ";": TokenType.SEMICOLON,
        "+": TokenType.PLUS_OPERATOR,
        "-": TokenType.MINUS_OPERATOR,
        "*": TokenType.MULTIPLICATION_OPERATOR,
        "/": TokenType.DIVISION_OPERATOR,
        "%": TokenType.MODULO_OPERATOR,
        "<": TokenType.LESS_THAN_OPERATOR,
        ">": TokenType.GREATER_THAN_OPERATOR,
        "=": TokenType.ASSIGNMENT,
        '!': TokenType.NEGATION_OPERATOR
    }

    double_char = {
        "<=": TokenType.LESS_THAN_OR_EQUAL_OPERATOR,
        ">=": TokenType.GREATER_THAN_OR_EQUAL_OPERATOR,
        "==": TokenType.EQUAL_OPERATOR,
        "!=": TokenType.NOT_EQUAL_OPERATOR,
    }

    boolean_literals = {
        "true": TokenType.BOOLEAN_LITERAL,
        "false": TokenType.BOOLEAN_LITERAL
    }

    comment_map = {
        "$": "$",
        "#": "\n"
    }


class Token:
    def __init__(self, token_type: TokenType, position: Position, value: Union[str, int, float, bool] = None):
        self.type = token_type
        self.position = position
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, pos={self.position})"

    def __eq__(self, other):
        return self.type == other.type and self.value == other.value and self.position == other.position
