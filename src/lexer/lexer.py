from src.lexer.source.source import Source
from src.lexer.source.string import StringSource
from src.lexer.token_ import TokenType,Token,Symbols

BEGIN_COMMENT = '#'


class Lexer:
    def __init__(self, source: Source):
        self.source = source
        self.current_char = self.source.next()
        self.column = 1
        self.row = 1

    def next_token(self):
        self._skip_white_characters_and_comments()

        if self.current_char == '\uFFFF':
            return Token(TokenType.EOF, (self.column, self.row), None)

        return (self._process_keyword_or_identifier()
                or self._process_string_literal()
                or self._process_boolean_literal()
                or self._process_number_literal()
                or self._special_character())

    def _skip_white_characters_and_comments(self):
        while self.current_char.isspace() or self.current_char == BEGIN_COMMENT:
            if self.current_char == BEGIN_COMMENT:
                while self.current_char != '\n':
                    self.current_char = self.source.next()
                    self.column += 1
            self.current_char = self.source.next()
            if self.current_char != '\n':
                self.column = 1
                self.row += 1

    def _process_keyword_or_identifier(self):
        if not self.current_char.isalpha() and self.current_char != '_':
            return None # I don't know whether I should raise error here or just return None

        name = []
        while self.current_char.isalpha() or self.current_char == "_" or self.current_char.isdigit():
            name.append(self.current_char)
            self.current_char = self.source.next()
            self.column += 1
        name = "".join(name)

        return Token(Symbols.keywords.get(name, TokenType.IDENTIFIER),(self.column, self.row), name)

    def _process_string_literal(self):
        pass

    def _process_boolean_literal(self):
        pass

    def _process_number_literal(self):
        pass

    def _special_character(self):
        pass


if __name__ == "__main__":
    code =(
"""#COMMENT
int sum(float x, int y){ #COMMENT 
  return x to int + y;
}""")
    code_source = StringSource(code)
    lexer = Lexer(code_source)
    lexer.next_token()
