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

    def __eq__(self, other):
        return (isinstance(other, type(self)) and
                self.left == other.left and
                self.right == other.right)


@dataclass
class EqualsExpression(RelationalExpression):
    ...


@dataclass
class NotEqualsExpression(RelationalExpression):
    ...


@dataclass
class LessThanExpression(RelationalExpression):
    ...


@dataclass
class LessThanOrEqualsExpression(RelationalExpression):
    ...


@dataclass
class GreaterThanExpression(RelationalExpression):
    ...


@dataclass
class GreaterThanOrEqualsExpression(RelationalExpression):
    ...


@dataclass
class AdditiveExpression(Expression):
    left: Expression
    right: Expression

    def __eq__(self, other):
        return (isinstance(other, type(self)) and
                self.left == other.left and
                self.right == other.right)


@dataclass
class MinusExpression(AdditiveExpression):
    ...


@dataclass
class PlusExpression(AdditiveExpression):
    ...


@dataclass
class MultiplicativeExpression(Expression):
    left: Expression
    right: Expression

    def __eq__(self, other):
        return (isinstance(other, type(self)) and
                self.left == other.left and
                self.right == other.right)


@dataclass
class MultiplyExpression(MultiplicativeExpression):
    ...


@dataclass
class DivideExpression(MultiplicativeExpression):
    ...


@dataclass
class ModuloExpression(MultiplicativeExpression):
    ...


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


RELATIONAL_OPERATOR_MAP = {
    TokenType.LESS_THAN_OPERATOR: LessThanExpression,
    TokenType.GREATER_THAN_OR_EQUAL_OPERATOR: GreaterThanOrEqualsExpression,
    TokenType.GREATER_THAN_OPERATOR: GreaterThanExpression,
    TokenType.LESS_THAN_OR_EQUAL_OPERATOR: LessThanOrEqualsExpression,
    TokenType.EQUAL_OPERATOR: EqualsExpression,
    TokenType.NOT_EQUAL_OPERATOR: NotEqualsExpression
}

MULTIPLICATIVE_OPERATOR_MAP = {
    TokenType.MULTIPLICATION_OPERATOR: MultiplyExpression,
    TokenType.DIVISION_OPERATOR: DivideExpression,
    TokenType.MODULO_OPERATOR: ModuloExpression
}

ADDITIVE_OPERATOR_MAP = {
    TokenType.PLUS_OPERATOR: PlusExpression,
    TokenType.MINUS_OPERATOR: MinusExpression
}