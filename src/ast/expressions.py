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

    def __eq__(self, other):
        return (self.left == other.left and
                self.right == other.right)


@dataclass
class AndExpression(Expression):
    left: Expression
    right: Expression

    def __eq__(self, other):
        return (self.left == other.left and
                self.right == other.right)


@dataclass
class CastedExpression(Expression):
    expression: Expression
    to_type: Type

    def __eq__(self, other):
        return (self.expression == other.expression and
                self.to_type == other.to_type)


@dataclass
class NegatedExpression(Expression):
    expression: Expression

    def __eq__(self, other):
        return self.expression == other.expression


@dataclass
class UnaryMinusExpression(Expression):
    expression: Expression

    def __eq__(self, other):
        return self.expression == other.expression


@dataclass
class RelationalExpression(Expression):
    left: Expression
    right: Expression
    operator: TokenType

    def __eq__(self, other):
        return (self.left == other.left and
                self.right == other.right and
                self.operator == other.operator)


@dataclass
class AdditiveExpression(Expression):
    left: Expression
    right: Expression
    operator: TokenType

    def __eq__(self, other):
        return (self.left == other.left and
                self.right == other.right and
                self.operator == other.operator)


@dataclass
class MultiplicativeExpression(Expression):
    left: Expression
    right: Expression
    operator: TokenType

    def __eq__(self, other):
        return (self.left == other.left and
                self.right == other.right and
                self.operator == other.operator)

@dataclass
class AttributeCall(Expression):
    var_name: str
    attr_name: str

    def __eq__(self, other):
        return (self.var_name == other.var_name and
                self.attr_name == other.attr_name)

@dataclass
class Variable(Expression):
    name: str

    def __eq__(self, other):
        return self.name == other.name

@dataclass
class BoolLiteral(Expression):
    value: bool
    def __eq__(self, other):
        return self.value == other.value


@dataclass
class FloatLiteral(Expression):
    value: float

    def __eq__(self, other):
        return self.value == other.value


@dataclass
class IntLiteral(Expression):
    value: int

    def __eq__(self, other):
        return self.value == other.value

@dataclass
class StringLiteral(Expression):
    value: str

    def __eq__(self, other):
        return self.value == other.value


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
