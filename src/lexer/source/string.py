from src.lexer.source.source import Source


class StringSource(Source):
    def __init__(self, data: str):
        self.data = data
        self.pos = 0

    def peek(self) -> str:
        if self.eof():
            return '\0'  # Null character for EOF
        return self.data[self.pos]

    def next(self) -> str:
        if self.eof():
            return '\0'
        char = self.data[self.pos]
        self.pos += 1
        return char

    def eof(self) -> bool:
        return self.pos >= len(self.data)
