from typing import TYPE_CHECKING

from dataclasses import dataclass

from src.ast.types import SimpleType
from src.lexer.token_ import TokenType

if TYPE_CHECKING:
    from src.ast.visitor import Visitor


class Expression:
    def accept(self, visitor: 'Visitor'):
        pass


@dataclass
class OrExpression(Expression):
    left: Expression
    right: Expression

    def __eq__(self, other):
        return (self.left == other.left and
                self.right == other.right)

    def accept(self, visitor: 'Visitor'):
        visitor.visit_or_expression(self)


@dataclass
class AndExpression(Expression):
    left: Expression
    right: Expression

    def __eq__(self, other):
        return (self.left == other.left and
                self.right == other.right)

    def accept(self, visitor: 'Visitor'):
        visitor.visit_and_expression(self)


@dataclass
class CastedExpression(Expression):
    expression: Expression
    to_type: SimpleType

    def __eq__(self, other):
        return (self.expression == other.expression and
                self.to_type == other.to_type)

    def accept(self, visitor: 'Visitor'):
        visitor.visit_casted_expression(self)

@dataclass
class NegatedExpression(Expression):
    expression: Expression

    def __eq__(self, other):
        return self.expression == other.expression

    def accept(self, visitor: 'Visitor'):
        visitor.visit_negated_expression(self)

@dataclass
class UnaryMinusExpression(Expression):
    expression: Expression

    def __eq__(self, other):
        return self.expression == other.expression

    def accept(self, visitor: 'Visitor'):
        visitor.visit_unary_minus_expression(self)

@dataclass
class RelationalExpression(Expression):
    left: Expression
    right: Expression

    def __eq__(self, other):
        return (isinstance(other, type(self)) and
                self.left == other.left and
                self.right == other.right)

    def accept(self, visitor: 'Visitor'):
        visitor.visit_relational_expression(self)


@dataclass
class EqualsExpression(RelationalExpression):
    def accept(self, visitor: 'Visitor'):
        visitor.visit_equals_expression(self)


@dataclass
class NotEqualsExpression(RelationalExpression):
    def accept(self, visitor: 'Visitor'):
        visitor.visit_not_equals_expression(self)


@dataclass
class LessThanExpression(RelationalExpression):
    def accept(self, visitor: 'Visitor'):
        visitor.visit_less_than_expression(self)


@dataclass
class LessThanOrEqualsExpression(RelationalExpression):
    def accept(self, visitor: 'Visitor'):
        visitor.visit_less_than_or_equals_expression(self)


@dataclass
class GreaterThanExpression(RelationalExpression):
    def accept(self, visitor: 'Visitor'):
        visitor.visit_greater_than_expression(self)


@dataclass
class GreaterThanOrEqualsExpression(RelationalExpression):
    def accept(self, visitor: 'Visitor'):
        visitor.visit_greater_than_or_equals_expression(self)


@dataclass
class AdditiveExpression(Expression):
    left: Expression
    right: Expression

    def __eq__(self, other):
        return (isinstance(other, type(self)) and
                self.left == other.left and
                self.right == other.right)

    def accept(self, visitor: 'Visitor'):
        visitor.visit_additive_expression(self)


@dataclass
class MinusExpression(AdditiveExpression):
    def accept(self, visitor: 'Visitor'):
        visitor.visit_minus_expression(self)


@dataclass
class PlusExpression(AdditiveExpression):
    def accept(self, visitor: 'Visitor'):
        visitor.visit_plus_expression(self)


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
    def accept(self, visitor: 'Visitor'):
        visitor.visit_multiply_expression(self)


@dataclass
class DivideExpression(MultiplicativeExpression):
    def accept(self, visitor: 'Visitor'):
        visitor.visit_divide_expression(self)


@dataclass
class ModuloExpression(MultiplicativeExpression):
    def accept(self, visitor: 'Visitor'):
        visitor.visit_modulo_expression(self)


@dataclass
class AttributeCall(Expression):
    var_name: str
    attr_name: str

    def __eq__(self, other):
        return (self.var_name == other.var_name and
                self.attr_name == other.attr_name)

    def accept(self, visitor: 'Visitor'):
        visitor.visit_attribute_call(self)


@dataclass
class Variable(Expression):
    name: str

    def __eq__(self, other):
        return self.name == other.name

    def accept(self, visitor: 'Visitor'):
        visitor.visit_variable(self)


@dataclass
class BoolLiteral(Expression):
    value: bool

    def __eq__(self, other):
        return self.value == other.value

    def accept(self, visitor: 'Visitor'):
        visitor.visit_bool_literal(self)

@dataclass
class FloatLiteral(Expression):
    value: float

    def __eq__(self, other):
        return self.value == other.value

    def accept(self, visitor: 'Visitor'):
        visitor.visit_float_literal(self)

@dataclass
class IntLiteral(Expression):
    value: int

    def __eq__(self, other):
        return self.value == other.value

    def accept(self, visitor: 'Visitor'):
        visitor.visit_int_literal(self)

@dataclass
class StringLiteral(Expression):
    value: str

    def __eq__(self, other):
        return self.value == other.value

    def accept(self, visitor: 'Visitor'):
        visitor.visit_string_literal(self)

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