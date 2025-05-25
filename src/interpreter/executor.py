import io
import operator
from typing import List, Callable

from src.ast.core_structures import Program, Function, CustomException
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
from src.ast.statemens import ContinueStatement, BreakStatement, AssignmentStatement, CatchStatement, \
    TryCatchStatement, ReturnStatement, IfStatement, Attribute, StatementBlock, FunctionCall, WhileStatement, \
    ThrowStatement
from src.ast.types import Type
from src.ast.visitor import Visitor
from src.errors.interpreter_errors import MissingMainFunctionDeclaration, UnknownFunctionCall, InterpreterError, \
    WrongExpressionType, WrongCastType, DivisionByZeroError, NotMatchingTypesInBinaryExpression
from src.interpreter.builtins import builtin_functions, builtin_exceptions
from src.interpreter.context import FunctionContext
from src.interpreter.typed_value import TypedValue
from src.lexer.lexer import DefaultLexer
from src.lexer.source import Source
from src.parser.parser import Parser
from src.interpreter.runtime_exception import RuntimeUserException
VALUE_TO_TYPE_MAP = {
    int: Type.IntType,
    float: Type.FloatType,
    bool: Type.BoolType,
    str: Type.StringType
}

COMPARISON_OPERATORS = {
    'equals': operator.eq,
    'not_equals': operator.ne,
    'less_than': operator.lt,
    'less_than_or_equals': operator.le,
    'greater_than': operator.gt,
    'greater_than_or_equals': operator.ge,
}


