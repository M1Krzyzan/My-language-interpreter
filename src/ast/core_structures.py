from src.ast.statemens import StatementBlock, Parameter
from src.ast.types import ReturnType
from dataclasses import dataclass


@dataclass
class Function:
    name: str
    parameters: list[Parameter]
    return_type: ReturnType
    statement_block: StatementBlock


@dataclass
class Program:
    functions: dict[str, Function]
    exceptions: dict[str, Exception]
