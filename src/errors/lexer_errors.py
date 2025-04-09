class LexerError(Exception):
    def __init__(self, message, position):
        super().__init__(message)
        self.message = message
        self.position = position

    def __str__(self):
        return f"\033[31mLexerError: {self.message}, {self.position}"


class OverFlowError(LexerError):
    def __init__(self, position):
        message = 'Number too big'
        super().__init__(message, position)


class IdentifierTooLongError(LexerError):
    def __init__(self, position):
        message = 'Identifier name too long'
        super().__init__(message, position)


class StringTooLongError(LexerError):
    def __init__(self, position):
        message = 'String literal too long'
        super().__init__(message, position)


class CommentTooLongError(LexerError):
    def __init__(self, position):
        message = 'Comment too long'
        super().__init__(message, position)


class UnexpectedEscapeCharacterError(LexerError):
    def __init__(self, position, character):
        message = f'Unexpected escape character \'{character}\''
        super().__init__(message, position)


class UnterminatedStringLiteralError(LexerError):
    def __init__(self, position):
        message = 'Unterminated string literal'
        super().__init__(message, position)


class PrecisionTooHighError(LexerError):
    def __init__(self, position):
        message = f'Precision too high'
        super().__init__(message, position)


class UnknownTokenError(LexerError):
    def __init__(self, position, character):
        message = f'Unknown token \'{character}\''
        super().__init__(message, position)


class UnterminatedCommentBlockError(LexerError):
    def __init__(self, position):
        message = 'Unterminated comment block'
        super().__init__(message, position)