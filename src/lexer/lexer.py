import sys
from io import StringIO
from typing import Optional

from src.lexer.source import Source
from src.lexer.token_ import TokenType, Token, Symbols
from src.errors.lexer_errors import (
    OverFlowError,
    IdentifierTooLongError,
    UnexpectedEscapeCharacterError,
    PrecisionTooHighError,
    UnterminatedStringLiteralError,
    StringTooLongError,
    CommentTooLongError,
    UnknownTokenError
)

MAX_COMMENT_LEN = 3000
MAX_STRING_LEN = 3000
MAX_IDENTIFIER_LENGTH = 128
MAX_PRECISION = 15


class Lexer:
    def __init__(self, source: Source):
        self.source = source
        self.current_char = self.source.next_char()
        self.current_token_position = None

    def next_token(self):
        self._skip_white_characters()

        self.current_token_position = self.source.current_position.copy()

        if self.current_char == '\x03':
            return Token(TokenType.ETX, self.current_token_position)

        if token := (
                self._try_build_comment() or
                self._try_build_keyword_or_identifier() or
                self._try_build_string_literal() or
                self._try_build_number_literal() or
                self._try_build_special_character()
        ):
            return token
        else:
            raise UnknownTokenError(self.current_token_position)

    def _skip_white_characters(self):
        while self.current_char.isspace():
            self.current_char = self.source.next_char()

    def _try_build_comment(self) -> Optional[Token]:
        if self.current_char != '#':
            return

        value = []
        self.current_char = self.source.next_char()

        while self.current_char != '\n' and self.current_char != '\x03':
            if len(value) >= MAX_COMMENT_LEN:
                raise CommentTooLongError(self.current_token_position)
            value.append(self.current_char)
            self.current_char = self.source.next_char()

        value = "".join(value)
        return Token(TokenType.COMMENT, self.current_token_position, value)

    def _try_build_keyword_or_identifier(self) -> Optional[Token]:
        if not (self.current_char.isalpha() or self.current_char == "_"):
            return

        builder = [self.current_char]
        self.current_char = self.source.next_char()

        while self.current_char.isalnum() or self.current_char == "_":
            if len(builder) >= MAX_IDENTIFIER_LENGTH:
                raise IdentifierTooLongError(self.current_token_position)
            builder.append(self.current_char)
            self.current_char = self.source.next_char()

        name_str = "".join(builder)

        token_type = (Symbols.boolean_literals.get(name_str) or
                      Symbols.keywords.get(name_str, TokenType.IDENTIFIER))

        if token_type == TokenType.IDENTIFIER:
            return Token(token_type, self.current_token_position, name_str)
        elif token_type == TokenType.BOOLEAN_LITERAL:
            value = name_str == "true"
            return Token(token_type, self.current_token_position, value)

        return Token(token_type, self.current_token_position)

    def _try_build_string_literal(self) -> Optional[Token]:
        if self.current_char != '"':
            return None

        self.current_char = self.source.next_char()

        value = []

        while self.current_char != '"' and self.current_char != "" and self.current_char != '\x03':
            if len(value) >= MAX_STRING_LEN:
                raise StringTooLongError(self.current_token_position)

            if self.current_char == '\\':
                self.current_char = self.source.next_char()
                self.current_char = self._get_escaped_character()

            value.append(self.current_char)
            self.current_char = self.source.next_char()

        if self.current_char == "" or self.current_char == '\x03':
            raise UnterminatedStringLiteralError(self.current_token_position)

        value = "".join(value)

        return Token(TokenType.STRING_LITERAL, self.current_token_position, value)

    def _try_build_number_literal(self) -> Optional[Token]:
        if not self.current_char.isdecimal():
            return

        decimal_part = self._parse_integer_part()

        if self.current_char != '.':
            return Token(TokenType.INT_LITERAL, self.current_token_position, decimal_part)

        fractional_part = self._parse_fractional_part()
        if fractional_part is None:
            return Token(TokenType.INT_LITERAL, self.current_token_position, decimal_part)

        return Token(TokenType.FLOAT_LITERAL, self.current_token_position, decimal_part + fractional_part)

    def _parse_integer_part(self) -> int:
        decimal_part = int(self.current_char)
        self.current_char = self.source.next_char()

        if decimal_part == 0 and self.current_char != '.':
            return 0

        while self.current_char.isdecimal():
            if (sys.maxsize - int(self.current_char)) // 10 < decimal_part:
                raise OverFlowError(self.current_token_position)

            decimal_part = 10 * decimal_part + int(self.current_char)
            self.current_char = self.source.next_char()

        return decimal_part

    def _parse_fractional_part(self) -> Optional[float]:
        next_character = self.source.peek_next_char()
        if not next_character.isdecimal():
            return None

        self.current_char = self.source.next_char()
        builder = []

        while self.current_char.isdecimal():
            if len(builder) >= MAX_PRECISION:
                raise PrecisionTooHighError(self.current_token_position)
            builder.append(self.current_char)
            self.current_char = self.source.next_char()

        fraction_digits = "".join(builder)
        return int(fraction_digits) / 10 ** len(fraction_digits)

    def _try_build_special_character(self) -> Optional[Token]:
        if not Symbols.single_char.get(self.current_char):
            return

        first_char = self.current_char
        self.current_char = self.source.next_char()

        if token_type := Symbols.double_char.get(first_char + self.current_char):
            return Token(token_type, self.current_token_position)
        elif token_type := Symbols.single_char.get(first_char):
            return Token(token_type, self.current_token_position)

    def _get_escaped_character(self) -> str:
        escaped_characters_map = {
            '\\': '\\',
            't': '\t',
            'n': '\n',
            '"': '\"'
        }

        if escaped_character := escaped_characters_map.get(self.current_char):
            return escaped_character

        raise UnexpectedEscapeCharacterError(self.current_token_position)


if __name__ == "__main__":
    code = (
        """#COMMENT
        int sum(float x, int y){ #COMMENT 
            if (x =! y){
                return x to int + y;
            }
        }""")
    code_source = Source(StringIO(code))
    lexer = Lexer(code_source)
    token_ = lexer.next_token()
    tokens = [token_]
    while token_.type != TokenType.ETX:
        token_ = lexer.next_token()
        tokens.append(token_)
        print(token_.type, end=" ")
