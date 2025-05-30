from typing import Any, Callable, Type, TYPE_CHECKING
from abc import ABC
from dataclasses import dataclass
from src.ast.node import Node
from src.ast.position import Position
if TYPE_CHECKING:
    from src.ast.visitor import Visitor

class BasicException:
    def __init__(self, position: Position, message: str = "Exception raised") -> None:
        self.name = "BasicException"
        self.attributes = [("position",position), ("message",message)]

    def __str__(self):
        return f"Base exception at {self.attributes[0]}: {self.attributes[1]}"

@dataclass
class BuiltinFunction(Node, ABC):
    handler: Callable

    def accept(self, visitor: 'Visitor'):
        visitor.visit_builtin_function(self)


@dataclass
class BuiltinException(Node, ABC):
    exception_object: Type[Any]

    def accept(self, visitor: 'Visitor'):
        visitor.visit_builtin_exception(self)
