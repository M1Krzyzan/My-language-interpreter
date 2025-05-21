from typing import Optional

from src.errors.interpreter_errors import InterpreterError
from src.interpreter.scope import Scope
from src.interpreter.variable import TypedVariable


class FunctionContext:
    def __init__(self, function_name: str):
        self.function_name = function_name
        self.variables = {}
        self.scope_stack = [Scope()]

    def push_scope(self):
        self.scope_stack.append(Scope())

    def pop_scope(self):
        if len(self.scope_stack) == 1:
            raise InterpreterError("Cannot pop the base (function) scope.")
        self.scope_stack.pop()

    def declare_variable(self, variable: TypedVariable):
        if self.scope_stack[-1].contains(variable.name):
            raise InterpreterError(f"Variable '{variable.name}' already declared.")
        self.scope_stack[-1].declare_variable(variable)

    def assign_variable(self, name: str, value: int|float|bool|str):
        for scope in reversed(self.scope_stack):
            if scope.contains(name):
                scope.assign_variable(name, value)
                return
        raise InterpreterError(f"Variable '{name}' not found in any scope.")

    def get_variable(self, name: str) -> TypedVariable:
        for scope in reversed(self.scope_stack):
            if scope.contains(name):
                return scope.get_variable(name)
        raise InterpreterError(f"Variable '{name}' not found in any scope.")