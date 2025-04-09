import sys
from io import StringIO
import pytest

from src.errors.lexer_errors import (
    OverFlowError,
    IdentifierTooLongError,
    StringTooLongError,
    UnexpectedEscapeCharacterError,
    PrecisionTooHighError,
    CommentTooLongError,
    UnterminatedStringLiteralError, UnterminatedCommentBlockError
)
from src.lexer.lexer import Lexer
from src.lexer.position import Position
from src.lexer.source import Source
from src.lexer.token_ import TokenType, Token, Symbols


def tokenize(input_text: str) -> Token:
    stream = StringIO(input_text, None)
    source = Source(stream)
    lexer = Lexer(source)
    return lexer.next_token()


@pytest.mark.parametrize(
    "input_text, expected_tokens", [
        (text, Token(token_type, Position(1, 1)),)
        for text, token_type in Symbols.keywords.items()
    ]
)
def test_build_keyword_tokens(input_text, expected_tokens):
    token = tokenize(input_text)
    assert token == expected_tokens


@pytest.mark.parametrize(
    "input_text, expected_tokens", [
        (text, Token(token_type, Position(1, 1)),)
        for text, token_type in {**Symbols.single_char, **Symbols.double_char}.items()
    ]
)
def test_build_operator_tokens(input_text, expected_tokens):
    token = tokenize(input_text)
    assert token == expected_tokens


@pytest.mark.parametrize("input_text, expected_tokens", [
    (name, Token(TokenType.IDENTIFIER, Position(1, 1), name))
    for name in ["x", "xyz", "_xyz", "_x_y_z", "x33", "x_3_", "_1", "__", "intx", "for_", "if1"]
])
def test_build_identifier_token(input_text, expected_tokens):
    token = tokenize(input_text)
    assert token == expected_tokens


@pytest.mark.parametrize("input_text", ["x" * 129])
def test_should_not_allow_identifiers_to_be_too_long(input_text):
    stream = StringIO(input_text, None)
    source = Source(stream)
    lexer = Lexer(source)

    with pytest.raises(IdentifierTooLongError):
        lexer.next_token()


@pytest.mark.parametrize("input_text, expected_tokens", [
    (string_in, Token(TokenType.STRING_LITERAL, Position(1, 1), string_value))
    for string_in, string_value in {
        "\"x y z\"": "x y z",
        "\"text\\\\ \\\"\\t\\n\"": "text\\ \"\t\n",
        "\"aa\\n x \\t\\nbb\"": "aa\n x \t\nbb",
        "\"\\\\\"": "\\",
        "\"\\\"  \\\"\\n \\\\ x \"": "\"  \"\n \\ x ",
    }.items()
])
def test_build_string_literal_token(input_text, expected_tokens):
    token = tokenize(input_text)
    assert token == expected_tokens


@pytest.mark.parametrize("input_text", ["\"" + "x" * 3001 + "\""])
def test_should_not_allow_string_literals_to_be_too_long(input_text):
    stream = StringIO(input_text, None)
    source = Source(stream)
    lexer = Lexer(source)

    with pytest.raises(StringTooLongError):
        lexer.next_token()


@pytest.mark.parametrize("input_text,", ["\"text", "\"text\n\"", "\"text\x03"])
def test_should_print_error_for_unclosed_string_literals(input_text):
    stream = StringIO(input_text, None)
    source = Source(stream)
    lexer = Lexer(source)

    with pytest.raises(UnterminatedStringLiteralError):
        lexer.next_token()


@pytest.mark.parametrize("input_text", ["\"\\n\\t\\a\""])
def test_should_not_allow_unknown_escaped_characters(input_text):
    stream = StringIO(input_text, None)
    source = Source(stream)
    lexer = Lexer(source)

    with pytest.raises(UnexpectedEscapeCharacterError):
        lexer.next_token()


@pytest.mark.parametrize("input_text, expected_tokens", [
    (number_in, Token(TokenType.INT_LITERAL, Position(1, 1), number_value))
    for number_in, number_value in {
        "0": 0,
        "8": 8,
        "3536": 3536,
        "234.notAnumber": 234,
        str(sys.maxsize): sys.maxsize,
    }.items()
])
def test_build_int_literal_token(input_text, expected_tokens):
    token = tokenize(input_text)
    assert token == expected_tokens


@pytest.mark.parametrize("input_text, expected_tokens", [
    ("00143", [
        Token(TokenType.INT_LITERAL, Position(1, 1), 0),
        Token(TokenType.INT_LITERAL, Position(1, 2), 0),
        Token(TokenType.INT_LITERAL, Position(1, 3), 143),
    ])
])
def test_each_leading_zero_is_separated_as_token(input_text, expected_tokens):
    stream = StringIO(input_text, None)
    source = Source(stream)
    lexer = Lexer(source)
    tokens = []

    while (token := lexer.next_token()).type != TokenType.ETX:
        tokens.append(token)

    assert len(tokens) == len(expected_tokens)
    assert tokens == expected_tokens


@pytest.mark.parametrize("input_text", [str(sys.maxsize + 1), f"{sys.maxsize + 0.1:.1f}"])
def test_number_size_exceeded(input_text):
    stream = StringIO(input_text, None)
    source = Source(stream)
    lexer = Lexer(source)

    with pytest.raises(OverFlowError):
        lexer.next_token()


