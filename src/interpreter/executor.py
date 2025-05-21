import io
from typing import List, Callable

from src.ast.core_structures import Program, Function, Exception
from src.ast.expressions import (
    GreaterThanExpression,
    GreaterThanOrEqualsExpression,
    LessThanOrEqualsExpression,
    LessThanExpression,
    NotEqualsExpression,
    EqualsExpression,
    MinusExpression,
    PlusExpression,
    ModuloExpression,
    DivideExpression,
    MultiplyExpression,
    IntLiteral,
    StringLiteral,
    FloatLiteral,
    BoolLiteral,
    Variable,
    AttributeCall, UnaryMinusExpression, NegatedExpression, CastedExpression, AndExpression, OrExpression
)
from src.ast.position import Position
from src.ast.statemens import ContinueStatement, BreakStatement, AssignmentStatement, Statement, CatchStatement, \
    TryCatchStatement, ReturnStatement, IfStatement, Attribute, StatementBlock, FunctionCall
from src.ast.types import Type
from src.ast.visitor import Visitor
from src.errors.interpreter_errors import MissingMainFunctionDeclaration, UnknownFunctionCall, InterpreterError, \
    WrongExpressionType, WrongCastType, DivisionByZeroError, NotMatchingTypesInBinaryExpression
from src.interpreter.builtins import builtin_functions, builtin_exceptions
from src.interpreter.context import FunctionContext
from src.interpreter.variable import TypedVariable
from src.lexer.lexer import DefaultLexer
from src.lexer.source import Source
from src.parser.parser import Parser

VALUE_TO_TYPE_MAP = {
    int: Type.IntType,
    float: Type.FloatType,
    bool: Type.BoolType,
    str: Type.StringType
}


