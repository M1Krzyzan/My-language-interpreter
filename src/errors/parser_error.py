
class ParserError(Exception):
    def __init__(self, message, position):
        super().__init__(message)
        self.message = message
        self.position = position

    def __str__(self):
        return f"\033[31mParserError: {self.message} at {self.position}"