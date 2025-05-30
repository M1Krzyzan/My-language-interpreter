import sys

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


class UndefinedVariableError(InterpreterError):
    def __init__(self, name: str, position: Position):
        message = f'Undefined variable "{name}" at {position}'
        super().__init__(message)


class VariableAlreadyDeclaredError(InterpreterError):
    def __init__(self, name: str, position: Position):
        message = f'Variable with name "{name}" already exists at {position})'
        super().__init__(message)


class UnknownFunctionCallError(InterpreterError):
    def __init__(self, function_name: str, position: Position):
        message = f'Undeclared function call "{function_name}" at {position}'
        super().__init__(message)


class WrongExpressionTypeError(InterpreterError):
    def __init__(self,
                 value_type: type,
                 expected_types: list[type] | type,
                 position: Position):
        if isinstance(expected_types, list):
            string = " or ".join(v.__name__ for v in expected_types)
        else:
            string = expected_types.__name__
        message = f'Wrong value type {value_type.__name__} expected {string} at {position}'
        super().__init__(message)


class DivisionByZeroError(InterpreterError):
    def __init__(self, position: Position):
        message = f'Division by zero at {position}'
        super().__init__(message)


class NotMatchingTypesInBinaryExpression(InterpreterError):
    def __init__(self, left_type: Type, right_type: Type, position: Position):
        message = f'Not matching types in binary operation {left_type}!={right_type} at {position}'
        super().__init__(message)


class InvalidReturnedValueTypeException(InterpreterError):
    def __init__(self, value_type: Type, function_type: Type):
        message = f'Type mismatch in return value: expected "{function_type}", but got "{value_type}".'
        super().__init__(message)


class RecursionTooDeepError(InterpreterError):
    def __init__(self, position: Position):
        message = f'Recursion limit reached at {position}'
        super().__init__(message)


class UndefinedExceptionError(InterpreterError):
    def __init__(self, exception_name: str, position: Position):
        message = f'Undefined exception throw "{exception_name}" at {position}'
        super().__init__(message)


class LoopControlOutsideLoopError(InterpreterError):
    def __init__(self, name: str):
        message = f'{name} loop control statement outside loop'
        super().__init__(message)


class UndefinedAttributeError(InterpreterError):
    def __init__(self, attr_name: str, exception_id: str, position: Position):
        message = f'There is no attribute "{attr_name}" for {exception_id} called at {position}'
        super().__init__(message)


class VoidFunctionUsedAsValueError(InterpreterError):
    def __init__(self):
        message = f'There is no value to read from void function call'
        super().__init__(message)


class WrongNumberOfArguments(InterpreterError):
    def __init__(self, name: str, arg_num: int, param_num: int, position: Position):
        message = f'Wrong number of arguments in call of "{name}", expected {arg_num}, got {param_num} at {position}'
        super().__init__(message)


class AttributeAlreadyDeclaredError(InterpreterError):
    def __init__(self, attribute_name: str, exception_id: str, position: Position):
        message = f'Attribute "{attribute_name}" for exception id "{exception_id}" already declared at {position}'
        super().__init__(message)


class ValueReturnInVoidFunctionError(InterpreterError):
    def __init__(self, name: str, position: Position):
        message = f'Returned non-empty value in function call "{name}" at {position}'
        super().__init__(message)


class ReturnStatementMissingError(InterpreterError):
    def __init__(self, name: str):
        message = f'Missing return statement in function "{name}"'
        super().__init__(message)


class ValueOverflowError(InterpreterError):
    def __init__(self, value: float | int, position: Position):
        message = f'Value {value} exceeds allowed maximum of {sys.maxsize} at {position}'
        super().__init__(message)
