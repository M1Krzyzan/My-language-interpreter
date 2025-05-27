from typing import Any

from src.ast.core_structures import CustomException
from src.interpreter.builtins import BasicException


class RuntimeUserException(BasicException):
    def __init__(self, definition: CustomException,
                 attributes: dict[str, Any]):
        super().__init__(attributes["position"], attributes["message"])
        self.definition = definition
        self.attributes = attributes

    def __str__(self):
        return f"{self.definition.name} at {self.position}: {self.message}"