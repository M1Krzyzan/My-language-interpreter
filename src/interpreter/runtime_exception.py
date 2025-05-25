from typing import Any

from src.ast.core_structures import CustomException
from src.ast.position import Position
from src.interpreter.builtins import BasicException


class RuntimeUserException(BasicException):
    def __init__(self, definition: CustomException,
                 attributes: dict[str, Any],
                 position: Position):
        super().__init__(position, attributes["message"])
        self.definition = definition
        self.attributes = attributes

    def __str__(self):
        return f"{self.definition.name} at {self.position}: {self.message}"