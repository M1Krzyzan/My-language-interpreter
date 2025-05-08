from abc import ABC, abstractmethod
from src.ast.core_structures import Program, Function, Exception
from src.ast.expressions import OrExpression, AndExpression, CastedExpression, RelationalExpression, \
    AdditiveExpression, MultiplicativeExpression, AttributeCall, Variable, BoolLiteral, FloatLiteral, StringLiteral, \
    IntLiteral, GreaterThanExpression, EqualsExpression, NotEqualsExpression, LessThanExpression, \
    LessThanOrEqualsExpression, GreaterThanOrEqualsExpression, MinusExpression, PlusExpression, ModuloExpression, \
    DivideExpression, MultiplyExpression, NegatedExpression, UnaryMinusExpression
from src.ast.statemens import Statement, StatementBlock, Attribute, IfStatement, ReturnStatement, TryCatchStatement, \
    CatchStatement, WhileStatement, ThrowStatement, FunctionCall, AssignmentStatement, LoopControlStatement


class Visitor(ABC):
    @abstractmethod
    def visit_program(self, program: Program):
        pass

    @abstractmethod
    def visit_function(self, function: Function):
        pass

    @abstractmethod
    def visit_exception(self, exception: Exception):
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
    def visit_function_call(self, self1):
        pass

    @abstractmethod
    def visit_assignment_statement(self, self1):
        pass

    @abstractmethod
    def visit_or_expression(self, self1):
        pass

    @abstractmethod
    def visit_and_expression(self, self1):
        pass

    @abstractmethod
    def visit_casted_expression(self, self1):
        pass

    @abstractmethod
    def visit_negated_expression(self, self1):
        pass

    @abstractmethod
    def visit_unary_minus_expression(self, self1):
        pass

    @abstractmethod
    def visit_attribute_call(self, self1):
        pass

    @abstractmethod
    def visit_variable(self, self1):
        pass

    @abstractmethod
    def visit_bool_literal(self, self1):
        pass

    @abstractmethod
    def visit_float_literal(self, self1):
        pass

    @abstractmethod
    def visit_string_literal(self, self1):
        pass

    @abstractmethod
    def visit_int_literal(self, self1):
        pass

    @abstractmethod
    def visit_multiply_expression(self, self1):
        pass

    @abstractmethod
    def visit_divide_expression(self, self1):
        pass

    @abstractmethod
    def visit_modulo_expression(self, self1):
        pass

    @abstractmethod
    def visit_plus_expression(self, self1):
        pass

    @abstractmethod
    def visit_minus_expression(self, self1):
        pass

    @abstractmethod
    def visit_equals_expression(self, self1):
        pass

    @abstractmethod
    def visit_not_equals_expression(self, self1):
        pass

    @abstractmethod
    def visit_less_than_expression(self, self1):
        pass

    @abstractmethod
    def visit_less_than_or_equals_expression(self, self1):
        pass

    @abstractmethod
    def visit_greater_than_or_equals_expression(self, self1):
        pass

    @abstractmethod
    def visit_greater_than_expression(self, self1):
        pass

    @abstractmethod
    def visit_loop_control_statement(self, loop_control_statement: LoopControlStatement):
        pass


