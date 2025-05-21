from typing import Optional

from src.errors.interpreter_errors import InterpreterError
from src.interpreter.variable import TypedVariable


class Scope:
    def __init__(self, parent_scope: 'Scope' = None):
        self.variables = {}
        self.parent_scope = parent_scope

    def declare_variable(self, variable: TypedVariable):
        if not self.contains(variable.name):
            raise InterpreterError(f"Variable '{variable.name}' is not declared in this scope.")
        self.variables[variable.name] = variable

    def assign_variable(self, name: str, value: int|float|bool|str):
        if (variable := self.variables.get(name)) is None:
            raise InterpreterError(f"Variable '{name}' is not declared in this scope.")
        variable.value = value

    def contains(self, name: str) -> bool:
        return name in self.variables

    def get_variable(self, name: str) -> TypedVariable:
        return self.variables.get(name)
