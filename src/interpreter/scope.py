
value_types = int|float|str|bool

class Scope:
    def __init__(self):
        self.variables = {}
        self.exception_attributes = {}

    def declare_variable(self, name: str, value: value_types) -> bool:
        if self.contains(name):
            return False
        self.variables[name] = value
        return True

    def assign_value(self, name: str, value: value_types):
        self.variables[name] = value

    def contains(self, name: str) -> bool:
        return name in self.variables

    def get_variable(self, name: str) -> value_types:
        return self.variables.get(name)

    def contains_attribute(self, exception_id: str, attribute_name: str) -> bool:
        if exception_id not in self.exception_attributes:
            return False
        return attribute_name in self.exception_attributes[exception_id]

    def add_attribute(self, exception_id:str, name:str, value: value_types):
        if exception_id not in self.exception_attributes:
            self.exception_attributes[exception_id] = {}
        self.exception_attributes[exception_id][name] = value

    def get_attribute(self, exception_id: str, attribute_name: str):
        return self.exception_attributes[exception_id][attribute_name]
