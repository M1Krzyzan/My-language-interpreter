import sys
from io import StringIO

import pytest

from src.error_manager.error_manager import ErrorManager
from src.error_manager.lexer_errors import OverFlowError
from src.lexer.lexer import Lexer, LexerError
from src.lexer.position import Position
from src.lexer.token_ import TokenType,Token
from src.lexer.source import Source


@pytest.mark.parametrize("input_text, expected_tokens", [
    ("if", Token(TokenType.IF_KEYWORD, Position(1, 1))),
    ("elif", Token(TokenType.ELIF_KEYWORD, Position(1, 1))),
    ("else", Token(TokenType.ELSE_KEYWORD, Position(1, 1))),
    ("while", Token(TokenType.WHILE_KEYWORD, Position(1, 1))),
    ("return", Token(TokenType.RETURN_KEYWORD, Position(1, 1))),
    ("break", Token(TokenType.BREAK_KEYWORD, Position(1, 1))),
    ("continue", Token(TokenType.CONTINUE_KEYWORD, Position(1, 1))),
    ("to", Token(TokenType.TO_KEYWORD, Position(1, 1))),
    ("void", Token(TokenType.VOID_KEYWORD, Position(1, 1))),
    ("int", Token(TokenType.INT_KEYWORD, Position(1, 1))),
    ("float", Token(TokenType.FLOAT_KEYWORD, Position(1, 1))),
    ("string", Token(TokenType.STRING_KEYWORD, Position(1, 1))),
    ("bool", Token(TokenType.BOOL_KEYWORD, Position(1, 1))),
    ("Exception", Token(TokenType.EXCEPTION_KEYWORD, Position(1, 1))),
    ("while", Token(TokenType.WHILE_KEYWORD, Position(1, 1))),
    ("or", Token(TokenType.OR_OPERATOR, Position(1, 1))),
    ("and", Token(TokenType.AND_OPERATOR, Position(1, 1))),
    ("not", Token(TokenType.NEGATION_OPERATOR, Position(1, 1))),
    (".", Token(TokenType.DOT, Position(1, 1))),
    (",", Token(TokenType.COMMA, Position(1, 1))),
    (":", Token(TokenType.COLON, Position(1, 1))),
    (";", Token(TokenType.SEMICOLON, Position(1, 1))),
    ("+", Token(TokenType.PLUS_OPERATOR, Position(1, 1))),
    ("-", Token(TokenType.MINUS_OPERATOR, Position(1, 1))),
    ("*", Token(TokenType.MULTIPLICATION_OPERATOR, Position(1, 1))),
    ("/", Token(TokenType.DIVISION_OPERATOR, Position(1, 1))),
    ("%", Token(TokenType.MODULO_OPERATOR, Position(1, 1))),
    ("<", Token(TokenType.LESS_THAN_OPERATOR, Position(1, 1))),
    ("<=", Token(TokenType.LESS_THAN_OR_EQUAL_OPERATOR, Position(1, 1))),
    (">", Token(TokenType.GREATER_THAN_OPERATOR, Position(1, 1))),
    (">=", Token(TokenType.GREATER_THAN_OR_EQUAL_OPERATOR, Position(1, 1))),
    ("==", Token(TokenType.EQUAL_OPERATOR, Position(1, 1))),
    ("!=", Token(TokenType.NOT_EQUAL_OPERATOR, Position(1, 1))),
    ("=", Token(TokenType.ASSIGNMENT, Position(1, 1))),
    ("xyz_4", Token(TokenType.IDENTIFIER, Position(1, 1),"xyz_4")),
    ('"text\\\\ \\\"\\t\\n"', Token(TokenType.STRING_LITERAL, Position(1, 1),"text\\ \"\t\n")),
    ("356", Token(TokenType.INT_LITERAL, Position(1, 1), 356)),
    ("5.135", Token(TokenType.FLOAT_LITERAL, Position(1, 1), 5.135)),
    ("true", Token(TokenType.BOOL_LITERAL, Position(1, 1), True)),
    ("# this is comment\n", Token(TokenType.COMMENT, Position(1, 1), " this is comment")),
])
def test_basic_tokens(input_text, expected_tokens):
    stream = StringIO(input_text)
    source = Source(stream)
    lexer = Lexer(source)
    tokens = lexer.next_token()
    assert tokens == expected_tokens

def test_position_tracking():
    input_code = """
                
          x
        
        
       =
          
             21
        \t
        \r\n;
        \n
        """
    stream = StringIO(input_code)
    source = Source(stream)
    lexer = Lexer(source)

    token = lexer.next_token()
    tokens = [token]
    while token.type != TokenType.EOT:
        token = lexer.next_token()
        tokens.append(token)
    assert tokens == [Token(TokenType.IDENTIFIER, Position(3, 11), "x"),
                      Token(TokenType.ASSIGNMENT, Position(6, 8)),
                      Token(TokenType.INT_LITERAL, Position(8, 14), 21),
                      Token(TokenType.SEMICOLON, Position(11, 1)),
                      Token(TokenType.EOT, Position(14, 9))]

def test_should_not_allow_identifiers_longer_than_128_characters():
    input_code = "x"*129
    stream = StringIO(input_code)
    source = Source(stream)
    lexer = Lexer(source)
    with pytest.raises(LexerError) as err:
        lexer.next_token()

    assert str(err.value) == "LexerError: Identifier too long, Line 1, Column 1"


def test_should_not_allow_numbers_to_be_too_big():
    input_code = str(sys.maxsize+1)
    stream = StringIO(input_code)
    source = Source(stream)
    with ErrorManager() as error_handler:
        lexer = Lexer(source, error_handler)
        lexer.next_token()
    assert len(error_handler._errors) == 1
    assert error_handler._errors[0] == OverFlowError(Position(1,1))