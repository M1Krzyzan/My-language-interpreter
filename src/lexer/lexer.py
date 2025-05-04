import sys
from abc import abstractmethod
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
    UnknownTokenError,
    UnterminatedCommentBlockError,
    LexerError
)

class Lexer:
    @abstractmethod
    def next_token(self) -> Token:
        pass


class DefaultLexer(Lexer):
    def __init__(
            self,
            source: Source,
            max_comment_len: int = 3000,
            max_string_len: int = 3000,
            max_identifier_len: int = 128,
            max_precision: int = 15
    ):
        self.source = source
        self._max_comment_len = max_comment_len
        self._max_identifier_len = max_identifier_len
        self._max_string_len = max_string_len
        self._max_precision = max_precision
        self.current_char, self.current_char_position = self.source.next_char()
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
            raise UnknownTokenError(self.current_token_position, self.current_char)

    def _skip_white_characters(self):
        while self.current_char.isspace():
            self.next_character()

    def _try_build_comment(self) -> Optional[Token]:
        stop_char = Symbols.comment_map.get(self.current_char)

        if not stop_char:
            return

        builder = []
        self.next_character()

        while self.current_char != stop_char and self.current_char != '\x03':
            if len(builder) >= self._max_comment_len:
                raise CommentTooLongError(self.current_char_position, self._max_comment_len)
            builder.append(self.current_char)
            self.next_character()

        if stop_char == '$' and self.current_char != '$':
            raise UnterminatedCommentBlockError(self.current_char_position)

        value = "".join(builder)
        self.next_character()

        return Token(TokenType.COMMENT, self.current_token_position, value)

    def _try_build_keyword_or_identifier(self) -> Optional[Token]:
        if not (self.current_char.isalpha() or self.current_char == "_"):
            return

        builder = [self.current_char]
        self.next_character()

        while self.current_char.isalnum() or self.current_char == "_":
            if len(builder) >= self._max_identifier_len:
                raise IdentifierTooLongError(self.current_char_position, self._max_identifier_len)
            builder.append(self.current_char)
            self.next_character()

        name_str = "".join(builder)

        token_type = Symbols.keywords.get(name_str, TokenType.IDENTIFIER)

        return Token(token_type, self.current_token_position, name_str)

    def _try_build_string_literal(self) -> Optional[Token]:
        if self.current_char != '"':
            return None

        self.next_character()

        value = []

        while self.current_char != '"' and self.current_char != '\x03' and self.current_char != "\n":
            if len(value) >= self._max_string_len:
                raise StringTooLongError(self.current_char_position, self._max_string_len)

            if self.current_char == '\\':
                self.next_character()
                self.current_char = self._get_escaped_character()

            value.append(self.current_char)
            self.next_character()

        if self.current_char == "\n" or self.current_char == '\x03':
            raise UnterminatedStringLiteralError(self.current_char_position)

        self.next_character()
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
        self.next_character()

        if decimal_part == 0 and self.current_char != '.':
            return 0

        while self.current_char.isdecimal():
            if (sys.maxsize - int(self.current_char)) // 10 < decimal_part:
                raise OverFlowError(self.current_char_position)

            decimal_part = 10 * decimal_part + int(self.current_char)
            self.next_character()

        return decimal_part

    def _parse_fractional_part(self) -> Optional[float]:
        next_character = self.source.peek_next_char()
        if not next_character.isdecimal():
            return None

        self.next_character()
        fractional_part = 0
        digits = 0
        while self.current_char.isdecimal():
            if digits >= self._max_precision:
                raise PrecisionTooHighError(self.current_char_position, self._max_precision)
            fractional_part = 10 * fractional_part + int(self.current_char)
            self.next_character()
            digits += 1

        return fractional_part / 10 ** digits

    def _try_build_special_character(self) -> Optional[Token]:
        if not Symbols.single_char.get(self.current_char):
            return

        first_char = self.current_char
        self.next_character()
        if token_type := Symbols.double_char.get(first_char + self.current_char):
            self.next_character()
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

        raise UnexpectedEscapeCharacterError(self.current_char_position, f"\\{self.current_char}")
    
    def next_character(self) -> None:
        self.current_char, self.current_char_position = self.source.next_char()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python lexer.py <filename>")
        sys.exit(1)

    with open(sys.argv[1], "r") as file:
        code_source = Source(file)
        lexer = DefaultLexer(code_source)
        token_ = lexer.next_token()

        try:
            while token_.type != TokenType.ETX:
                print(token_)
                token_ = lexer.next_token()
            print(token_)
        except LexerError as e:
            print(e)