@pytest.mark.parametrize("input_text, expected_tokens", [
    (number_in, Token(TokenType.FLOAT_LITERAL, Position(1, 1), number_value))
    for number_in, number_value in {
        "0.0": 0.0,
        "0.1": 0.1,
        "0.0008": 0.0008,
        "15231.53245": 15231.53245
    }.items()
])
def test_build_float_literal_token(input_text, expected_tokens):
    token = tokenize(input_text)
    assert token == expected_tokens


@pytest.mark.parametrize("input_text", ["0." + "0" * 15 + "9"])
def test_precision_limit_exceeded(input_text):
    stream = StringIO(input_text, None)
    source = Source(stream)
    lexer = Lexer(source)

    with pytest.raises(PrecisionTooHighError):
        lexer.next_token()


@pytest.mark.parametrize("input_text, expected_tokens", [
    ("true", Token(TokenType.BOOLEAN_LITERAL, Position(1, 1), True)),
    ("false", Token(TokenType.BOOLEAN_LITERAL, Position(1, 1), False))
])
def test_build_boolean_literal_token(input_text, expected_tokens):
    token = tokenize(input_text)
    assert token == expected_tokens


@pytest.mark.parametrize("input_text, expected_tokens", [
    (text_in, Token(TokenType.COMMENT, Position(1, 1), text_value)) for text_in, text_value in {
        "# this is comment\n text": " this is comment",
        "#this is comment without new line": "this is comment without new line",
        "# comment with ASCII 3\x03": " comment with ASCII 3"
    }.items()
])
def test_build_single_line_comment_token(input_text, expected_tokens):
    token = tokenize(input_text)
    assert token == expected_tokens


@pytest.mark.parametrize("input_text, expected_tokens", [
    (text_in, Token(TokenType.COMMENT, Position(1, 1), text_value)) for text_in, text_value in {
        "$COMMENT\nBLOCK\nWITH\n4 LINES$": "COMMENT\nBLOCK\nWITH\n4 LINES"
    }.items()
])
def test_build_block_comment_token(input_text, expected_tokens):
    token = tokenize(input_text)
    assert token == expected_tokens


@pytest.mark.parametrize("input_text", [
    "$COMMENT\nBLOCK\nWITH\n4 LINES", "$COMMENT\nBLOCK\nWITH\n4 LINES\x03"
])
def test_should_raise_exception_for_unterminated_block_comment(input_text):
    stream = StringIO(input_text, None)
    source = Source(stream)
    lexer = Lexer(source)

    with pytest.raises(UnterminatedCommentBlockError):
        lexer.next_token()


@pytest.mark.parametrize("input_text", ["#" + "a" * 3001])
def test_should_not_allow_comments_to_be_too_long(input_text):
    stream = StringIO(input_text, None)
    source = Source(stream)
    lexer = Lexer(source)

    with pytest.raises(CommentTooLongError):
        lexer.next_token()


@pytest.mark.parametrize("input_text, expected_token", [
    ("", Token(TokenType.ETX, Position(1, 1)),),
    ("\n", Token(TokenType.ETX, Position(2, 1)),),
    ("text ", Token(TokenType.ETX, Position(1, 6)),)
])
def test_build_end_of_text_token(input_text, expected_token):
    stream = StringIO(input_text, None)
    source = Source(stream)

    lexer = Lexer(source)
    token = lexer.next_token()
    while token.type != TokenType.ETX:
        token = lexer.next_token()

    assert token == expected_token


@pytest.mark.parametrize("input_text, expected_token", [
    ("text", Token(TokenType.ETX, Position(1, 5)),)
])
def test_should_always_give_end_of_text_token_after_end_of_text(input_text, expected_token):
    stream = StringIO(input_text, None)
    source = Source(stream)

    lexer = Lexer(source)
    lexer.next_token()  # Skip string literal token
    for _ in range(10):
        token = lexer.next_token()
        assert token == expected_token


@pytest.mark.parametrize("input_text, expected_tokens", [
    (text, [
        Token(TokenType.IDENTIFIER, Position(3, 11), "x"),
        Token(TokenType.ASSIGNMENT, Position(6, 8)),
        Token(TokenType.INT_LITERAL, Position(8, 14), 21),
        Token(TokenType.SEMICOLON, Position(11, 1)),
        Token(TokenType.ETX, Position(14, 5)),
    ]) for text in [
        "\n\n          x\n\n\n       =\n\n             21\n\t\n\n;\n\n\n    ",
        "\r\n\r\n          x\r\n\r\n\r\n       =\r\n\r\n             21\r\n\t\r\n\r\n;\r\n\r\n\r\n    ",
    ]
])
def test_position_tracking(input_text, expected_tokens):
    stream = StringIO(input_text, None)
    source = Source(stream)

    lexer = Lexer(source)
    token = lexer.next_token()
    tokens = [token]
    while token.type != TokenType.ETX:
        token = lexer.next_token()
        tokens.append(token)

    assert len(tokens) == len(expected_tokens)
    assert tokens == expected_tokens
