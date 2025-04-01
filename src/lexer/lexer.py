from src.lexer.source.source import Source
from src.lexer.source.string import StringSource

class Lexer:
    def __init__(self, source: Source):
        self.source = source
        self.column = 0
        self.row = 0

    def get_token(self):
        while not self.source.eof():
            char = self.source.peek()
            if char.isspace():
                self.source.next()
                continue  # Skip whitespace

            return self.source.next()  # Return the next meaningful character

        return None


if __name__ == "__main__":
    code_source = StringSource("hello world")
    lexer = Lexer(code_source)
