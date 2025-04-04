from io import StringIO

from src.lexer.source import Source
from src.lexer.token_ import TokenType,Token,Symbols

BEGIN_COMMENT = '#'
MAX_COMMENT_LEN = 3000
MAX_IDENTIFIER_LENGTH = 125

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

        return (self._try_build_comment()
                or self._try_build_keyword_or_identifier()
                or self._try_build_string_literal()
                or self._try_build_boolean_literal()
                or self._try_build_number_literal()
                or self._try_build_special_character())

    def _skip_white_characters(self):
        while self.current_char.isspace():
            self.current_char = self.source.next_char()

    def _try_build_comment(self):
        if self.current_char != '#':
            return

        value = []

        while self.current_char != '\n':
            self.current_char = self.source.next_char()
            if len(value) > MAX_COMMENT_LEN:
                raise LexerError("Comment too long", self.current_token_position)
            value.append(self.current_char)

        value = "".join(value)
        return Token(TokenType.COMMENT, self.current_token_position, value)


    def _try_build_keyword_or_identifier(self):
        if not self.current_char.isalpha() and self.current_char != '_':
            return None

        name = [self.current_char]
        self.current_char = self.source.next_char()

        while self.current_char.isalnum() or self.current_char == "_":
            if len(name) > MAX_IDENTIFIER_LENGTH:
                return LexerError("Identifier too long", self.current_token_position)
            name.append(self.current_char)
            self.current_char = self.source.next_char()

        name = "".join(name)
        token_type = Symbols.keywords.get(name, TokenType.IDENTIFIER)
        if token_type == TokenType.IDENTIFIER:
            return Token(token_type, self.current_token_position, name)
        else:
            return Token(token_type,self.current_token_position)

    def _try_build_string_literal(self):
        pass

    def _try_build_boolean_literal(self):
        pass

    def _try_build_number_literal(self):
        pass

    def _try_build_special_character(self):
        if not Symbols.single_char.get(self.current_char) and self.current_char!= '!':
            return

        first_char = self.current_char
        self.current_char = self.source.next_char()

        if token_type := Symbols.double_char.get(first_char + self.current_char):
            return Token(token_type, self.current_token_position)
        elif token_type := Symbols.single_char.get(first_char):
            return Token(token_type, self.current_token_position)



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