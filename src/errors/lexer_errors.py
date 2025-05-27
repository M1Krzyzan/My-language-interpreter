import sys


class LexerError(Exception):
    def __init__(self, message, position):
        super().__init__(message)
        self.message = message
        self.position = position

    def __str__(self):
        return f"\033[31mLexerError: {self.message} at {self.position}\033[0m"


class OverFlowError(LexerError):
    def __init__(self, position):
        message = f'Number too big: Should be less than or equal to {sys.maxsize} '
        super().__init__(message, position)


class IdentifierTooLongError(LexerError):
    def __init__(self, position, length_limit):
        message = 'Identifier name too long: Should be less than or equal to %d characters' % length_limit
        super().__init__(message, position)


class StringTooLongError(LexerError):
    def __init__(self, position, length_limit):
        message = 'String literal too long: Should be less than %d characters' % length_limit
        super().__init__(message, position)


class CommentTooLongError(LexerError):
    def __init__(self, position, length_limit):
        message = 'Comment too long: Should be less than %d characters' % length_limit
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
    def __init__(self, position, precision_limit):
        message = 'Precision too high: Should be less than or equal to %d digits}' % precision_limit
        super().__init__(message, position)


class UnknownTokenError(LexerError):
    def __init__(self, position, character):
        message = f'Unknown token \'{character}\''
        super().__init__(message, position)


class UnterminatedCommentBlockError(LexerError):
    def __init__(self, position):
        message = 'Unterminated comment block'
        super().__init__(message, position)