class ProgramExecutor(Visitor):
    context_stack: List[FunctionContext]

    def __init__(self, recursion_limit=100):
        self.return_flag = False
        self.last_result = None
        self.functions = {}
        self.exceptions = builtin_exceptions
        self.recursion_limit = recursion_limit
        self.context_stack = []

    def execute(self, program: Program):
        program.accept(self)

    def visit_program(self, program: Program):
        if program.functions.get("main") is None:
            raise MissingMainFunctionDeclaration(Position(1, 1))

        for function in program.functions.values():
            function.accept(self)
        for exception in program.exceptions.values():
            exception.accept(self)

        main_call = FunctionCall(position=self.functions["main"].position,
                                 name="main",
                                 arguments=[])
        main_call.accept(self)

    def visit_function(self, function: Function):
        self.functions[function.name] = function

    def visit_exception(self, exception: Exception):
        self.exceptions[exception.name] = exception

    def visit_statement_block(self, statement_block: StatementBlock):
        self.context_stack[-1].push_scope()
        for statement in statement_block.statements:
            statement.accept(self)

            if self.return_flag:
                self.return_flag = False
                return
        self.context_stack[-1].pop_scope()

    def visit_attribute(self, attribute: Attribute):
        pass

    def visit_if_statement(self, if_statement: IfStatement):
        pass

    def visit_return_statement(self, return_statement: ReturnStatement):
        if return_statement.expression is not None:
            return_statement.expression.accept(self)
        self.return_flag = True

    def visit_try_catch_statement(self, try_catch_statement: TryCatchStatement):
        pass

    def visit_catch_statement(self, catch_statement: CatchStatement):
        pass

    def visit_while_statement(self, statement: Statement):
        pass

    def visit_throw_statement(self, statement: Statement):
        pass

    def visit_function_call(self, function_call: FunctionCall):
        function_name = function_call.name
        if function_def := self.functions.get(function_name):
            self.visit_user_function_call(function_call, function_def)
        elif builtin_def := builtin_functions.get(function_name):
            self.visit_builtin_function_call(function_call, builtin_def)
        else:
            raise UnknownFunctionCall(function_call.position, function_name)

    def visit_user_function_call(self, function_call: FunctionCall, function_def: Function):
        eval_arguments = []
        for argument in function_call.arguments:
            argument.accept(self)
            eval_arguments.append(self.last_result)

        call_context = FunctionContext(function_call.name)
        self.context_stack.append(call_context)

        for param, value in zip(function_def.parameters, eval_arguments):
            variable = TypedVariable(name=param.name, value=value, type=param.type)
            self.context_stack[-1].declare_variable(variable)

        try:
            function_def.statement_block.accept(self)
        finally:
            self.context_stack.pop()

    def visit_builtin_function_call(self, function_call: FunctionCall, builtin_function: Callable):
        eval_arguments = []
        for argument in function_call.arguments:
            argument.accept(self)
            eval_arguments.append(self.last_result)

        builtin_function(eval_arguments)

    def visit_assignment_statement(self, assigment_statement: AssignmentStatement):
        assigment_statement.expression.accept(self)
        name = assigment_statement.name
        value_type = VALUE_TO_TYPE_MAP.get(type(self.last_result))
        variable = TypedVariable(name, value_type, self._consume_last_result())
        self.context_stack[-1].declare_variable(variable)

    def visit_or_expression(self, or_expression: OrExpression):
        or_expression.left.accept(self)
        left = self._consume_last_result()

        or_expression.right.accept(self)
        right = self._consume_last_result()

        self.last_result = left or right

    def visit_and_expression(self, and_expression: AndExpression):
        and_expression.left.accept(self)
        left = self._consume_last_result()
        left_type = VALUE_TO_TYPE_MAP.get(type(left))
        if left_type != Type.BoolType:
            raise WrongExpressionType(left_type)

        and_expression.right.accept(self)
        right = self._consume_last_result()
        right_type = VALUE_TO_TYPE_MAP.get(type(right))
        if right_type != Type.BoolType:
            raise WrongExpressionType(right_type)

        self.last_result = left and right

    def visit_casted_expression(self, casted_expression: CastedExpression):
        casted_expression.expression.accept(self)
        self._cast_expression(casted_expression.to_type)

    def visit_negated_expression(self, negated_expression: NegatedExpression):
        negated_expression.expression.accept(self)
        value = self._consume_last_result()
        value_type = VALUE_TO_TYPE_MAP.get(type(value))
        if value_type != Type.BoolType:
            raise WrongExpressionType(value_type)
        self.last_result = not value

    def visit_unary_minus_expression(self, unary_minus_expression: UnaryMinusExpression):
        unary_minus_expression.expression.accept(self)
        value = self._consume_last_result()
        value_type = VALUE_TO_TYPE_MAP.get(type(value))
        if value_type != Type.IntType and value_type != Type.FloatType:
            raise WrongExpressionType(value_type)
        self.last_result = -value

    def visit_attribute_call(self, attribute_call: AttributeCall):
        pass

    def visit_variable(self, variable: Variable):
        typed_variable = self.context_stack[-1].get_variable(variable.name)
        variable_value = typed_variable.value
        self.last_result = variable_value

    def visit_bool_literal(self, bool_literal: BoolLiteral):
        self.last_result = bool_literal.value

    def visit_float_literal(self, float_literal: FloatLiteral):
        self.last_result = float_literal.value

    def visit_string_literal(self, string_literal: StringLiteral):
        self.last_result = string_literal.value

    def visit_int_literal(self, int_literal: IntLiteral):
        self.last_result = int_literal.value

    def visit_multiply_expression(self, multiply_expression: MultiplyExpression):
        multiply_expression.left.accept(self)
        left = self._consume_last_result()

        left_type = VALUE_TO_TYPE_MAP.get(type(left))
        if left_type != Type.FloatType and left_type != Type.IntType:
            raise WrongExpressionType(left_type)

        multiply_expression.right.accept(self)
        right = self._consume_last_result()

        right_type = VALUE_TO_TYPE_MAP.get(type(right))
        if right_type != Type.FloatType and right_type != Type.IntType:
            raise WrongExpressionType(right_type)

        if left_type != right_type:
            raise NotMatchingTypesInBinaryExpression(left_type, right_type)
        self.last_result = left * right

    def visit_divide_expression(self, divide_expression: DivideExpression):
        divide_expression.left.accept(self)
        left = self._consume_last_result()

        left_type = VALUE_TO_TYPE_MAP.get(type(left))
        if left_type != Type.FloatType and left_type != Type.IntType:
            raise WrongExpressionType(left_type)

        divide_expression.right.accept(self)
        right = self._consume_last_result()

        right_type = VALUE_TO_TYPE_MAP.get(type(right))
        if right_type != Type.FloatType and right_type != Type.IntType:
            raise WrongExpressionType(right_type)

        if right == 0:
            raise DivisionByZeroError()

        if left_type != right_type:
            raise NotMatchingTypesInBinaryExpression(left_type, right_type)

        if left_type == Type.IntType:
            self.last_result = left // right
        elif left_type == Type.FloatType:
            self.last_result = left / right

    def visit_modulo_expression(self, modulo_expression: ModuloExpression):
        pass

    def visit_plus_expression(self, plus_expression: PlusExpression):
        plus_expression.left.accept(self)
        left = self._consume_last_result()

        left_type = VALUE_TO_TYPE_MAP.get(type(left))
        if left_type == Type.BoolType or left_type == Type.VoidType:
            raise WrongExpressionType(left_type)

        plus_expression.right.accept(self)
        right = self._consume_last_result()

        right_type = VALUE_TO_TYPE_MAP.get(type(right))
        if left_type == Type.BoolType or left_type == Type.VoidType:
            raise WrongExpressionType(right_type)

        if left_type != right_type:
            raise NotMatchingTypesInBinaryExpression(left_type, right_type)

        self.last_result = left + right

    def visit_minus_expression(self, minus_expression: MinusExpression):
        minus_expression.left.accept(self)
        left = self._consume_last_result()

        left_type = VALUE_TO_TYPE_MAP.get(type(left))
        if left_type == Type.BoolType or left_type == Type.VoidType:
            raise WrongExpressionType(left_type)

        minus_expression.right.accept(self)
        right = self._consume_last_result()

        right_type = VALUE_TO_TYPE_MAP.get(type(right))
        if left_type == Type.BoolType or left_type == Type.VoidType:
            raise WrongExpressionType(right_type)

        if left_type != right_type:
            raise NotMatchingTypesInBinaryExpression(left_type, right_type)

        self.last_result = left - right

    def visit_equals_expression(self, equals_expression: EqualsExpression):
        equals_expression.left.accept(self)
        left = self._consume_last_result()

        equals_expression.right.accept(self)
        right = self._consume_last_result()

    def visit_not_equals_expression(self, not_equals_expression: NotEqualsExpression):
        pass

    def visit_less_than_expression(self, less_than_expression: LessThanExpression):
        pass

    def visit_less_than_or_equals_expression(self, less_than_or_equals_expression: LessThanOrEqualsExpression):
        pass

    def visit_greater_than_or_equals_expression(self, greater_than_or_equals_expression: GreaterThanOrEqualsExpression):
        pass

    def visit_greater_than_expression(self, greater_than_expression: GreaterThanExpression):
        pass

    def visit_break_statement(self, break_statement: BreakStatement):
        pass

    def visit_continue_statement(self, continue_statement: ContinueStatement):
        pass

    def _consume_last_result(self):
        if self.last_result is None:
            raise InterpreterError("There is no value to return")
        value = self.last_result
        self.last_result = None
        return value

    def _cast_expression(self, to_type: Type):
        value = self._consume_last_result()
        origin_type = type(value)
        if isinstance(origin_type, int.__class__):
            self.last_result = self._cast_int(to_type, value)
        elif isinstance(origin_type, float.__class__):
            self.last_result = self._cast_float(to_type, value)
        elif isinstance(origin_type, bool.__class__):
            self.last_result = self._cast_boolean(to_type, value)
        elif isinstance(origin_type, str.__class__):
            self.last_result = self._cast_string(to_type, value)
        else:
            raise WrongExpressionType(origin_type)

    @staticmethod
    def _cast_int(to_type: Type, value: int) -> [int | float | bool | str]:
        if to_type == Type.IntType:
            return value
        elif to_type == Type.FloatType:
            return float(value)
        elif to_type == Type.BoolType:
            return False if value == 0 else True
        elif to_type == Type.StringType:
            return str(value)
        else:
            WrongCastType(to_type)

    @staticmethod
    def _cast_float(to_type: Type, value: float) -> [int | float | bool | str]:
        if to_type == Type.IntType:
            return int(value)
        elif to_type == Type.FloatType:
            return value
        elif to_type == Type.BoolType:
            return False if value == 0.0 else True
        elif to_type == Type.StringType:
            return str(value)
        else:
            WrongCastType(to_type)

    @staticmethod
    def _cast_boolean(to_type: Type, value: bool) -> [int | float | bool | str]:
        if to_type == Type.IntType:
            return 1 if value else 0
        elif to_type == Type.FloatType:
            return 1.0 if value else 0.0
        elif to_type == Type.BoolType:
            return value
        elif to_type == Type.StringType:
            return "true" if value else "false"
        else:
            WrongCastType(to_type)

    @staticmethod
    def _cast_string(to_type: Type, value: str) -> [int | float | bool | str]:
        if to_type == Type.IntType:
            return int(value)
        elif to_type == Type.FloatType:
            return float(value)
        elif to_type == Type.BoolType:
            return False if value == '' else True
        elif to_type == Type.StringType:
            return value
        else:
            WrongCastType(to_type)


def main():
    input_code = """
        exception ValueError(int value) {
            message: string = "Wrong value="+value to string +" - should be higher than 0: ";
        }

        $
        Block
        comment
        $

        bool is_even(int number){
            return number % 2 == 0;
        }

        void print_even_if_not_divisible_by_5(int number){
            while (number > 0) {
                # comment
                if (number % 5 == 0) {
                    break;
                }elif (is_even(number)) {
                    continue;
                }else{
                    print("x: ", number);
                    number = number - 1;
                }
            }
        }
        void main(){
            try{
                x = input() to int;
                if (x <= 0){
                    throw ValueError(x);
                }
                print_even_if_not_divisible_by_5(x);
            }catch(BaseException e){
                print("Error: ", e.message, "\\n \\t Value=", e.value, e.line, "\\n");
            }
        }
        """
    stream = io.StringIO(input_code)
    source = Source(stream)
    lexer = DefaultLexer(source)
    program = Parser(lexer).get_program()
    ProgramExecutor().execute(program)


if __name__ == '__main__':
    main()
