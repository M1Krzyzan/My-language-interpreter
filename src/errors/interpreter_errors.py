from src.ast.position import Position
from src.ast.types import Type


class InterpreterError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"\033[31mInterpreterError: {self.message}\033[0m"


class MissingMainFunctionDeclaration(InterpreterError):
    def __init__(self):
        message = "Missing main function declaration in program"
        super().__init__(message)


class FailedValueAssigmentError(InterpreterError):
    def __init__(self, name: str, position: Position):
        message = f'Failed to assign value to variable "{name}" at {position}'
        super().__init__(message)


class UndefinedVariableError(InterpreterError):
    def __init__(self, name: str, position: Position):
        message = f'Undefined variable "{name}" at {position}'
        super().__init__(message)


class VariableAlreadyDeclaredError(InterpreterError):
    def __init__(self, name: str, position: Position):
        message = f'Variable with name "{name}" already exists at {position})'
        super().__init__(message)


class UnknownFunctionCall(InterpreterError):
    def __init__(self, function_name: str, position: Position):
        message = f'Undeclared function call "{function_name}" at {position}'
        super().__init__(message)


class WrongExpressionTypeError(InterpreterError):
    def __init__(self, value_type: Type, expected_types: list[Type] | Type, position: Position):
        if isinstance(expected_types, list):
            string = " or ".join(str(v) for v in expected_types)
        else:
            string = expected_types
        message = f'Wrong value type {value_type} expected {string} at {position}'
        super().__init__(message)


class WrongCastTypeError(InterpreterError):
    def __init__(self, exp_type: Type, position: Position):
        message = f'Unknown target type {exp_type} in cast expression at {position}'
        super().__init__(message)


class DivisionByZeroError(InterpreterError):
    def __init__(self, position: Position):
        message = f'Division by zero at {position}'
        super().__init__(message)


class NotMatchingTypesInBinaryExpression(InterpreterError):
    def __init__(self, left_type: Type, right_type: Type, position: Position):
        message = f'Not matching types in binary operation {left_type}!={right_type} at {position}'
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
    def __init__(self, attr_name: str, exception_id: str):
        message = f'There is no attribute "{attr_name}" for {exception_id}'
        super().__init__(message)


class NoLastResultError(InterpreterError):
    def __init__(self):
        message = f'There is no value to return"'
        super().__init__(message)


class WrongNumberOfArguments(InterpreterError):
    def __init__(self, name: str):
        message = f'Wrong number of arguments in "{name}"'
        super().__init__(message)


class AttributeAlreadyDeclaredError(InterpreterError):
    def __init__(self, attribute_name: str, exception_id: str):
        message = f'Attribute "{attribute_name}" for exception id "{exception_id}" already declared.'
        super().__init__(message)
