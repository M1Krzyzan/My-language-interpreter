from typing import Optional

from src.interpreter.scope import Scope
from src.interpreter.typed_value import TypedValue


class FunctionContext:
    def __init__(self, function_name: str):
        self.function_name = function_name
        self.variables = {}
        self.scope_stack = [Scope()]

    def push_scope(self):
        self.scope_stack.append(Scope())

    def pop_scope(self):
        self.scope_stack.pop()

    def declare_variable(self, name: str, value: TypedValue) -> bool:
        scope = self.scope_stack[-1]
        return not scope.contains(name) and scope.declare_variable(name, value)

    def assign_variable(self, name: str, value: int|float|bool|str) -> bool:
        for scope in reversed(self.scope_stack):
            if scope.contains(name):
                scope.assign_variable(name, value)
                return True
        return False

    def get_variable(self, name: str) -> Optional[TypedValue]:
        for scope in reversed(self.scope_stack):
            if scope.contains(name):
                return scope.get_variable(name)
        return None

    def get_attribute(self, exception_id: str, attribute_name: str) -> Optional[TypedValue]:
        for scope in reversed(self.scope_stack):
            if scope.contains_attribute(exception_id, attribute_name):
                return scope.get_attribute(exception_id, attribute_name)
        return None

    def add_attribute(self, exception_id: str, attribute_name: str, value: TypedValue) -> bool:
        if self.scope_stack[-1].contains_attribute(exception_id, attribute_name):
            return False
        self.scope_stack[-1].add_attribute(exception_id, attribute_name, value)
        return True