from src.ast.position import Position
from src.ast.types import Type


class InterpreterError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
        # self.position = position

    def __str__(self):
        return f"\033[31mInterpreterError: {self.message} at"


class MissingMainFunctionDeclaration(InterpreterError):
    def __init__(self, position: Position):
        message = "Missing main function declaration in program"
        super().__init__(message)


class UnknownFunctionCall(InterpreterError):
    def __init__(self, function_name: str):
        message = f'Undeclared function call(name="{function_name}")'
        super().__init__(message)


class WrongExpressionType(InterpreterError):
    def __init__(self, exp_type):
        message = f'Unknown expression type {exp_type}")'
        super().__init__(message)


class WrongCastType(InterpreterError):
    def __init__(self, exp_type: Type):
        message = f'Unknown target type {exp_type}")'
        super().__init__(message)


class DivisionByZeroError(InterpreterError):
    def __init__(self):
        message = f'Cant divide by zero")'
        super().__init__(message)


class NotMatchingTypesInBinaryExpression(InterpreterError):
    def __init__(self, left_type: Type, right_type: Type):
        message = f'Not matching types in binary operation "{left_type}"!="{right_type}")'
        super().__init__(message)


class InvalidReturnTypeException(InterpreterError):
    def __init__(self, value_type: Type, function_type: Type):
        message = f'Type mismatch in return value: expected "{function_type}", but got "{value_type}".'
        super().__init__(message)

class RecursionTooDeepError(InterpreterError):
    def __init__(self):
        message = f'Recursion limit reached'
        super().__init__(message)

class UndefinedExceptionError(InterpreterError):
    def __init__(self, exception_name: str):
        message = f'Undefined exception "{exception_name}"'
        super().__init__(message)

class LoopControlOutsideLoopError(InterpreterError):
    def __init__(self, name: str):
        message = f'{name} loop control statement outside loop'
        super().__init__(message)

class UndefinedAttributeError(InterpreterError):
    def __init__(self, name: str):
        message = f'Undefined attribute "{name}"'
        super().__init__(message)

class NoLastResultError(InterpreterError):
    def __init__(self):
        message = f'There is no value to return"'
        super().__init__(message)

class WRongNumberOfArguments(InterpreterError):
    def __init__(self, name: str):
        message = f'Wrong number of arguments in "{name}"'
        super().__init__(message)
