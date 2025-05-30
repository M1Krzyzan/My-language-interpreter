import io
from operator import eq, ne, lt, le, gt, ge, add, mul, sub, mod
from typing import Callable

from src.ast.core_structures import Program, Function, CustomException
from src.ast.expressions import *
from src.ast.statemens import *
from src.ast.visitor import Visitor
from src.errors.interpreter_errors import *
from src.interpreter.builtins import BuiltinFunction, BuiltinException, BasicException
from src.interpreter.context import FunctionContext
from src.interpreter.runtime_exception import RuntimeUserException
from src.lexer.lexer import DefaultLexer
from src.lexer.source import Source
from src.parser.parser import Parser

VALUE_TO_TYPE_MAP = {
    int: Type.IntType,
    float: Type.FloatType,
    bool: Type.BoolType,
    str: Type.StringType
}
TYPE_TO_VALUE_MAP = {v: k for k, v in VALUE_TO_TYPE_MAP.items()}

COMPARISON_OPERATORS = {
    'equals': eq,
    'not_equals': ne,
    'less_than': lt,
    'less_than_or_equals': le,
    'greater_than': gt,
    'greater_than_or_equals': ge,
}


class ProgramExecutor(Visitor):

    def __init__(self, recursion_limit=30, number_precision=15):
        self.recursion_limit = recursion_limit
        self.number_precision = number_precision
        self.break_flag = False
        self.continue_flag = False
        self.return_flag = False
        self.exception_to_throw = None
        self.catched = False
        self.last_result = None
        self.functions = {}
        self.exceptions = {}
        self.context_stack = []

    def execute(self, program: Program):
        program.accept(self)
        if self.exception_to_throw:
            print(f"\033[31m{self.exception_to_throw}\033[0m")

    def visit_program(self, program: Program):
        if program.functions.get("main") is None:
            raise MissingMainFunctionDeclaration()

        self.functions["print"] = BuiltinFunction(self.builtin_print)
        self.functions["input"] = BuiltinFunction(self.builtin_input)

        self.exceptions["BasicException"] = BuiltinException(BasicException)

        for function in program.functions.values():
            self.functions[function.name] = function

        for exception in program.exceptions.values():
            self.exceptions[exception.name] = exception

        main_call = FunctionCall(position=self.functions["main"].position,
                                 name="main",
                                 arguments=[])
        main_call.accept(self)

    def visit_function(self, function_def: Function):
        eval_arguments, call_position = self._consume_last_result()

        if len(eval_arguments) != len(function_def.parameters):
            raise WrongNumberOfArguments(function_def.name,
                                         len(eval_arguments),
                                         len(function_def.parameters),
                                         call_position)

        call_context = FunctionContext(function_def.name)
        self.context_stack.append(call_context)
        context = self.context_stack[-1]

        for param, value in zip(function_def.parameters, eval_arguments):
            if not context.declare_variable(param.name, value):
                raise VariableAlreadyDeclaredError(param.name, param.position)

        function_def.statement_block.accept(self)
        if self.break_flag or self.continue_flag:
            raise LoopControlOutsideLoopError("Break" if self.break_flag else "Continue")

        if self.exception_to_throw:
            self.context_stack.pop()
            return

        if function_def.return_type != Type.VoidType and not self.return_flag:
            raise ReturnStatementMissingError(function_def.name)

        if self.return_flag:
            if self.last_result is not None and function_def.return_type == Type.VoidType:
                raise ValueReturnInVoidFunctionError(function_def.name, call_position)

            if (return_type := VALUE_TO_TYPE_MAP.get(type(self.last_result))) != function_def.return_type:
                raise InvalidReturnedValueTypeException(return_type, function_def.return_type)

        self.context_stack.pop()
        self.return_flag = False

    def visit_exception(self, exception_def: CustomException):
        eval_arguments, throw_position = self._consume_last_result()

        context = self.context_stack[-1]
        context.push_scope()

        if len(eval_arguments) != len(exception_def.parameters):
            raise WrongNumberOfArguments(exception_def.name,
                                         len(eval_arguments),
                                         len(exception_def.parameters),
                                         throw_position.position)

        for param, value in zip(exception_def.parameters, eval_arguments):
            value_type = type(value)
            param_type = TYPE_TO_VALUE_MAP[param.type]

            if value_type != param_type:
                raise WrongExpressionTypeError(value_type, param_type, param.position)

            if not context.declare_variable(param.name, value):
                raise VariableAlreadyDeclaredError(param.name, param.position)

        eval_attributes = []
        for attr in exception_def.attributes:
            attr.accept(self)
            eval_attributes.append((attr.name, self._consume_last_result()))

        context.pop_scope()
        eval_attributes.append(("position", throw_position))
        self.exception_to_throw = RuntimeUserException(exception_def.name, eval_attributes)

    def visit_builtin_exception(self, builtin_exception: BuiltinException):
        arguments, throw_position = self._consume_last_result()
        arguments = [throw_position] + arguments
        self.exception_to_throw = builtin_exception.exception_object(*arguments)


    def visit_statement_block(self, statement_block: StatementBlock):
        context = self.context_stack[-1]
        context.push_scope()

        for statement in statement_block.statements:
            statement.accept(self)

            if self.return_flag:
                break

            self.last_result = None

            if self.break_flag or self.continue_flag or self.exception_to_throw:
                break

        context.pop_scope()

    def visit_attribute(self, attribute: Attribute):
        attribute.expression.accept(self)

    def visit_if_statement(self, if_statement: IfStatement):
        if_statement.condition.accept(self)

        if self.exception_to_throw:
            return

        condition_value = self._consume_last_result()
        condition_value_type = type(condition_value)

        if condition_value_type != bool:
            raise WrongExpressionTypeError(condition_value_type, bool, if_statement.condition.position)

        if condition_value:
            if_statement.if_block.accept(self)
            return

        for elif_condition, elif_block in if_statement.elif_statement:
            elif_condition.accept(self)

            if self.exception_to_throw:
                return

            elif_condition_value = self._consume_last_result()
            elif_condition_value_type = type(elif_condition_value)

            if elif_condition_value_type != bool:
                raise WrongExpressionTypeError(elif_condition_value_type, bool, elif_condition.position)

            if elif_condition_value:
                elif_block.accept(self)
                return

        if if_statement.else_block is not None:
            if_statement.else_block.accept(self)

    def visit_return_statement(self, return_statement: ReturnStatement):
        if return_statement.expression is not None:
            return_statement.expression.accept(self)

            if self.exception_to_throw:
                return

        self.return_flag = True

    def visit_try_catch_statement(self, try_catch_statement: TryCatchStatement):
        try_catch_statement.try_block.accept(self)

        if self.exception_to_throw:
            for catch in try_catch_statement.catch_statements:
                catch.accept(self)
                if self.catched:
                    self.catched = False
                    break

    def visit_catch_statement(self, catch: CatchStatement):
        exception = self.exception_to_throw
        context = self.context_stack[-1]

        if  catch.exception == "BasicException" or catch.exception == exception.name:
            context.push_scope()

            for attr_name, value in exception.attributes:
                if not context.add_attribute(catch.name, attr_name, value):
                    raise AttributeAlreadyDeclaredError(attr_name, catch.name, catch.position)

            self.exception_to_throw = None
            catch.block.accept(self)
            self.catched = True

            context.pop_scope()
            self.last_result = None

    def visit_while_statement(self, while_statement: WhileStatement):
        while_statement.condition.accept(self)

        if self.exception_to_throw:
            return

        condition_value = self._consume_last_result()
        condition_value_type = type(condition_value)

        if condition_value_type != bool:
            raise WrongExpressionTypeError(condition_value_type, bool, while_statement.condition.position)

        while condition_value:
            while_statement.block.accept(self)

            if self.break_flag or self.return_flag:
                self.break_flag = False
                break

            if self.continue_flag:
                self.continue_flag = False
                continue

            if self.exception_to_throw:
                break

            while_statement.condition.accept(self)

            if self.exception_to_throw:
                return

            condition_value = self._consume_last_result()

    def visit_throw_statement(self, throw_statement: ThrowStatement):
        exception_name = throw_statement.name

        eval_arguments = []
        for argument in throw_statement.args:
            argument.accept(self)

            if self.exception_to_throw:
                return

            eval_arguments.append(self._consume_last_result())

        self.last_result = eval_arguments, throw_statement.position

        if exception_def := self.exceptions.get(exception_name):
            exception_def.accept(self)
        else:
            raise UndefinedExceptionError(exception_name, throw_statement.position)

    def visit_function_call(self, function_call: FunctionCall):
        function_name = function_call.name

        if len(self.context_stack) >= self.recursion_limit:
            raise RecursionTooDeepError(function_call.position)

        eval_arguments = []
        for argument in function_call.arguments:
            argument.accept(self)

            if self.exception_to_throw:
                return

            eval_arguments.append(self._consume_last_result())

        self.last_result = eval_arguments, function_call.position

        if function_def := self.functions.get(function_name):
            function_def.accept(self)
        else:
            raise UnknownFunctionCallError(function_name, function_call.position)

    def visit_builtin_function(self, builtin_function: BuiltinFunction):
        builtin_function.handler()

    def visit_assignment_statement(self, assigment_statement: AssignmentStatement):
        assigment_statement.expression.accept(self)

        if self.exception_to_throw:
            return

        name = assigment_statement.name
        value = self._consume_last_result()
        value_type = type(value)

        context = self.context_stack[-1]
        if (declared_variable := context.get_variable(name)) is not None:
            variable_type = type(declared_variable)
            if variable_type != value_type:
                raise WrongExpressionTypeError(value_type,
                                               variable_type,
                                               assigment_statement.expression.position)

            context.assign_value(name, value)
        else:
            if not context.declare_variable(name, value):
                raise VariableAlreadyDeclaredError(name, assigment_statement.position)

    def visit_or_expression(self, or_expression: OrExpression):
        or_expression.left.accept(self)

        if self.exception_to_throw:
            return

        left = self._assert_bool(self._consume_last_result(), or_expression.left.position)

        if left:
            self.last_result = True
        else:
            or_expression.right.accept(self)

            if self.exception_to_throw:
                return

            right = self._assert_bool(self._consume_last_result(), or_expression.right.position)
            self.last_result = right

    def visit_and_expression(self, and_expression: AndExpression):
        and_expression.left.accept(self)

        if self.exception_to_throw:
            return

        left = self._assert_bool(self._consume_last_result(), and_expression.left.position)

        if not left:
            self.last_result = False
        else:
            and_expression.right.accept(self)

            if self.exception_to_throw:
                return

            right = self._assert_bool(self._consume_last_result(), and_expression.right.position)

            self.last_result = right

    def visit_casted_expression(self, casted_expression: CastedExpression):
        casted_expression.expression.accept(self)

        if self.exception_to_throw:
            return

        self._cast_expression(casted_expression.to_type, casted_expression.position)

    def visit_negated_expression(self, negated_expression: NegatedExpression):
        self._evaluate_unary_expression(
            expression=negated_expression.expression,
            expected_types=bool,
            position=negated_expression.position,
            operator_fn=lambda v: not v
        )

    def visit_unary_minus_expression(self, unary_minus_expression: UnaryMinusExpression):
        self._evaluate_unary_expression(
            expression=unary_minus_expression.expression,
            expected_types=[int, float],
            position=unary_minus_expression.position,
            operator_fn=lambda v: -v
        )

    def visit_attribute_call(self, attribute_call: AttributeCall):
        context = self.context_stack[-1]
        attr_name = attribute_call.attr_name
        var_name = attribute_call.var_name

        if (attribute := context.get_attribute(var_name, attr_name)) is None:
            raise UndefinedAttributeError(attribute_call.attr_name, var_name, attribute_call.position)

        self.last_result = attribute

    def visit_variable(self, variable: Variable):
        context = self.context_stack[-1]
        if (variable_value := context.get_variable(variable.name)) is None:
            raise UndefinedVariableError(variable.name, variable.position)

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
        self._evaluate_arithmetic_expression(
            expression=multiply_expression,
            operator_func=mul,
            allowed_types=[int, float]
        )

    def visit_divide_expression(self, divide_expression: DivideExpression):
        safe_divide_with_position = lambda x, y: self._safe_divide(x, y, divide_expression.position)
        self._evaluate_arithmetic_expression(
            expression=divide_expression,
            operator_func=safe_divide_with_position,
            allowed_types=[int, float]
        )

    def visit_modulo_expression(self, modulo_expression: ModuloExpression):
        self._evaluate_arithmetic_expression(
            expression=modulo_expression,
            operator_func=mod,
            allowed_types=[int, float]
        )

    def visit_plus_expression(self, plus_expression: PlusExpression):
        self._evaluate_arithmetic_expression(
            expression=plus_expression,
            operator_func=add,
            allowed_types=[int, float, str]
        )

    def visit_minus_expression(self, minus_expression: MinusExpression):
        self._evaluate_arithmetic_expression(
            expression=minus_expression,
            operator_func=sub,
            allowed_types=[int, float]
        )

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

    def _evaluate_unary_expression(
            self,
            expression: Expression,
            expected_types: list[type] | type,
            position: Position,
            operator_fn: Callable
    ):
        expression.accept(self)

        if self.exception_to_throw:
            return

        value = self._consume_last_result()
        self._check_type(value, expected_types, position)
        self.last_result = operator_fn(value)

    def _visit_binary_comparison(self, expr, op_func):
        expr.left.accept(self)

        if self.exception_to_throw:
            return

        left = self._consume_last_result()
        left_type = type(left)

        expr.right.accept(self)

        if self.exception_to_throw:
            return

        right = self._consume_last_result()
        right_type = type(right)

        if left_type != right_type:
            raise NotMatchingTypesInBinaryExpression(left_type, right_type)

        self.last_result = op_func(left, right)

    def visit_break_statement(self, break_statement: BreakStatement):
        self.break_flag = True

    def visit_continue_statement(self, continue_statement: ContinueStatement):
        self.continue_flag = True

    def _consume_last_result(self):
        if self.last_result is None:
            raise VoidFunctionUsedAsValueError()

        value = self.last_result
        self.last_result = None
        return value

    @staticmethod
    def _assert_bool(value: str | bool | float | int, position: Position) -> bool:
        value_type = type(value)
        if value_type != bool:
            raise WrongExpressionTypeError(value_type, bool, position)
        return value

    @staticmethod
    def _check_type(value: str | bool | float | int,
                    expected_types: list[type] | type,
                    position: Position):
        value_type = type(value)
        if isinstance(expected_types, list):
            if value_type not in expected_types:
                raise WrongExpressionTypeError(value_type, expected_types, position)
        else:
            if value_type != expected_types:
                raise WrongExpressionTypeError(value_type, expected_types, position)
        return value

    @staticmethod
    def _safe_divide(x: int | float, y: int | float, position: Position) -> int | float:
        if y == 0:
            raise DivisionByZeroError(position)
        x_type = type(x)
        return x // y if x_type == int else x / y

    def _cast_expression(self, to_type: Type, position: Position):
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
            raise WrongExpressionTypeError(origin_type,
                                           [int, float, str, bool],
                                           position)

        self.last_result = cast_func(to_type, value)

    @staticmethod
    def _check_numeric_type(value_type: Type):
        if value_type not in (Type.IntType, Type.FloatType):
            raise WrongExpressionTypeError(value_type)

    @staticmethod
    def _cast_int(to_type: Type, value: int):
        cast_map = {
            Type.IntType: lambda v: v,
            Type.FloatType: float,
            Type.BoolType: lambda v: v != 0,
            Type.StringType: str,
        }
        return cast_map[to_type](value)

    @staticmethod
    def _cast_float(to_type: Type, value: float):
        cast_map = {
            Type.IntType: int,
            Type.FloatType: lambda v: v,
            Type.BoolType: lambda v: v != 0.0,
            Type.StringType: str,
        }
        return cast_map[to_type](value)

    @staticmethod
    def _cast_boolean(to_type: Type, value: bool):
        cast_map = {
            Type.IntType: lambda v: 1 if v else 0,
            Type.FloatType: lambda v: 1.0 if v else 0.0,
            Type.BoolType: lambda v: v,
            Type.StringType: lambda v: "true" if v else "false",
        }

        return cast_map[to_type](value)

    @staticmethod
    def _cast_string(to_type: Type, value: str):
        cast_map = {
            Type.IntType: int,
            Type.FloatType: float,
            Type.BoolType: lambda v: v != '',
            Type.StringType: lambda v: v,
        }
        return cast_map[to_type](value)

    def _evaluate_arithmetic_expression(
            self,
            expression: Expression,
            operator_func: Callable,
            allowed_types: list[type],
    ):
        left_expr = expression.left
        right_expr = expression.right

        left_expr.accept(self)

        if self.exception_to_throw:
            return

        left = self._consume_last_result()
        left_type = type(left)
        if left_type not in allowed_types:
            raise WrongExpressionTypeError(left_type, allowed_types, left_expr.position)

        right_expr.accept(self)

        if self.exception_to_throw:
            return

        right = self._consume_last_result()
        right_type = type(right)
        if right_type not in allowed_types:
            raise WrongExpressionTypeError(right_type, allowed_types, right_expr.position)

        if left_type != right_type:
            raise NotMatchingTypesInBinaryExpression(left_type, right_type, left_expr.position)

        result = operator_func(left, right)
        result_type = type(result)

        if result_type != bool and result_type != str:
            if abs(result) >= sys.maxsize:
                raise ValueOverflowError(result, expression.position)

            result = round(result, self.number_precision)

        self.last_result = result

    def builtin_print(self) -> None:
        args, position = self._consume_last_result()
        transform = lambda x: "true" if x is True else "false" if x is False else x
        print(*map(transform, args))

    def builtin_input(self):
        self.last_result = input()


def main():
    input_code = """
        exception ValueError(int value) {
            message: string = "Wrong value="+value to string +" - should be higher than 0";
            value: int = value;
        }

        $
        Block
        comment
        $

        bool is_even(int number){
            return number % 2 == 0;
        }

        void print_even_if_not_divisible_by_5(int number){
            a = 5;
            while (number > 0) {
                # comment
                if (number % 5 == 0) {
                    number = number - 1;
                    continue;
                }elif (is_even(number)) {
                    number = number - 1;
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
                print("Error: ", e.message, "\\n \\t Value=", e.value, e.position, "\\n");
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