class ProgramExecutor(Visitor):
    context_stack: List[FunctionContext]

    def __init__(self, recursion_limit=30):
        self.exception_to_throw = None
        self.break_flag = False
        self.continue_flag = False
        self.return_flag = False
        self.last_result = None
        self.functions = {}
        self.exceptions = builtin_exceptions
        self.recursion_limit = recursion_limit
        self.context_stack = []

    def execute(self, program: Program):
        program.accept(self)
        if self.exception_to_throw:
            print(f"\033[31m{self.exception_to_throw}")

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

    def visit_exception(self, exception: CustomException):
        self.exceptions[exception.name] = exception

    def visit_statement_block(self, statement_block: StatementBlock):
        self.context_stack[-1].push_scope()
        for statement in statement_block.statements:
            statement.accept(self)

            if (self.break_flag or self.continue_flag or
                    self.return_flag or self.exception_to_throw):
                return
        self.context_stack[-1].pop_scope()

    def visit_attribute(self, attribute: Attribute):
            attribute.expression.accept(self)

    def visit_if_statement(self, if_statement: IfStatement):
        if_statement.condition.accept(self)
        condition_value = self._consume_last_result()
        condition_value_type = VALUE_TO_TYPE_MAP.get(type(condition_value))

        if condition_value_type != Type.BoolType:
            raise WrongExpressionType(condition_value_type)

        if condition_value:
            if_statement.if_block.accept(self)
            return

        for elif_condition, elif_block in if_statement.elif_statement:
            elif_condition.accept(self)
            elif_condition_value = self._consume_last_result()
            elif_condition_value_type = VALUE_TO_TYPE_MAP.get(type(elif_condition_value))

            if elif_condition_value_type != Type.BoolType:
                raise WrongExpressionType(condition_value_type)

            if elif_condition_value:
                elif_block.accept(self)
                return

        if if_statement.else_block is not None:
            if_statement.else_block.accept(self)

        self.last_result = None

    def visit_return_statement(self, return_statement: ReturnStatement):
        if return_statement.expression is not None:
            return_statement.expression.accept(self)
        self.return_flag = True

    def visit_try_catch_statement(self, try_catch_statement: TryCatchStatement):
        try_catch_statement.try_block.accept(self)

        if self.exception_to_throw:
            for catch in try_catch_statement.catch_statements:
                catch.accept(self)
                if not self.exception_to_throw:
                    break

    def visit_catch_statement(self, catch_statement: CatchStatement):
        catch = catch_statement
        exception = self.exception_to_throw
        if catch.exception == exception.definition.name or catch.exception == "BasicException":
            self.context_stack[-1].push_scope()
            for attr_name, value in exception.attributes.items():
                value_type = VALUE_TO_TYPE_MAP.get(type(value))
                typed_value = TypedValue(value_type, value)
                self.context_stack[-1].add_attribute(catch.name, attr_name, typed_value)
            catch.block.accept(self)
            self.context_stack[-1].pop_scope()
            self.exception_to_throw = None

    def visit_while_statement(self, while_statement: WhileStatement):
        while_statement.condition.accept(self)
        condition_value = self._consume_last_result()
        condition_value_type = VALUE_TO_TYPE_MAP.get(type(condition_value))

        if condition_value_type != Type.BoolType:
            raise WrongExpressionType(condition_value_type)

        while condition_value:
            while_statement.block.accept(self)

            if self.break_flag:
                self.break_flag = False
                break

            if self.continue_flag:
                self.continue_flag = False
                continue

            while_statement.condition.accept(self)
            condition_value = self._consume_last_result()

        self.last_result = None

    def visit_throw_statement(self, throw_statement: ThrowStatement):
        if (exception_def := self.exceptions.get(throw_statement.name)) is None:
            raise InterpreterError("place holder")

        eval_arguments = []
        for argument in throw_statement.args:
            argument.accept(self)
            eval_arguments.append(self._consume_last_result())

        context = self.context_stack[-1]
        context.push_scope()
        for param, value in zip(exception_def.parameters, eval_arguments):
            value_type = VALUE_TO_TYPE_MAP.get(type(value))
            if value_type != param.type:
                raise WrongExpressionType(value_type)
            typed_value = TypedValue(value=value, type=param.type)
            context.declare_variable(param.name, typed_value)

        eval_attributes = {}
        for attr in exception_def.attributes:
            attr.expression.accept(self)
            eval_attributes[attr.name] = self._consume_last_result()

        context.pop_scope()
        self.exception_to_throw = RuntimeUserException(exception_def, eval_attributes, throw_statement.position)

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
            eval_arguments.append(self._consume_last_result())

        if len(self.context_stack) >= self.recursion_limit:
            raise InterpreterError("recursion limit reached")

        call_context = FunctionContext(function_call.name)
        self.context_stack.append(call_context)

        for param, value in zip(function_def.parameters, eval_arguments):
            typed_value = TypedValue(value=value, type=param.type)
            self.context_stack[-1].declare_variable(param.name, typed_value)

        try:
            function_def.statement_block.accept(self)
            if self.break_flag or self.continue_flag:
                raise InterpreterError("m")
        finally:
            self.context_stack.pop()
            self.return_flag = False

    def visit_builtin_function_call(self, function_call: FunctionCall, builtin_function: Callable):
        eval_arguments = []
        for argument in function_call.arguments:
            argument.accept(self)
            eval_arguments.append(self.last_result)

        builtin_function(eval_arguments)

    def visit_assignment_statement(self, assigment_statement: AssignmentStatement):
        assigment_statement.expression.accept(self)
        name = assigment_statement.name
        value = self._consume_last_result()
        value_type = VALUE_TO_TYPE_MAP.get(type(value))

        context = self.context_stack[-1]
        if (declared_variable := context.get_variable(name)) is not None:
            if declared_variable.type != value_type:
                raise WrongExpressionType(value_type)
            context.assign_variable(name, value)
        else:
            typed_value = TypedValue(value_type, value)
            context.declare_variable(name, typed_value)

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
        attribute = self.context_stack[-1].get_attribute(attribute_call.var_name, attribute_call.attr_name)
        if attribute is None:
            raise InterpreterError("place holder")
        self.last_result = attribute.value

    def visit_variable(self, variable: Variable):
        typed_variable = self.context_stack[-1].get_variable(variable.name)
        variable_value = typed_variable.value
        self.last_result = variable_value

    def visit_bool_literal(self, bool_literal: BoolLiteral):
        self.last_result = True if bool_literal.value == "true" else False

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
        modulo_expression.left.accept(self)
        left = self._consume_last_result()

        left_type = VALUE_TO_TYPE_MAP.get(type(left))
        if left_type != Type.FloatType and left_type != Type.IntType:
            raise WrongExpressionType(left_type)

        modulo_expression.right.accept(self)
        right = self._consume_last_result()

        right_type = VALUE_TO_TYPE_MAP.get(type(right))
        if right_type != Type.FloatType and right_type != Type.IntType:
            raise WrongExpressionType(right_type)

        if left_type != right_type:
            raise NotMatchingTypesInBinaryExpression(left_type, right_type)

        self.last_result = round(left % right, 15)

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

    def visit_equals_expression(self, expression: EqualsExpression):
        self._visit_binary_comparison(expression, COMPARISON_OPERATORS['equals'])

    def visit_not_equals_expression(self, expression: NotEqualsExpression):
        self._visit_binary_comparison(expression, COMPARISON_OPERATORS['not_equals'])

    def visit_less_than_expression(self, expression: LessThanExpression):
        self._visit_binary_comparison(expression, COMPARISON_OPERATORS['less_than'])

    def visit_less_than_or_equals_expression(self, expression: LessThanOrEqualsExpression):
        self._visit_binary_comparison(expression, COMPARISON_OPERATORS['less_than_or_equals'])

    def visit_greater_than_expression(self, expression: GreaterThanExpression):
        self._visit_binary_comparison(expression, COMPARISON_OPERATORS['greater_than'])

    def visit_greater_than_or_equals_expression(self, expression: GreaterThanOrEqualsExpression):
        self._visit_binary_comparison(expression, COMPARISON_OPERATORS['greater_than_or_equals'])

    def _visit_binary_comparison(self, expr, op_func):
        expr.left.accept(self)
        left = self._consume_last_result()
        left_type = VALUE_TO_TYPE_MAP.get(type(left))

        expr.right.accept(self)
        right = self._consume_last_result()
        right_type = VALUE_TO_TYPE_MAP.get(type(right))

        if left_type != right_type:
            raise NotMatchingTypesInBinaryExpression(left_type, right_type)

        self.last_result = op_func(left, right)

    def visit_break_statement(self, break_statement: BreakStatement):
        self.break_flag = True

    def visit_continue_statement(self, continue_statement: ContinueStatement):
        self.continue_flag = True

    def _consume_last_result(self):
        if self.last_result is None:
            raise InterpreterError("There is no value to return")
        value = self.last_result
        self.last_result = None
        return value

    def _cast_expression(self, to_type: Type):
        value = self._consume_last_result()
        origin_type = type(value)

        cast_map = {
            int: self._cast_int,
            float: self._cast_float,
            bool: self._cast_boolean,
            str: self._cast_string,
        }

        cast_func = cast_map.get(origin_type)
        if not cast_func:
            raise WrongExpressionType(origin_type)

        self.last_result = cast_func(to_type, value)

    @staticmethod
    def _check_numeric_type(value_type: Type):
        if value_type not in (Type.IntType, Type.FloatType):
            raise WrongExpressionType(value_type)

    @staticmethod
    def _cast_int(to_type: Type, value: int):
        cast_map = {
            Type.IntType: lambda v: v,
            Type.FloatType: float,
            Type.BoolType: lambda v: v != 0,
            Type.StringType: str,
        }
        if to_type not in cast_map:
            raise WrongCastType(to_type)
        return cast_map[to_type](value)

    @staticmethod
    def _cast_float(to_type: Type, value: float):
        cast_map = {
            Type.IntType: int,
            Type.FloatType: lambda v: v,
            Type.BoolType: lambda v: v != 0.0,
            Type.StringType: str,
        }
        if to_type not in cast_map:
            raise WrongCastType(to_type)
        return cast_map[to_type](value)

    @staticmethod
    def _cast_boolean(to_type: Type, value: bool):
        cast_map = {
            Type.IntType: lambda v: 1 if v else 0,
            Type.FloatType: lambda v: 1.0 if v else 0.0,
            Type.BoolType: lambda v: v,
            Type.StringType: lambda v: "true" if v else "false",
        }
        if to_type not in cast_map:
            raise WrongCastType(to_type)
        return cast_map[to_type](value)

    @staticmethod
    def _cast_string(to_type: Type, value: str):
        cast_map = {
            Type.IntType: int,
            Type.FloatType: float,
            Type.BoolType: lambda v: v != '',
            Type.StringType: lambda v: v,
        }
        if to_type not in cast_map:
            raise WrongCastType(to_type)
        return cast_map[to_type](value)

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
