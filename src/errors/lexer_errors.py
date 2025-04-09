class LexerError(Exception):
    def __init__(self, position):
        self.position = position


class OverFlowError(LexerError):
    def __repr__(self):
        return f'LexerError: Overflow in {self.position}'


class IdentifierTooLongError(LexerError):
    def __repr__(self):
        return f'LexerError: Identifier oversize error in {self.position}'


class StringTooLongError(LexerError):
    def __repr__(self):
        return f'LexerError: String too long in {self.position}'


class CommentTooLongError(LexerError):
    def __repr__(self):
        return f'LexerError: Comment too long in {self.position}'


class UnexpectedEscapeCharacterError(LexerError):
    def __repr__(self):
        return f'LexerError: Unexpected escape character in {self.position}'


class UnterminatedStringLiteralError(LexerError):
    def __repr__(self):
        return f'LexerError: Unclosed string in {self.position}'


class PrecisionTooHighError(LexerError):
    def __repr__(self):
        return f'LexerError: Precision too big in {self.position}'


class UnknownTokenError(LexerError):
    def __repr__(self):
        return f'LexerError: Unknown token in {self.position}'
