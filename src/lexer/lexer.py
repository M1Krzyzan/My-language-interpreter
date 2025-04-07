import sys
from io import StringIO
from typing import Optional

from src.lexer.source import Source
from src.lexer.token_ import TokenType,Token,Symbols
from src.error_manager.error_manager import ErrorManager
from src.error_manager.lexer_errors import (
    OverFlowError,
    IdentifierTooLongError,
    UnexpectedEscapeCharacterError,
    PrecisionTooBigError,
    UnclosedStringError,
    StringTooLongError,
    CommentTooLongError,
    UnknownTokenError
)

MAX_COMMENT_LEN = 3000
MAX_STRING_LEN = 3000
MAX_IDENTIFIER_LENGTH = 128
MAX_PRECISION = 15


class Lexer:
    def __init__(self, source: Source, error_handler: ErrorManager):
        self.source = source
        self.error_handler = error_handler
        self.current_char = self.source.current_char
        self.current_token_position = None

    def next_token(self):
        self._skip_white_characters()

        self.current_token_position = self.source.current_position.copy()

        if self.current_char == '':
            return Token(TokenType.ETX, self.current_token_position)

        return (self._try_build_comment()or
                self._try_build_keyword_or_identifier() or
                self._try_build_string_literal() or
                self._try_build_number_literal() or
                self._try_build_special_character() or
                self._try_build_unknown_token())

    def _skip_white_characters(self):
        while self.current_char.isspace():
            self.current_char = self.source.next_char()

    def _try_build_comment(self) -> Optional[Token]:
        if self.current_char != '#':
            return

        value = []
        self.current_char = self.source.next_char()

        while self.current_char != '\n' and self.current_char != '':
            if len(value) >= MAX_COMMENT_LEN:
               self.error_handler.add_error(CommentTooLongError(self.current_token_position))
            value.append(self.current_char)
            self.current_char = self.source.next_char()

        value = "".join(value)
        return Token(TokenType.COMMENT, self.current_token_position, value)


    def _try_build_keyword_or_identifier(self) -> Optional[Token]:
        if not self.current_char.isalpha() and self.current_char != '_':
            return None

        name = [self.current_char]
        self.current_char = self.source.next_char()

        while self.current_char.isalnum() or self.current_char == "_":
            if len(name) >= MAX_IDENTIFIER_LENGTH:
                self.error_handler.add_error(IdentifierTooLongError(self.current_token_position))
            name.append(self.current_char)
            self.current_char = self.source.next_char()

        name = "".join(name)

        token_type = Symbols.boolean_literals.get(name) or Symbols.keywords.get(name, TokenType.IDENTIFIER)

        if token_type == TokenType.IDENTIFIER:
            return Token(token_type, self.current_token_position, name)
        elif token_type == TokenType.BOOL_LITERAL:
            value = True if name == "true" else False
            return Token(token_type, self.current_token_position, value)

        return Token(token_type,self.current_token_position)

    def _try_build_string_literal(self) -> Optional[Token]:
        if self.current_char != '"':
            return None

        self.current_char = self.source.next_char()

        value = []

        while self.current_char != '"' and self.current_char != "" and self.current_char != chr(3):
            if len(value) >= MAX_STRING_LEN:
                self.error_handler.critical_error(StringTooLongError(self.current_token_position))
            if self.current_char == '\\':
                self.current_char = self.source.next_char()
                self.current_char = self._get_escaped_character()
            value.append(self.current_char)
            self.current_char = self.source.next_char()

        if self.current_char == "" or self.current_char == chr(3):
            self.error_handler.add_error(UnclosedStringError(self.current_token_position))

        value = "".join(value)

        return Token(TokenType.STRING_LITERAL, self.current_token_position, value)


    def _try_build_number_literal(self) -> Optional[Token]:
        if not self.current_char.isdecimal():
            return

        decimal_part = int(self.current_char)
        self.current_char = self.source.next_char()
        if decimal_part == 0 and self.current_char != '.':
            return Token(TokenType.INT_LITERAL, self.current_token_position, decimal_part)

        while self.current_char.isdecimal():
            if (sys.maxsize - int(self.current_char)) // 10 < decimal_part:
                self.error_handler.critical_error(OverFlowError(self.current_token_position))
            decimal_part = 10*decimal_part + int(self.current_char)
            self.current_char = self.source.next_char()

        if self.current_char != '.':
            return Token(TokenType.INT_LITERAL, self.current_token_position, decimal_part)

        next_character = self.source.peek_next_char()
        if not next_character.isdecimal():
            return Token(TokenType.INT_LITERAL, self.current_token_position, decimal_part)

        self.current_char = self.source.next_char()

        number_list = []

        while self.current_char.isdecimal():
            if len(number_list) >= MAX_PRECISION:
                self.error_handler.critical_error(PrecisionTooBigError(self.current_token_position))

            number_list.append(self.current_char)
            self.current_char = self.source.next_char()

        fractional_string = "".join(number_list)

        fractional_part = int(fractional_string)/10**(len(fractional_string))

        return Token(TokenType.FLOAT_LITERAL, self.current_token_position, decimal_part+fractional_part)

    def _try_build_special_character(self) -> Optional[Token]:
        if not Symbols.single_char.get(self.current_char) and self.current_char != '!':
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

        self.error_handler.critical_error(UnexpectedEscapeCharacterError(self.current_token_position))

    def _try_build_unknown_token(self):
        self.error_handler.add_error(UnknownTokenError(self.current_token_position))
        value = self.current_char
        self.current_char = self.source.next_char()
        return Token(TokenType.UNKNOWN, self.current_token_position, value)



if __name__ == "__main__":
    code =(
"""#COMMENT
int sum(float x, int y){ #COMMENT 
    if (x =! y){
        return x to int + y;
    }
}""")
    code_source = Source(StringIO(code))
    with ErrorManager() as error_handler:
        lexer = Lexer(code_source, error_handler)
        token = lexer.next_token()
        tokens = [token]
        while token.type != TokenType.ETX:
            token = lexer.next_token()
            tokens.append(token)
            print(token.type, end=" ")