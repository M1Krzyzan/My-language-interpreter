class Position:
    def __init__(self, line: int, column: int):
        self.line = line
        self.column = column

    def advance_column(self):
        self.column += 1

    def advance_line(self):
        self.line += 1
        self.column = 1

    def copy(self):
        return Position(self.line, self.column)

    def __str__(self):
        return f"Line {self.line}, Column {self.column}"

    def __eq__(self, other):
        return self.line == other.line and self.column == other.column