from io import StringIO

import pytest

from src.ast.core_structures import Function, CustomException
from src.ast.expressions import *
from src.ast.statemens import *
from src.errors.parser_errors import UnexpectedToken, ExpectedDeclarationError
from src.lexer.lexer import DefaultLexer
from src.ast.position import Position
from src.lexer.source import Source
from src.lexer.token_ import TokenType
from src.parser.parser import Parser


def test_parse_program():
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
    stream = StringIO(input_code, None)
    source = Source(stream)
    lexer = DefaultLexer(source)
    program = Parser(lexer).get_program()

    assert len(program.functions) == 3
    assert len(program.exceptions) == 1
    assert program.functions.get("is_even")
    assert program.functions.get("print_even_if_not_divisible_by_5")
    assert program.functions.get("main")
    assert program.exceptions.get("ValueError")

    is_even_function = program.functions.get("is_even")
    print_even_function = program.functions.get("print_even_if_not_divisible_by_5")
    main_function = program.functions.get("main")
    value_error_exception = program.exceptions.get("ValueError")

    # is_even function
    assert isinstance(is_even_function, Function)
    assert is_even_function.name == "is_even"
    assert is_even_function.position == Position(11, 5)
    assert is_even_function.return_type == Type.BoolType

    assert len(is_even_function.parameters) == 1
    assert isinstance(is_even_function.parameters[0], Parameter)
    assert is_even_function.parameters[0].name == "number"
    assert is_even_function.parameters[0].type == Type.IntType

    assert isinstance(is_even_function.statement_block, StatementBlock)
    assert len(is_even_function.statement_block.statements) == 1
    return_statement = is_even_function.statement_block.statements[0]
    assert isinstance(return_statement, ReturnStatement)
    assert return_statement.position == Position(12, 9)

    equals_expression = return_statement.expression
    assert isinstance(equals_expression, EqualsExpression)
    assert equals_expression.position == Position(12, 16)

    modulo_expression = equals_expression.left
    assert isinstance(modulo_expression, ModuloExpression)
    assert modulo_expression.position == Position(12, 16)

    assert isinstance(modulo_expression.left, Variable)
    assert modulo_expression.left.name == "number"
    assert modulo_expression.left.position == Position(12, 16)

    assert isinstance(modulo_expression.right, IntLiteral)
    assert modulo_expression.right.position == Position(12, 25)
    assert modulo_expression.right.value == 2

    assert isinstance(equals_expression.right, IntLiteral)
    assert equals_expression.right.position == Position(12, 30)
    assert equals_expression.right.value == 0

    # print_even_if_not_divisible_by_5 function
    assert isinstance(print_even_function, Function)
    assert print_even_function.name == "print_even_if_not_divisible_by_5"
    assert print_even_function.position == Position(15, 5)
    assert print_even_function.return_type == Type.VoidType

    assert len(print_even_function.parameters) == 1
    assert isinstance(print_even_function.parameters[0], Parameter)
    assert print_even_function.parameters[0].name == "number"
    assert print_even_function.parameters[0].type == Type.IntType

    assert isinstance(print_even_function.statement_block, StatementBlock)
    assert len(print_even_function.statement_block.statements) == 1
    while_statement = print_even_function.statement_block.statements[0]
    assert isinstance(while_statement, WhileStatement)
    assert while_statement.position == Position(16, 9)

    condition = while_statement.condition
    assert isinstance(condition, GreaterThanExpression)
    assert condition.position == Position(16, 16)

    assert isinstance(condition.left, Variable)
    assert condition.left.position == Position(16, 16)
    assert condition.left.name == "number"

    assert isinstance(condition.right, IntLiteral)
    assert condition.right.position == Position(16, 25)
    assert condition.right.value == 0

    assert isinstance(while_statement.block, StatementBlock)
    assert len(while_statement.block.statements) == 1
    if_statement = while_statement.block.statements[0]
    assert isinstance(if_statement, IfStatement)
    assert if_statement.position == Position(18, 13)

    if_condition = if_statement.condition
    assert isinstance(if_condition, EqualsExpression)
    assert if_condition.position == Position(18, 17)

    modulo_expression = if_condition.left
    assert isinstance(modulo_expression, ModuloExpression)
    assert modulo_expression.position == Position(18, 17)
    assert isinstance(modulo_expression.left, Variable)
    assert modulo_expression.left.position == Position(18, 17)
    assert modulo_expression.left.name == "number"
    assert isinstance(modulo_expression.right, IntLiteral)
    assert modulo_expression.right.position == Position(18, 26)
    assert modulo_expression.right.value == 5

    assert isinstance(if_condition.right, IntLiteral)
    assert if_condition.right.position == Position(18, 31)
    assert if_condition.right.value == 0

    assert isinstance(if_statement.if_block, StatementBlock)
    assert len(if_statement.if_block.statements) == 1
    break_statement = if_statement.if_block.statements[0]
    assert isinstance(break_statement, BreakStatement)
    assert break_statement.position == Position(19, 17)

    assert len(if_statement.elif_statement) == 1
    elif_condition, elif_block = if_statement.elif_statement[0]
    assert isinstance(elif_condition, FunctionCall)
    assert elif_condition.position == Position(20, 20)
    assert elif_condition.name == "is_even"

    assert len(elif_condition.arguments) == 1
    argument = elif_condition.arguments[0]
    assert isinstance(argument, Variable)
    assert argument.position == Position(20, 28)
    assert argument.name == "number"

    assert isinstance(elif_block, StatementBlock)
    assert len(elif_block.statements) == 1
    continue_statement = elif_block.statements[0]
    assert isinstance(continue_statement, ContinueStatement)
    assert continue_statement.position == Position(21, 17)

    assert isinstance(if_statement.else_block, StatementBlock)
    assert len(if_statement.else_block.statements) == 2
    func_call = if_statement.else_block.statements[0]
    assert isinstance(func_call, FunctionCall)
    assert func_call.position == Position(23, 17)
    assert func_call.name == "print"
    assert len(func_call.arguments) == 2

    string_literal = func_call.arguments[0]
    assert isinstance(string_literal, StringLiteral)
    assert string_literal.position == Position(23, 23)
    assert string_literal.value == "x: "

    var = func_call.arguments[1]
    assert isinstance(var, Variable)
    assert var.position == Position(23, 30)
    assert var.name == "number"

    assigment = if_statement.else_block.statements[1]
    assert isinstance(assigment, AssignmentStatement)
    assert assigment.position == Position(24, 17)
    assert assigment.name == "number"

    minus_expression = assigment.expression
    assert isinstance(minus_expression, MinusExpression)
    assert minus_expression.position == Position(24, 26)
    assert isinstance(minus_expression.left, Variable)
    assert minus_expression.left.name == "number"
    assert minus_expression.left.position == Position(24, 26)

    assert isinstance(minus_expression.right, IntLiteral)
    assert minus_expression.right.position == Position(24, 35)
    assert minus_expression.right.value == 1

    # main function
    assert isinstance(main_function, Function)
    assert main_function.name == "main"
    assert main_function.position == Position(28, 5)
    assert main_function.return_type == Type.VoidType
    assert len(main_function.parameters) == 0

    assert isinstance(main_function.statement_block, StatementBlock)
    assert len(main_function.statement_block.statements) == 1
    try_statement = main_function.statement_block.statements[0]
    assert isinstance(try_statement, TryCatchStatement)
    assert try_statement.position == Position(29, 9)
    assert isinstance(try_statement.try_block, StatementBlock)
    assert len(try_statement.try_block.statements) == 3

    assignment_statement = try_statement.try_block.statements[0]
    assert isinstance(assignment_statement, AssignmentStatement)
    assert assignment_statement.position == Position(30, 13)
    assert assignment_statement.name == "x"

    casted_expression = assignment_statement.expression
    assert isinstance(casted_expression, CastedExpression)
    assert casted_expression.position == Position(30, 17)
    assert casted_expression.to_type == Type.IntType

    function_call = casted_expression.expression
    assert isinstance(function_call, FunctionCall)
    assert function_call.position == Position(30, 17)
    assert function_call.name == "input"
    assert len(function_call.arguments) == 0

    if_statement = try_statement.try_block.statements[1]
    assert isinstance(if_statement, IfStatement)
    assert if_statement.position == Position(31, 13)

    condition = if_statement.condition
    assert isinstance(condition, LessThanOrEqualsExpression)
    assert condition.position == Position(31, 17)

    assert isinstance(condition.left, Variable)
    assert condition.left.position == Position(31, 17)
    assert condition.left.name == "x"

    assert isinstance(condition.right, IntLiteral)
    assert condition.right.position == Position(31, 22)
    assert condition.right.value == 0

    assert isinstance(if_statement.if_block, StatementBlock)
    assert len(if_statement.if_block.statements) == 1
    throw_statement = if_statement.if_block.statements[0]
    assert isinstance(throw_statement, ThrowStatement)
    assert throw_statement.position == Position(32, 17)
    assert throw_statement.name == "ValueError"

    assert len(throw_statement.args) == 1
    variable = throw_statement.args[0]
    assert isinstance(variable, Variable)
    assert variable.position == Position(32, 34)
    assert variable.name == "x"

    function_call = try_statement.try_block.statements[2]
    assert isinstance(function_call, FunctionCall)
    assert function_call.position == Position(34, 13)
    assert function_call.name == "print_even_if_not_divisible_by_5"
    assert len(function_call.arguments) == 1

    variable = function_call.arguments[0]
    assert isinstance(variable, Variable)
    assert variable.position == Position(34, 46)
    assert variable.name == "x"

    assert len(try_statement.catch_statements) == 1
    catch_statement = try_statement.catch_statements[0]
    assert isinstance(catch_statement, CatchStatement)
    assert catch_statement.position == Position(35, 10)
    assert catch_statement.exception == "BaseException"
    assert catch_statement.name == "e"

    assert isinstance(catch_statement.block, StatementBlock)
    assert len(catch_statement.block.statements) == 1
    function_call = catch_statement.block.statements[0]

    assert isinstance(function_call, FunctionCall)
    assert function_call.position == Position(36, 13)
    assert function_call.name == "print"
    assert len(function_call.arguments) == 6

    arg0 = function_call.arguments[0]
    assert isinstance(arg0, StringLiteral)
    assert arg0.position == Position(36, 19)
    assert arg0.value == "Error: "

    arg1 = function_call.arguments[1]
    assert isinstance(arg1, AttributeCall)
    assert arg1.position == Position(36, 30)
    assert arg1.var_name == "e"
    assert arg1.attr_name == "message"

    arg2 = function_call.arguments[2]
    assert isinstance(arg2, StringLiteral)
    assert arg2.position == Position(36, 41)
    assert arg2.value == "\n \t Value="

    arg3 = function_call.arguments[3]
    assert isinstance(arg3, AttributeCall)
    assert arg3.position == Position(36, 57)
    assert arg3.var_name == "e"
    assert arg3.attr_name == "value"

    arg4 = function_call.arguments[4]
    assert isinstance(arg4, AttributeCall)
    assert arg4.position == Position(36, 66)
    assert arg4.var_name == "e"
    assert arg4.attr_name == "line"

    arg5 = function_call.arguments[5]
    assert isinstance(arg5, StringLiteral)
    assert arg5.position == Position(36, 74)
    assert arg5.value == "\n"

    # exception ValueError
    assert isinstance(value_error_exception, CustomException)
    assert value_error_exception.name == "ValueError"
    assert value_error_exception.position == Position(2, 5)

    assert len(value_error_exception.parameters) == 1
    assert isinstance(value_error_exception.parameters[0], Parameter)
    assert value_error_exception.parameters[0].name == "value"
    assert value_error_exception.parameters[0].type == Type.IntType

    assert len(value_error_exception.attributes) == 1
    exception_attribute = value_error_exception.attributes[0]
    assert isinstance(exception_attribute, Attribute)
    assert exception_attribute.name == "message"
    assert exception_attribute.type == Type.StringType

    attribute_expression = exception_attribute.expression
    assert isinstance(attribute_expression, PlusExpression)
    assert attribute_expression.position == Position(3, 27)

    plus_expression = attribute_expression.left
    assert isinstance(plus_expression, PlusExpression)
    assert plus_expression.position == Position(3, 27)
    assert isinstance(plus_expression.left, StringLiteral)
    assert plus_expression.left.position == Position(3, 27)
    assert plus_expression.left.value == "Wrong value="

    casted_expression = plus_expression.right
    assert isinstance(casted_expression, CastedExpression)
    assert casted_expression.position == Position(3, 42)
    assert casted_expression.to_type == Type.StringType
    assert isinstance(casted_expression.expression, Variable)
    assert casted_expression.expression.position == Position(3, 42)
    assert casted_expression.expression.name == "value"

    assert isinstance(attribute_expression.right, StringLiteral)
    assert attribute_expression.right.position == Position(3, 59)
    assert attribute_expression.right.value == " - should be higher than 0: "


def test_parse_program_raises_when_program_cant_be_parsed():
    input_code = """
    main();
    void main(){
        x = 5;
    }
    """
    stream = StringIO(input_code, None)
    source = Source(stream)
    lexer = DefaultLexer(source)

    with pytest.raises(ExpectedDeclarationError) as exception_info:
        Parser(lexer).get_program()

    assert exception_info.value.position == Position(2, 5)
    assert exception_info.value.message == ("Expected Function or Exception declaration, "
                                            "got unexpected declaration type")


def test_parse_program_raises_when_function_cant_be_parsed():
    input_code = """
    void main(){
        x = 5
    }
    """
    stream = StringIO(input_code, None)
    source = Source(stream)
    lexer = DefaultLexer(source)

    with pytest.raises(UnexpectedToken) as exception_info:
        Parser(lexer).get_program()

    assert exception_info.value.position == Position(4, 5)
    assert exception_info.value.message == (f'Unexpected token - expected "{TokenType.SEMICOLON}"'
                                            f', got "{TokenType.RIGHT_CURLY_BRACKET}"')
