from typing import List

from src.ast.expressions import Expression
from src.ast.types import Type
from src.lexer.position import Position
from dataclasses import dataclass



@dataclass
class Statement:
    position: Position

@dataclass
class StatementBlock:
    statements: List[Statement]

@dataclass
class IfStatement(Statement):
    condition: Expression
    if_block: StatementBlock
    elif_condition: List[Expression]
    elif_block: List[StatementBlock]
    else_block: StatementBlock


@dataclass
class WhileStatement(Statement):
    condition: Expression
    block: StatementBlock


@dataclass
class LoopControlStatement(Statement):
    ...


@dataclass
class AssignmentStatement(Statement):
    name: str
    expression: Expression


@dataclass
class FunctionCallStatement(Statement):
    name: str
    arguments: List[Expression]


@dataclass
class ReturnStatement(Statement):
    expression: Expression

@dataclass
class Attribute:
    name: str
    type: Type
    expression: Expression

@dataclass
class AttributeCall:
    var_name: str
    attr_name: str

@dataclass
class Variable(Statement):
    name: str

@dataclass
class Parameter:
    name: str
    type: Type

@dataclass
class Exception:
    name: str
    parameters: list[Parameter]
    attributes: list[Attribute]

@dataclass
class CatchStatement(Statement):
    exception: str
    name: str
    block: StatementBlock


@dataclass
class TryCatchStatement(Statement):
    try_block: StatementBlock
    catch_statements: List[CatchStatement]
