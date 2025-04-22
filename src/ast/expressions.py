from src.ast.types import Type
from dataclasses import dataclass


class Expression:
    def __init__(self, left: 'Expression', right: 'Expression'):
        self.left = left
        self.right = right


@dataclass
class CastedExpression:
    expression: Expression
    to_type: Type


@dataclass
class NegatedExpression:
    expression: Expression


@dataclass
class AndExpression(Expression):
    ...


@dataclass
class OrExpression(Expression):
    ...


@dataclass
class EqualsExpression(Expression):
    ...


@dataclass
class NotEqualsExpression(Expression):
    ...


@dataclass
class LessThanExpression(Expression):
    ...


@dataclass
class LessThanOrEqualsExpression(Expression):
    ...


@dataclass
class GreaterThanExpression(Expression):
    ...


@dataclass
class GreaterThanOrEqualsExpression(Expression):
    ...


@dataclass
class MultiplyExpression(Expression):
    ...


@dataclass
class DivideExpression(Expression):
    ...


@dataclass
class ModuloExpression(Expression):
    ...


@dataclass
class MinusExpression(Expression):
    ...


@dataclass
class PlusExpression(Expression):
    ...
