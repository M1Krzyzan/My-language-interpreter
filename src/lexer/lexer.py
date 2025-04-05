from io import StringIO
from typing import Optional

from src.lexer.source import Source
from src.lexer.token_ import TokenType,Token,Symbols

BEGIN_COMMENT = '#'
MAX_COMMENT_LEN = 3000
MAX_IDENTIFIER_LENGTH = 125
MAX_STRING_LEN = 3000
class Lexer:
    def __init__(self, source: Source):
        self.source = source
        self.current_char = self.source.current_char
        self.current_token_position = None

    def next_token(self):
        self._skip_white_characters()

        self.current_token_position = self.source.current_position.copy()

        if self.current_char == '':
            return Token(TokenType.EOT, self.current_token_position)

        return (self._try_build_comment()or
                self._try_build_keyword_or_identifier() or
                self._try_build_string_literal() or
                self._try_build_number_literal() or
                self._try_build_special_character())

    def _skip_white_characters(self):
        while self.current_char.isspace():
            self.current_char = self.source.next_char()

    def _try_build_comment(self) -> Optional[Token]:
        if self.current_char != '#':
            return

        value = []
        self.current_char = self.source.next_char()

        while self.current_char != '\n':
            if len(value) > MAX_COMMENT_LEN:
                raise LexerError("Comment too long", self.current_token_position)
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
            if len(name) > MAX_IDENTIFIER_LENGTH:
                raise LexerError("Identifier too long", self.current_token_position)
            name.append(self.current_char)
            self.current_char = self.source.next_char()

        name = "".join(name)

        token_type = Symbols.keywords.get(name, TokenType.IDENTIFIER)

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

        while self.current_char != '"' or self.current_char == "":
            if len(value) > MAX_STRING_LEN:
                raise LexerError("String literal too long", self.current_token_position)
            if self.current_char == '\\':
                self.current_char = self.source.next_char()
                self.current_char = self._get_escaped_character()
            value.append(self.current_char)
            self.current_char = self.source.next_char()

        if self.current_char == "":
            raise LexerError("Unclosed string literal", self.current_token_position)

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
            try:
                decimal_part = 10*decimal_part + int(self.current_char)
            except OverflowError:
                raise LexerError("Number too large", self.current_token_position)
            self.current_char = self.source.next_char()

        if self.current_char != '.':
            return Token(TokenType.INT_LITERAL, self.current_token_position, decimal_part)

        next_character = self.source.peek_next_char()
        if not next_character.isdecimal():
            return Token(TokenType.INT_LITERAL, self.current_token_position, decimal_part)

        self.current_char = self.source.next_char()

        number_list = []

        while self.current_char.isdecimal():
            number_list.append(self.current_char)
            self.current_char = self.source.next_char()

        fractional_string = "".join(number_list)

        try:
            fractional_part = int(fractional_string)/10**(len(fractional_string))
        except OverflowError:
            raise LexerError("Number too large", self.current_token_position)

        return Token(TokenType.FLOAT_LITERAL, self.current_token_position, decimal_part+fractional_part)

    def _try_build_special_character(self) -> Optional[Token]:
        if not Symbols.single_char.get(self.current_char) and self.current_char!= '!':
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
        try:
            escaped_character = escaped_characters_map[self.current_char]
        except KeyError:
            raise LexerError("Invalid escape character", self.current_token_position)

        return escaped_character



class LexerError(Exception):
    pass


if __name__ == "__main__":
    code =(
"""#COMMENT
int sum(float x, int y){ #COMMENT 
    if (x =! y){
        return x to int + y;
    }
}""")
    code_source = Source(StringIO(code))
    lexer = Lexer(code_source)
    token = lexer.next_token()
    while token.type != TokenType.EOT:
        token = lexer.next_token()
        print(token.type, end=" ")