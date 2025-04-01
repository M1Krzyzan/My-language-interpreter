from src.lexer.source.source import Source


class FileSource(Source):
    def __init__(self, filename: str):
        self.file = open(filename, 'r')
        self.buffer = ''
        self.eof_flag = False
        self._read_next()

    def _read_next(self):
        self.buffer = self.file.read(1)  # Read a single character at a time
        if not self.buffer:
            self.eof_flag = True
            self.buffer = '\0'

    def peek(self) -> str:
        return self.buffer

    def next(self) -> str:
        char = self.buffer
        self._read_next()
        return char

    def eof(self) -> bool:
        return self.eof_flag

    def close(self):
        self.file.close()
