from src.error_manager.error_manager import Error

class OverFlowError(Error):
    def __repr__(self):
        return f'LexerError: Overflow in {self.position}'

class IdentifierTooLongError(Error):
    def __repr__(self):
        return f'LexerError: Identifier oversize error in {self.position}'

class StringTooLongError(Error):
    def __repr__(self):
        return f'LexerError: String too long in {self.position}'

class CommentTooLongError(Error):
    def __repr__(self):
        return f'LexerError: Comment too long in {self.position}'

class UnexpectedEscapeCharacterError(Error):
    def __repr__(self):
        return f'LexerError: Unexpected escape character in {self.position}'

class UnclosedStringError(Error):
    def __repr__(self):
        return f'LexerError: Unclosed string in {self.position}'

class PrecisionTooBigError(Error):
    def __repr__(self):
        return f'LexerError: Precision too big in {self.position}'

class UnknownTokenError(Error):
    def __repr__(self):
        return f'LexerError: Unknown token in {self.position}'