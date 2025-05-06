from enum import Enum, auto
from typing import List, Tuple, Optional

from src.ast.expressions import Expression
from src.ast.types import Type
from src.lexer.position import Position
from dataclasses import dataclass, field


@dataclass
class Statement:
    position: Position


@dataclass
class StatementBlock:
    statements: List[Statement]

    def __eq__(self, other):
        return self.statements == other.statements


@dataclass
class IfStatement(Statement):
    condition: Expression
    if_block: StatementBlock
    elif_statement: Optional[List[Tuple[Expression, StatementBlock]]] = field(default_factory=list)
    else_block: Optional[StatementBlock] = None

    def __eq__(self, other):
        return (
            self.condition == other.condition and
            self.if_block == other.if_block and
            self.elif_statement == other.elif_statement if (self.elif_statement and other.elif_statement)
            else self.else_block is other.else_block and
                 self.else_block == other.else_block if (self.else_block and other.else_block)
            else self.else_block is other.else_block
        )


@dataclass
class WhileStatement(Statement):
    condition: Expression
    block: StatementBlock

    def __eq__(self, other):
        return (self.condition == other.condition and
                self.block == other.block)


class LoopControlType(Enum):
    BREAK = auto()
    CONTINUE = auto()


@dataclass
class LoopControlStatement(Statement):
    type: LoopControlType

    def __eq__(self, other):
        return self.type == other.type


@dataclass
class AssignmentStatement(Statement):
    name: str
    expression: Expression

    def __eq__(self, other):
        return (self.expression == other.expression and
                self.name == other.name)


@dataclass
class FunctionCall(Expression, Statement):
    name: str
    arguments: List[Expression]

    def __eq__(self, other):
        return (self.name == other.name and
                self.arguments == other.arguments)


@dataclass
class ReturnStatement(Statement):
    expression: Expression

    def __eq__(self, other):
        return (self.position == other.position and
                self.expression == other.expression)


@dataclass
class Attribute:
    name: str
    type: Type
    expression: Optional[Expression] = field(default_factory=list)

    def __eq__(self, other):
        return (self.name == other.name and
                self.type == other.type and
                self.expression == other.expression)


@dataclass
class Parameter:
    name: str
    type: Type

    def __eq__(self, other):
        return (self.name == other.name and
                self.type == other.type)





@dataclass
class CatchStatement(Statement):
    exception: str
    name: str
    block: StatementBlock

    def __eq__(self, other):
        return (self.exception == other.exception and
                self.block == other.block and
                self.name == other.name)


@dataclass
class TryCatchStatement(Statement):
    try_block: StatementBlock
    catch_statements: List[CatchStatement]

    def __eq__(self, other):
        return (self.try_block == other.try_block and
                self.catch_statements == other.catch_statements)


@dataclass
class ThrowStatement(Statement):
    name: str
    args: List[Expression]

    def __eq__(self, other):
        return (self.name == other.name and
                self.args == other.args)
