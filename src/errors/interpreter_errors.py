from src.ast.position import Position


class InterpreterError(Exception):
    def __init__(self, message: str, position: Position):
        super().__init__(message)
        self.message = message
        self.position = position

    def __str__(self):
        return f"\033[31mInterpreterError: {self.message} at {self.position}"

class MissingMainFunctionDeclaration(InterpreterError):
    def __init__(self, position: Position):
        message = "Missing main function declaration in program"
        super().__init__(message, position)

class UnknownFunctionCall(InterpreterError):
    def __init__(self, position: Position, function_name: str):
        message = f'Undeclared function call(name="{function_name}")'
        super().__init__(message, position)
