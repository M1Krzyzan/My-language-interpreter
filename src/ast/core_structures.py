from src.ast.statemens import StatementBlock, Parameter
from src.ast.types import ReturnType
from dataclasses import dataclass
from src.ast.statemens import Exception
from src.lexer.position import Position


@dataclass
class Function:
    position: Position
    name: str
    parameters: list[Parameter]
    return_type: ReturnType
    statement_block: StatementBlock

    def __eq__(self, other) -> bool:
        return (isinstance(other, Function) and
                self.position == other.position and
                self.name == other.name and
                self.parameters == other.parameters and
                self.return_type == other.return_type and
                self.statement_block == other.statement_block)


@dataclass
class Program:
    functions: dict[str, Function]
    exceptions: dict[str, Exception]

    def equals(self, other) -> bool:
        return (self.functions == other.functions and
                self.exceptions == other.exceptions)
