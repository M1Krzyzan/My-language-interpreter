from typing import Optional

from src.ast.types import Type
from dataclasses import dataclass

from src.lexer.token_ import TokenType


class Expression:
    pass


@dataclass
class OrExpression(Expression):
    left: Expression
    right: Expression


@dataclass
class AndExpression(Expression):
    left: Expression
    right: Expression


@dataclass
class CastedExpression(Expression):
    expression: Expression
    to_type: Type


@dataclass
class NegatedExpression(Expression):
    expression: Expression


@dataclass
class UnaryMinusExpression(Expression):
    expression: Expression


@dataclass
class RelationalExpression(Expression):
    left: Expression
    right: Expression
    operator: TokenType


@dataclass
class AdditiveExpression(Expression):
    left: Expression
    right: Expression
    operator: TokenType


@dataclass
class MultiplicativeExpression(Expression):
    left: Expression
    right: Expression
    operator: TokenType


@dataclass
class EqualsExpression(Expression):
    left: Expression
    right: Expression


@dataclass
class NotEqualsExpression(Expression):
    left: Expression
    right: Expression


@dataclass
class LessThanExpression(Expression):
    left: Expression
    right: Expression


@dataclass
class LessThanOrEqualsExpression(Expression):
    left: Expression
    right: Expression


@dataclass
class GreaterThanExpression(Expression):
    left: Expression
    right: Expression


@dataclass
class GreaterThanOrEqualsExpression(Expression):
    left: Expression
    right: Expression


@dataclass
class MultiplyExpression(Expression):
    left: Expression
    right: Expression


@dataclass
class DivideExpression(Expression):
    left: Expression
    right: Expression


@dataclass
class ModuloExpression(Expression):
    left: Expression
    right: Expression


@dataclass
class MinusExpression(Expression):
    left: Expression
    right: Expression


@dataclass
class PlusExpression(Expression):
    left: Expression
    right: Expression


@dataclass
class BoolLiteral(Expression):
    value: bool


@dataclass
class FloatLiteral(Expression):
    value: float


@dataclass
class IntLiteral(Expression):
    value: int


@dataclass
class StringLiteral(Expression):
    value: str
