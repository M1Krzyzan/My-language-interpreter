from typing import TextIO, Tuple

from src.lexer.position import Position


class Source:
    def __init__(self, stream: TextIO):
        self.stream = stream
        self.current_position = Position(line=1, column=0)
        self.current_char = None

    def next_char(self) -> Tuple[str, Position]:
        if self.current_char == '':
            return '\x03', self.current_position

        if self.current_char == '\n':
            self.current_position.advance_line()
        else:
            self.current_position.advance_column()

        self.current_char = self.stream.read(1)
        char = self.current_char if self.current_char else '\x03'

        return char, self.current_position

    def peek_next_char(self):
        current_index = self.stream.tell()
        next_char = self.stream.read(1)
        self.stream.seek(current_index)
        return next_char
