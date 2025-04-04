from io import StringIO

import pytest
from src.lexer.lexer import Lexer
from src.lexer.position import Position
from src.lexer.token_ import TokenType,Token
from src.lexer.source import Source


@pytest.mark.parametrize("input_text, expected_tokens", [
    ("if", Token(TokenType.IF_KEYWORD, Position(1, 1))),
    ("+", Token(TokenType.PLUS_OPERATOR, Position(1, 1))),
    ("-", Token(TokenType.MINUS_OPERATOR, Position(1, 1))),
    ("*", Token(TokenType.MULTIPLICATION_OPERATOR, Position(1, 1))),
    ("/", Token(TokenType.DIVISION_OPERATOR, Position(1, 1))),
    ("==", Token(TokenType.EQUAL_OPERATOR, Position(1, 1))),
    ("while", Token(TokenType.WHILE_KEYWORD, Position(1, 1))),
    ("int", Token(TokenType.INT_KEYWORD, Position(1, 1))),
    ("x", Token(TokenType.IDENTIFIER, Position(1, 1),"x")),
])
def test_lexer_tokenize(input_text, expected_tokens):
    stream = StringIO(input_text)
    source = Source(stream)
    lexer = Lexer(source)
    tokens = lexer.next_token()
    assert tokens == expected_tokens