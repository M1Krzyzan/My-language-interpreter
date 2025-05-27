from typing import Any

from src.ast.core_structures import CustomException
from src.interpreter.builtins import BasicException


class RuntimeUserException(BasicException):
    def __init__(self, definition: CustomException,
                 attributes: list[tuple[str, Any]]):
        position = next((attr for name, attr in attributes if name == 'position'))
        message = next((attr for name, attr in attributes if name == 'message'))
        super().__init__(position, message)
        self.definition = definition
        self.attributes = attributes

    def __str__(self):
        return f"{self.definition.name} at {self.position}: {self.message}"
