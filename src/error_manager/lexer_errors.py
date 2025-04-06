from src.error_manager.error_manager import Error

class OverFlowError(Error):
    def __repr__(self):
        return f'LexerError: Overflow in {self.position}'