from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.ast.visitor import Visitor


class Node(ABC):
    @abstractmethod
    def accept(self, visitor: 'Visitor'):
        pass