class PrintVisitor(Visitor):
    def __init__(self):
        self.indent = 0

    def _print_with_indent(self, text: str):
        print("\t" * self.indent + text)

    def visit_program(self, program: Program):
        print("Program [")

        for function in program.functions.values():
            function.accept(self)

        for exception in program.exceptions.values():
            exception.accept(self)

        self._print_with_indent("]")

    def visit_function(self, function: Function):
        self.indent += 1
        self._print_with_indent("Function [")

        self.indent += 1
        self._print_with_indent(f"name=\"{function.name}\"")
        self._print_with_indent(f"return_type={function.return_type.type}")

        if len(function.parameters) != 0:
            self._print_with_indent("parameters=[")
            self.indent += 1
            for param in function.parameters:
                self._print_with_indent(f"Param(name={param.name}, type={param.type})")
            self.indent -= 1
            self._print_with_indent("]")
        else:
            self._print_with_indent("parameters=[]")

        self._print_with_indent("body=[")
        function.statement_block.accept(self)
        self._print_with_indent("]")

        self.indent -= 1
        self._print_with_indent("]")

        self.indent -= 1

    def visit_statement_block(self, statement_block: StatementBlock):
        for statement in statement_block.statements:
            statement.accept(self)

    def visit_exception(self, exception: Exception):
        self.indent += 1
        self._print_with_indent("Exception [")
        self.indent += 1

        self._print_with_indent(f"name=\"{exception.name}\"")

        if exception.parameters:
            self._print_with_indent("parameters=[")
            self.indent += 1
            for param in exception.parameters:
                self._print_with_indent(f"Param(name=\"{param.name}\", type={param.type})")
            self.indent -= 1
            self._print_with_indent("]")
        else:
            self._print_with_indent("parameters=[]")

        if exception.attributes:
            self._print_with_indent("attributes=[")
            for attribute in exception.attributes:
                attribute.accept(self)
            self._print_with_indent("]")
        else:
            self._print_with_indent("attributes=[]")

        self.indent -= 1
        self._print_with_indent("]")
        self.indent -= 1

    def visit_attribute(self, attribute: Attribute):
        self.indent += 1
        self._print_with_indent("Attribute(")
        self.indent += 1

        self._print_with_indent(f"name=\"{attribute.name}\"")
        self._print_with_indent(f"type={attribute.type}")

        if attribute.expression:
            self._print_with_indent("expression=[")
            attribute.expression.accept(self)
            self._print_with_indent("]")
        else:
            self._print_with_indent("expression=[]")

        self.indent -= 1
        self._print_with_indent(")")
        self.indent -= 1

    def visit_if_statement(self, if_statement: IfStatement):
        self.indent += 1
        self._print_with_indent("IfStatement[")
        self.indent += 1

        self._print_with_indent("condition=[")
        if_statement.condition.accept(self)
        self._print_with_indent("]")

        self._print_with_indent("if_block=[")
        if_statement.if_block.accept(self)
        self._print_with_indent("]")

        i = 1
        for elif_condition, elif_block in if_statement.elif_statement:
            self._print_with_indent(f"elif_condition{i}=[")
            elif_condition.accept(self)
            self._print_with_indent("]")

            self._print_with_indent(f"elif_block{i}=[")
            elif_block.accept(self)
            self._print_with_indent("]")
            i += 1

        if if_statement.else_block:
            self._print_with_indent("ElseStatement[")
            if_statement.else_block.accept(self)
            self._print_with_indent("]")

        self.indent -= 1
        self._print_with_indent("]")
        self.indent -= 1

    def visit_loop_control_statement(self, loop_control_statement: LoopControlStatement):
        self.indent += 1
        self._print_with_indent(f"LoopControlStatement({loop_control_statement.type})")
        self.indent -= 1

    def visit_return_statement(self, return_statement: ReturnStatement):
        self.indent += 1
        self._print_with_indent("ReturnStatement[")
        self.indent += 1

        return_statement.expression.accept(self)

        self.indent -= 1
        self._print_with_indent("]")
        self.indent -= 1

    def visit_try_catch_statement(self, try_catch_statement: TryCatchStatement):
        self.indent += 1
        self._print_with_indent("TryCatchStatement[")
        self.indent += 1

        self._print_with_indent("try_block=[")
        try_catch_statement.try_block.accept(self)
        self._print_with_indent("]")

        self._print_with_indent("catch_statements=[")
        for catch_statement in try_catch_statement.catch_statements:
            catch_statement.accept(self)
        self._print_with_indent("]")
        self.indent -= 1
        self._print_with_indent("]")
        self.indent -= 1

    def visit_catch_statement(self, catch_statement: CatchStatement):
        self.indent += 1
        self._print_with_indent("CatchStatement(")
        self.indent += 1

        self._print_with_indent(f"exception=\"{catch_statement.exception}\"")
        self._print_with_indent(f"name=\"{catch_statement.name}\"")

        self._print_with_indent("catch_block=[")
        catch_statement.block.accept(self)
        self._print_with_indent("]")

        self.indent -= 1
        self._print_with_indent(")")
        self.indent -= 1

    def visit_while_statement(self, while_statement: WhileStatement):
        self.indent += 1
        self._print_with_indent("WhileStatement[")
        self.indent += 1

        self._print_with_indent("condition=[")
        while_statement.condition.accept(self)
        self._print_with_indent("]")

        self._print_with_indent("while_block=[")
        self.indent += 1

        while_statement.block.accept(self)

        self.indent -= 1
        self._print_with_indent("]")

        self.indent -= 1
        self._print_with_indent("]")
        self.indent -= 1

    def visit_throw_statement(self, throw_statement: ThrowStatement):
        self.indent += 1
        self._print_with_indent("ThrowStatement[")
        self.indent += 1

        self._print_with_indent(f"name=\"{throw_statement.name}\"")
        if len(throw_statement.args) != 0:
            self._print_with_indent("arguments=[")
            for argument in throw_statement.args:
                argument.accept(self)
            self._print_with_indent("]")
        else:
            self._print_with_indent("arguments=[]")

        self.indent -= 1
        self._print_with_indent("]")
        self.indent -= 1

    def visit_function_call(self, function_call: FunctionCall):
        self.indent += 1
        self._print_with_indent("FunctionCall(")
        self.indent += 1

        self._print_with_indent(f"name=\"{function_call.name}\"")

        if len(function_call.arguments) != 0:
            self._print_with_indent("arguments=[")
            for argument in function_call.arguments:
                argument.accept(self)
            self._print_with_indent("]")
        else:
            self._print_with_indent("arguments=[]")

        self.indent -= 1
        self._print_with_indent(")")
        self.indent -= 1

    def visit_assignment_statement(self, assignment_statement: AssignmentStatement):
        self.indent += 1
        self._print_with_indent("AssignmentStatement(")
        self.indent += 1

        self._print_with_indent(f"name=\"{assignment_statement.name}\"")

        self._print_with_indent("expression=[")
        assignment_statement.expression.accept(self)
        self._print_with_indent("]")

        self.indent -= 1
        self._print_with_indent(")")
        self.indent -= 1

    def visit_or_expression(self, or_expression: OrExpression):
        self.indent += 1
        self._print_with_indent("OrExpression(")
        self.indent += 1

        self._print_with_indent("left=[")
        or_expression.left.accept(self)
        self._print_with_indent("]")
        self._print_with_indent("right=[")
        or_expression.right.accept(self)
        self._print_with_indent("]")

        self.indent -= 1
        self._print_with_indent(")")
        self.indent -= 1

    def visit_and_expression(self, and_expression: AndExpression):
        self.indent += 1
        self._print_with_indent("AndExpression(")
        self.indent += 1

        self._print_with_indent("left=[")
        and_expression.left.accept(self)
        self._print_with_indent("]")
        self._print_with_indent("right=[")
        and_expression.right.accept(self)
        self._print_with_indent("]")

        self.indent -= 1
        self._print_with_indent(")")
        self.indent -= 1

    def visit_casted_expression(self, casted_expression: CastedExpression):
        self.indent += 1
        self._print_with_indent("CastedExpression(")
        self.indent += 1

        self._print_with_indent("expression=[")
        casted_expression.expression.accept(self)
        self._print_with_indent("]")
        self._print_with_indent(f"type={casted_expression.to_type}")

        self.indent -= 1
        self._print_with_indent(")")
        self.indent -= 1

    def visit_negated_expression(self, negated_expression: NegatedExpression):
        self.indent += 1
        self._print_with_indent("NegatedExpression(")
        self.indent += 1

        self._print_with_indent("expression=[")
        negated_expression.expression.accept(self)
        self._print_with_indent("]")

        self.indent -= 1
        self._print_with_indent(")")
        self.indent -= 1

    def visit_unary_minus_expression(self, unary_minus_expression: UnaryMinusExpression):
        self.indent += 1
        self._print_with_indent("UnaryMinusExpression(")
        self.indent += 1

        self._print_with_indent("expression=[")
        unary_minus_expression.expression.accept(self)
        self._print_with_indent("]")

        self.indent -= 1
        self._print_with_indent(")")
        self.indent -= 1

    def visit_attribute_call(self, attribute_call: AttributeCall):
        self.indent += 1
        self._print_with_indent("AttributeCall(")
        self.indent += 1

        self._print_with_indent(f"variable=\"{attribute_call.var_name}\"")
        self._print_with_indent(f"attribute=\"{attribute_call.attr_name}\"")

        self.indent -= 1
        self._print_with_indent(")")
        self.indent -= 1

    def visit_variable(self, variable: Variable):
        self.indent += 1
        self._print_with_indent(f"Variable({variable.name})")
        self.indent -= 1

    def visit_bool_literal(self, bool_literal: BoolLiteral):
        self.indent += 1
        self._print_with_indent(f"BoolLiteral({bool_literal.value})")
        self.indent -= 1

    def visit_float_literal(self, float_literal: FloatLiteral):
        self.indent += 1
        self._print_with_indent(f"FloatLiteral({float_literal.value})")
        self.indent -= 1

    def visit_string_literal(self, string_literal: StringLiteral):
        self.indent += 1
        self._print_with_indent(f"StringLiteral({string_literal.value})")
        self.indent -= 1

    def visit_int_literal(self, int_literal: IntLiteral):
        self.indent += 1
        self._print_with_indent(f"IntLiteral({int_literal.value})")
        self.indent -= 1

    def visit_multiply_expression(self, multiply_expression: MultiplyExpression):
        self.visit_multiplicative_expression(multiply_expression, "MultiplyExpression")

    def visit_divide_expression(self, divide_expression: DivideExpression):
        self.visit_multiplicative_expression(divide_expression, "DivideExpression")

    def visit_modulo_expression(self, modulo_expression: ModuloExpression):
        self.visit_multiplicative_expression(modulo_expression, "ModuloExpression")

    def visit_plus_expression(self, plus_expression: PlusExpression):
        self.visit_additive_expression(plus_expression, "PlusExpression")

    def visit_minus_expression(self, minus_expression: MinusExpression):
        self.visit_additive_expression(minus_expression, "MinusExpression")

    def visit_equals_expression(self, equals_expression: EqualsExpression):
        self.visit_relational_expression(equals_expression, "EqualsExpression")

    def visit_not_equals_expression(self, not_equals_expression: NotEqualsExpression):
        self.visit_relational_expression(not_equals_expression, "NotEqualsExpression")

    def visit_less_than_expression(self, less_than_expression: LessThanExpression):
        self.visit_relational_expression(less_than_expression, "LessThanExpression")

    def visit_less_than_or_equals_expression(self, less_than_or_equals_expression: LessThanOrEqualsExpression):
        self.visit_relational_expression(less_than_or_equals_expression, "LessThanOrEqualsExpression")

    def visit_greater_than_or_equals_expression(self, greater_than_or_equals_expression: GreaterThanOrEqualsExpression):
        self.visit_relational_expression(greater_than_or_equals_expression, "GreaterThanOrEqualsExpression")

    def visit_greater_than_expression(self, greater_than_expression: GreaterThanExpression):
        self.visit_relational_expression(greater_than_expression, "GreaterThanExpression")

    def visit_relational_expression(self, relational_expression: RelationalExpression, name: str):
        self.indent += 1
        self._print_with_indent(f"{name}(")
        self.indent += 1

        self._print_with_indent("left=[")
        relational_expression.left.accept(self)
        self._print_with_indent("]")
        self._print_with_indent("right=[")
        relational_expression.right.accept(self)
        self._print_with_indent("]")

        self.indent -= 1
        self._print_with_indent(")")
        self.indent -= 1

    def visit_additive_expression(self, additive_expression: AdditiveExpression, name: str):
        self.indent += 1
        self._print_with_indent(f"{name}(")
        self.indent += 1

        self._print_with_indent("left=[")
        additive_expression.left.accept(self)
        self._print_with_indent("]")
        self._print_with_indent("right=[")
        additive_expression.right.accept(self)
        self._print_with_indent("]")

        self.indent -= 1
        self._print_with_indent(")")
        self.indent -= 1

    def visit_multiplicative_expression(self, multiplicative_expression: MultiplicativeExpression, name: str):
        self.indent += 1
        self._print_with_indent(f"{name}(")
        self.indent += 1

        self._print_with_indent("left=[")
        multiplicative_expression.left.accept(self)
        self._print_with_indent("]")
        self._print_with_indent("right=[")
        multiplicative_expression.right.accept(self)
        self._print_with_indent("]")

        self.indent -= 1
        self._print_with_indent(")")
        self.indent -= 1
