from io import TextIOWrapper, StringIO

from src.lexer.position import Position


class Source:
    def __init__(self, stream: TextIOWrapper | StringIO):
        self.stream = stream
        self.current_position = Position(line=1, column=1)
        self.current_char = self.stream.read(1)

    def next_char(self) -> str:
        if self.current_char == '':
            return ''

        if self.current_char == '\n':
            self.current_position.advance_line()
        else:
            self.current_position.advance_column()

        self.current_char = self.stream.read(1)

        return self.current_char

    def peek_next_char(self):
        current_index = self.stream.tell()
        next_char = self.stream.read(1)
        self.stream.seek(current_index)
        return next_char
