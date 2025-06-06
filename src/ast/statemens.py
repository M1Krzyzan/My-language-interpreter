from typing import List, Tuple, Optional, TYPE_CHECKING

from src.ast.expressions import Expression
from src.ast.types import Type
from src.ast.node import Node
from src.ast.position import Position
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from src.ast.visitor import Visitor


@dataclass
class Statement(Node):
    position: Position

    def accept(self, visitor: 'Visitor'):
        pass


@dataclass
class StatementBlock(Node):
    statements: List[Statement]

    def __eq__(self, other):
        return self.statements == other.statements

    def accept(self, visitor: 'Visitor'):
        visitor.visit_statement_block(self)


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

    def accept(self, visitor: 'Visitor'):
        visitor.visit_if_statement(self)


@dataclass
class WhileStatement(Statement):
    condition: Expression
    block: StatementBlock

    def __eq__(self, other):
        return (self.condition == other.condition and
                self.block == other.block)

    def accept(self, visitor: 'Visitor'):
        visitor.visit_while_statement(self)


@dataclass
class BreakStatement(Statement):
    def __eq__(self, other):
        return isinstance(other, type(self))

    def __str__(self):
        return "break"

    def accept(self, visitor: 'Visitor'):
        visitor.visit_break_statement(self)


@dataclass
class ContinueStatement(Statement):
    def __eq__(self, other):
        return isinstance(other, type(self))

    def __str__(self):
        return "continue"

    def accept(self, visitor: 'Visitor'):
        visitor.visit_continue_statement(self)


@dataclass
class AssignmentStatement(Statement):
    name: str
    expression: Expression

    def __eq__(self, other):
        return (self.expression == other.expression and
                self.name == other.name)

    def accept(self, visitor: 'Visitor'):
        visitor.visit_assignment_statement(self)


@dataclass
class FunctionCall(Expression, Statement):
    name: str
    arguments: List[Expression]

    def __eq__(self, other):
        return (self.name == other.name and
                self.arguments == other.arguments)

    def accept(self, visitor: 'Visitor'):
        visitor.visit_function_call(self)


@dataclass
class ReturnStatement(Statement):
    expression: Expression

    def __eq__(self, other):
        return (self.position == other.position and
                self.expression == other.expression)

    def accept(self, visitor: 'Visitor'):
        visitor.visit_return_statement(self)


@dataclass
class Attribute:
    position: Position
    name: str
    type: Type
    expression: Expression

    def __eq__(self, other):
        return (self.name == other.name and
                self.type == other.type and
                self.expression == other.expression)

    def accept(self, visitor: 'Visitor'):
        visitor.visit_attribute(self)


@dataclass
class Parameter:
    position: Position
    name: str
    type: Type

    def __eq__(self, other):
        return (self.name == other.name and
                self.type == other.type)


@dataclass
class CatchStatement(Statement):
    position: Position
    exception: str
    name: str
    block: StatementBlock

    def __eq__(self, other):
        return (self.exception == other.exception and
                self.block == other.block and
                self.name == other.name)

    def accept(self, visitor: 'Visitor'):
        visitor.visit_catch_statement(self)


@dataclass
class TryCatchStatement(Statement):
    try_block: StatementBlock
    catch_statements: List[CatchStatement]

    def __eq__(self, other):
        return (self.try_block == other.try_block and
                self.catch_statements == other.catch_statements)

    def accept(self, visitor: 'Visitor'):
        visitor.visit_try_catch_statement(self)


@dataclass
class ThrowStatement(Statement):
    name: str
    args: List[Expression]

    def __eq__(self, other):
        return (self.name == other.name and
                self.args == other.args)

    def accept(self, visitor: 'Visitor'):
        visitor.visit_throw_statement(self)
