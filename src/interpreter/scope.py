
from src.errors.interpreter_errors import InterpreterError
from src.interpreter.typed_value import TypedValue


class Scope:
    def __init__(self):
        self.variables = {}
        self.exception_attributes = {}

    def declare_variable(self, name: str, value: TypedValue) -> bool:
        if self.contains(name):
            return False
        self.variables[name] = value
        return True

    def assign_variable(self, name: str, value: int|float|bool|str) -> bool:
        if (variable := self.variables.get(name)) is None:
            return False
        variable.value = value
        return True

    def contains(self, name: str) -> bool:
        return name in self.variables

    def get_variable(self, name: str) -> TypedValue:
        return self.variables.get(name)

    def contains_attribute(self, exception_id: str, attribute_name: str) -> bool:
        if exception_id not in self.exception_attributes:
            return False
        return attribute_name in self.exception_attributes[exception_id]

    def add_attribute(self, exception_id:str, name:str, value:TypedValue):
        if exception_id not in self.exception_attributes:
            self.exception_attributes[exception_id] = {}
        self.exception_attributes[exception_id][name] = value

    def get_attribute(self, exception_id: str, attribute_name: str):
        return self.exception_attributes[exception_id][attribute_name]
