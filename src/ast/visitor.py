from abc import ABC, abstractmethod

from src.ast.core_structures import Program, Function, CustomException
from src.ast.expressions import OrExpression, AndExpression, CastedExpression, \
    AttributeCall, Variable, BoolLiteral, FloatLiteral, StringLiteral, \
    IntLiteral, GreaterThanExpression, EqualsExpression, NotEqualsExpression, LessThanExpression, \
    LessThanOrEqualsExpression, GreaterThanOrEqualsExpression, MinusExpression, PlusExpression, ModuloExpression, \
    DivideExpression, MultiplyExpression, NegatedExpression, UnaryMinusExpression
from src.ast.statemens import Statement, StatementBlock, Attribute, IfStatement, ReturnStatement, TryCatchStatement, \
    CatchStatement, AssignmentStatement, \
    BreakStatement, ContinueStatement, FunctionCall


class Visitor(ABC):
    @abstractmethod
    def visit_program(self, program: Program):
        pass

    @abstractmethod
    def visit_function(self, function: Function):
        pass

    @abstractmethod
    def visit_exception(self, exception: CustomException):
        pass

    @abstractmethod
    def visit_statement_block(self, statement_block: StatementBlock):
        pass

    @abstractmethod
    def visit_attribute(self, attribute: Attribute):
        pass

    @abstractmethod
    def visit_if_statement(self, if_statement: IfStatement):
        pass

    @abstractmethod
    def visit_return_statement(self, return_statement: ReturnStatement):
        pass

    @abstractmethod
    def visit_try_catch_statement(self, try_catch_statement: TryCatchStatement):
        pass

    @abstractmethod
    def visit_catch_statement(self, catch_statement: CatchStatement):
        pass

    @abstractmethod
    def visit_while_statement(self, statement: Statement):
        pass

    @abstractmethod
    def visit_throw_statement(self, statement: Statement):
        pass

    @abstractmethod
    def visit_function_call(self, function_call: FunctionCall):
        pass

    @abstractmethod
    def visit_assignment_statement(self, assigment_statement: AssignmentStatement):
        pass

    @abstractmethod
    def visit_or_expression(self, or_expression: OrExpression):
        pass

    @abstractmethod
    def visit_and_expression(self, and_expression: AndExpression):
        pass

    @abstractmethod
    def visit_casted_expression(self, casted_expression: CastedExpression):
        pass

    @abstractmethod
    def visit_negated_expression(self, negated_expression: NegatedExpression):
        pass

    @abstractmethod
    def visit_unary_minus_expression(self, unary_minus_expression: UnaryMinusExpression):
        pass

    @abstractmethod
    def visit_attribute_call(self, attribute_call: AttributeCall):
        pass

    @abstractmethod
    def visit_variable(self, variable: Variable):
        pass

    @abstractmethod
    def visit_bool_literal(self, bool_literal: BoolLiteral):
        pass

    @abstractmethod
    def visit_float_literal(self, float_literal: FloatLiteral):
        pass

    @abstractmethod
    def visit_string_literal(self, string_literal: StringLiteral):
        pass

    @abstractmethod
    def visit_int_literal(self, int_literal: IntLiteral):
        pass

    @abstractmethod
    def visit_multiply_expression(self, multiply_expression: MultiplyExpression):
        pass

    @abstractmethod
    def visit_divide_expression(self, divide_expression: DivideExpression):
        pass

    @abstractmethod
    def visit_modulo_expression(self, modulo_expression: ModuloExpression):
        pass

    @abstractmethod
    def visit_plus_expression(self, plus_expression: PlusExpression):
        pass

    @abstractmethod
    def visit_minus_expression(self, minus_expression: MinusExpression):
        pass

    @abstractmethod
    def visit_equals_expression(self, equals_expression: EqualsExpression):
        pass

    @abstractmethod
    def visit_not_equals_expression(self, not_equals_expression: NotEqualsExpression):
        pass

    @abstractmethod
    def visit_less_than_expression(self, less_than_expression: LessThanExpression):
        pass

    @abstractmethod
    def visit_less_than_or_equals_expression(self, less_than_or_equals_expression: LessThanOrEqualsExpression):
        pass

    @abstractmethod
    def visit_greater_than_or_equals_expression(self, greater_than_or_equals_expression: GreaterThanOrEqualsExpression):
        pass

    @abstractmethod
    def visit_greater_than_expression(self, greater_than_expression: GreaterThanExpression):
        pass

    @abstractmethod
    def visit_break_statement(self, break_statement: BreakStatement):
        pass

    @abstractmethod
    def visit_continue_statement(self, continue_statement: ContinueStatement):
        pass
