import contextlib
import io
from unittest.mock import patch

import pytest

from src.errors.interpreter_errors import *
from src.interpreter.executor import ProgramExecutor
from src.lexer.lexer import DefaultLexer
from src.lexer.source import Source
from src.parser.parser import Parser


def execute_program(input_code: str) -> str:
    stream = io.StringIO(input_code)
    source = Source(stream)
    lexer = DefaultLexer(source)
    program = Parser(lexer).get_program()
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        ProgramExecutor().execute(program)

    return output.getvalue().strip()


@pytest.mark.parametrize(
    "args, expected", [
        ("8 ", "8"),
        ("1.5", "1.5"),
        ("\"text\"", "text"),
        ("true", "true"),
        ("\"text1\", \"text2\"", "text1 text2"),
    ]
)
def test_should_execute_builtin_print(args, expected):
    input_code = f"""
    void main(){{
        print({args});
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == expected


@pytest.mark.parametrize(
    "value, expected", [
        (8, "8"),
        (1.5, "1.5"),
        ("text", "text"),
    ]
)
def test_should_execute_builtin_input(value, expected):
    input_code = f"""
    void main(){{
        print(input() to string);
    }}
    """
    with patch("builtins.input", return_value=value):
        captured_output = execute_program(input_code)

    assert captured_output == expected


@pytest.mark.parametrize(
    "casted_expression, expected", [
        ("2 to int", "2"),
        ("2 to float", "2.0"),
        ("2 to bool", "true"),
        ("0 to bool", "false"),
        ("2 to string", "2"),
        ("2.6 to int", "2"),
        ("2.6 to float", "2.6"),
        ("2.6 to bool", "true"),
        ("0.0 to bool", "false"),
        ("2.6 to string", "2.6"),
        ("true to int", "1"),
        ("false to int", "0"),
        ("true to float", "1.0"),
        ("false to float", "0.0"),
        ("true to bool", "true"),
        ("false to bool", "false"),
        ("true to string", "true"),
        ("false to string", "false"),
        ("\"2\" to int", "2"),
        ("\"2.6\" to float", "2.6"),
        ("\"text\" to bool", "true"),
        ("\"\" to bool", "false"),
        ("\"text\" to string", "text")
    ]
)
def test_cast_simple_types(casted_expression, expected):
    input_code = f"""
    void main(){{
        print({casted_expression});
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == expected


@pytest.mark.parametrize(
    "value, expected", [
        ("2", "2"),
        ("3.44", "3.44"),
        ("true", "true"),
        ("\"text\"", "text")
    ]
)
def test_declare_variable(value, expected):
    input_code = f"""
    void main(){{
        x = {value};
        print(x);
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == expected


@pytest.mark.parametrize(
    "a, b, expected", [
        (2, 2, "4"),
        (1.4, 1.3, "2.7"),
        ("\"text\"", "\"another\"", "textanother")
    ]
)
def test_execute_plus_expression(a, b, expected):
    input_code = f"""
    void main(){{
        x = {a} + {b};
        print(x);
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == expected


@pytest.mark.parametrize(
    "a, b, expected", [
        (2, 2, "0"),
        (1.4, 1.3, "0.1"),
    ]
)
def test_execute_minus_expression(a, b, expected):
    input_code = f"""
    void main(){{
        x = {a} - {b};
        print(x);
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == expected


@pytest.mark.parametrize(
    "a, b, expected", [
        (2, 2, "1"),
        (2, 3, "0"),
        (5, 3, "1"),
        (1.5, 0.3, "5.0"),
        (1.0, 3.0, "0.333333333333333"),
    ]
)
def test_execute_divide_expression(a, b, expected):
    input_code = f"""
    void main(){{
        x = {a} / {b};
        print(x);
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == expected


@pytest.mark.parametrize(
    "a, b, expected", [
        (2, 2, "4"),
        (2, 3, "6"),
        (1.5, 2.0, "3.0"),
        (2.0, 0.3, "0.6"),
    ]
)
def test_execute_multiply_expression(a, b, expected):
    input_code = f"""
    void main(){{
        x = {a} * {b};
        print(x);
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == expected


@pytest.mark.parametrize(
    "a, b, expected", [
        (2, 2, "0"),
        (2, 3, "2"),
        (1.5, 2.0, "1.5"),
        (2.0, 0.3, "0.2"),
    ]
)
def test_execute_modulo_expression(a, b, expected):
    input_code = f"""
    void main(){{
        x = {a} % {b};
        print(x);
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == expected


@pytest.mark.parametrize(
    "a, b", [
        (2, 2.0),
        (1, 1.3),
        ("\"text\"", 1)
    ]
)
def test_should_raise_when_type_missmatch_in_binary_expression(a, b):
    input_code = f"""
    void main(){{
        x = {a} + {b};
        print(x);
    }}
    """
    with pytest.raises(NotMatchingTypesInBinaryExpression):
        execute_program(input_code)


@pytest.mark.parametrize(
    "expression, expected", [
        ("5.0 > 3.0", "true"),
        ("2.0 > 3.0", "false"),
        ("5 > 3", "true"),
        ("2 > 3", "false"),
        ("2.0 < 3.0", "true"),
        ("5.0 < 3.0", "false"),
        ("2 < 3", "true"),
        ("5 < 3", "false"),
        ("3.0 <= 3.0", "true"),
        ("5.0 <= 3.0", "false"),
        ("3.0 >= 3.0", "true"),
        ("2.0 >= 3.0", "false"),
        ("3 <= 3", "true"),
        ("5 <= 3", "false"),
        ("3 >= 3", "true"),
        ("2 >= 3", "false"),
        ("5 == 5", "true"),
        ("5 == 3", "false"),
        ("5.0 == 3.0", "false"),
        ("5.0 == 5.0", "true"),
        ("\"abc\" == \"abc\"", "true"),
        ("\"abc\" == \"abcd\"", "false"),
        ("true == true", "true"),
        ("false == false", "true"),
        ("true == false", "false"),
        ("false == true", "false"),
        ("5 != 3", "true"),
        ("5 != 5", "false"),
        ("5.0 != 3.0", "true"),
        ("5.0 != 5.0", "false"),
        ("\"abc\" != \"abc\"", "false"),
        ("\"abc\" != \"abcd\"", "true"),
        ("true != false", "true"),
        ("false != true", "true"),
        ("false != false", "false"),
        ("true != true", "false"),
    ]
)
def test_execute_relational_expressions(expression, expected):
    input_code = f"""
    void main(){{
        print({expression});
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == expected


@pytest.mark.parametrize(
    "expression, expected", [
        ("true and true", "true"),
        ("false and true", "false"),
        ("true and false", "false"),
        ("false and false", "false"),
        ("true or true", "true"),
        ("false or true", "true"),
        ("true or false", "true"),
        ("false or false", "false"),
    ]
)
def test_execute_logical_expressions(expression, expected):
    input_code = f"""
    void main(){{
        print({expression});
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == expected


@pytest.mark.parametrize(
    "expression, expected", [
        ("not true", "false"),
        ("not false", "true"),
        ("not (1==2)", "true"),
        ("not (1!=2)", "false"),
        ("not (1>=2)", "true"),
        ("not (1<=2)", "false"),
        ("not (1<2)", "false"),
        ("not (1>2)", "true"),
        ("!true", "false"),
        ("!false", "true"),
        ("!(1==2)", "true"),
        ("!(1!=2)", "false"),
        ("!(1>=2)", "true"),
        ("!(1<=2)", "false"),
        ("!(1<2)", "false"),
        ("!(1>2)", "true"),
    ]
)
def test_execute_negated_expressions(expression, expected):
    input_code = f"""
    void main(){{
        print({expression});
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == expected


@pytest.mark.parametrize(
    "expression, expected", [
        ("-7", "-7"),
        ("-7+1", "-6"),
        ("-(7+1)", "-8"),
    ]
)
def test_execute_negated_expressions(expression, expected):
    input_code = f"""
    void main(){{
        print({expression});
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == expected


@pytest.mark.parametrize(
    "a, b, expected", [
        (3, 5, "5")
    ]
)
def test_assigment_should_change_value_of_variable(a, b, expected):
    input_code = f"""
    void main(){{
        x = {a};
        x = {b};
        print(x);
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == expected


@pytest.mark.parametrize(
    "a, b", [
        (3, 5.0),
        (3, "true"),
        (3, "\"3\""),
        (5.0, 3),
        (5.0, "true"),
        (5.0, "\"5.0\""),
        ("true", 3),
        ("true", 3.0),
        ("true", "\"true\""),
        ("\"3\"", 3),
        ("\"3\"", 3.0),
        ("\"3\"", "true"),
    ]
)
def test_variable_assignment_fails_with_wrong_type(a, b):
    input_code = f"""
    void main(){{
        x = {a};
        x = {b};
        print(x);
    }}
    """
    with pytest.raises(WrongExpressionTypeError):
        execute_program(input_code)


@pytest.mark.parametrize(
    "value, expected", [
        ("1", "if"),
        ("2", "elif"),
        ("3", "else"),
    ]
)
def test_execute_if_statement(value, expected):
    input_code = f"""
    void main(){{
        x = {value};
        if (x == 1){{
            print("if");
        }}elif(x == 2){{
            print("elif");
        }}else{{
            print("else");
        }}
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == expected


@pytest.mark.parametrize(
    "value, threshold, expected", [
        (1, 0, "0"),
        (5, 3, "3"),
        (2, 3, "2"),
        (2, 3, "2"),
    ]
)
def test_execute_while_statement(value, threshold, expected):
    input_code = f"""
    void main(){{
        x = {value};
        while(x > {threshold}){{
            x = x - 1;
        }}
        print(x);
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == expected


def test_while_statement_should_end_after_break():
    input_code = f"""
    void main(){{
        x = 5;
        while(x > 0){{
            print(x);
            x = x - 1;
            if(x == 1){{
                break;
                print("break");
            }}
        }}
        print(x);
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == "5\n4\n3\n2\n1"


def test_while_statement_should_skip_rest_of_statements_after_continue():
    input_code = f"""
    void main(){{
        x = 5;
        while(x > 0){{
            print(x);
            x = x - 1;
            if(x == 1){{
                continue;
                print("break");
            }}
        }}
        print(x);
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == "5\n4\n3\n2\n1\n0"


def test_execute_function_call():
    input_code = f"""
    int add(int x, int y){{
        return x+y;
    }}
    float func1(float x){{
        return x;
    }}
    bool func2(bool x){{
        return x;
    }}
    string func3(string x){{
        return x;
    }}
    void print_a(){{
       print("a");
    }}
    void main(){{
        a = add(1, 2);
        print(a);
        print(func1(2.5));
        print(func2(true));
        print(func3("text"));
        print_a();
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == "3\n2.5\ntrue\ntext\na"


def test_execute_function_call_should_reset_value_after_each_call():
    input_code = f"""
    float func1(float x){{
        return x;
    }}
    void main(){{
        func1(2.5);
        print(func1(3.0));
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == "3.0"


def test_execute_function_call_should_end_executing_statements_after_return():
    input_code = f"""
    float func1(float x){{
        return x;
        print("func1");
    }}
    void main(){{
        print(func1(3.0));
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == "3.0"


def test_execute_function_call_without_enough_parameters():
    input_code = f"""
    float func1(float x){{
        return x;
        print("func1");
    }}
    void main(){{
        print(func1());
    }}
    """
    with pytest.raises(WrongNumberOfArguments):
        execute_program(input_code)


@pytest.mark.parametrize(
    "func_type, value", [
        ("int", 3.0),
        ("int", "true"),
        ("int", "\"text\""),
        ("float", 3),
        ("float", "true"),
        ("float", "\"text\""),
        ("bool", 3),
        ("bool", 3.0),
        ("bool", "\"text\""),
        ("string", 3),
        ("string", 3.0),
        ("string", "true"),
    ]
)
def test_return_type_mismatch_raises_error(func_type, value):
    input_code = f"""
    {func_type} func1(){{
        return {value};
    }}
    void main(){{
        func1();
    }}
    """
    with pytest.raises(InvalidReturnTypeException):
        execute_program(input_code)


def test_recursion():
    input_code = f"""
    int fibonacci(int n){{
        if(n<3){{
            return 1;
        }}
        return fibonacci(n-2)+fibonacci(n-1);
    }}
    void main(){{
        print(fibonacci(15));
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == "610"


def test_should_raise_exception_when_recursion_is_too_deep():
    input_code = f"""
    int fibonacci(int n){{
        if(n<3){{
            return 1;
        }}
        return fibonacci(n-2)+fibonacci(n-1);
    }}
    void main(){{
        print(fibonacci(55) to string);
    }}
    """
    with pytest.raises(RecursionTooDeepError):
        execute_program(input_code)


def test_should_correctly_deduce_variable_scope():
    input_code = f"""
    void func1(int x){{
        print(x);
        if(x > 0){{
            x = 3;
            print(x);
            if(x > 0){{
                x = 2;
            }}
            print(x);
        }}
        print(x);
        
    }}
    void main(){{
        x = 5;
        print(x);
        func1(5);
        print(x);
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == "5\n5\n3\n2\n2\n5"


def test_should_throw_exception_when_variable_declared_in_inner_scope():
    input_code = f"""
    void func1(int x){{
        print(x);
        if(x > 0){{
            x = 3;
            print(x);
            if(x > 0){{
                x = 2;
                y = 2;
            }}
            print(y);
        }}
        print(x);

    }}
    void main(){{
        x = 5;
        print(x);
        func1(5);
        print(x);
    }}
    """
    with pytest.raises(UndefinedVariableError) as exception_info:
        execute_program(input_code)

    assert exception_info.value.message == 'Undefined variable "y" at Line 11, Column 19'


def test_execute_throw_custom_exception():
    input_code = f"""
    exception ValueError(int value) {{
        message: string = "Text value=" + value to string;
    }}
    void main(){{
        throw ValueError(3);
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == "\x1b[31mValueError at Line 6, Column 9: Text value=3\033[0m"


def test_execute_throw_custom_exception_from_within_function():
    input_code = f"""
    exception ValueError(int value) {{
        message: string = "Text value=" + value to string;
    }}
    void func1(){{
        throw ValueError(3);
        print("text after throw");
    }}
    void main(){{
        func1();
        print("after func1");
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == "\x1b[31mValueError at Line 6, Column 9: Text value=3\033[0m"


def test_execute_try_catch_statement():
    input_code = f"""
    exception ValueError(int value) {{
        message: string = "Text value=" + value to string;
    }}
    void func1(){{
        throw ValueError(3);
        print("text after throw");
    }}
    void main(){{
        try{{
            func1();
            print("after func1");
        }}catch(ValueError e){{
            print("after catch");
        }}
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == "after catch"


def test__get_access_to_attributes_in_catch_statement():
    input_code = f"""
    exception ValueError(int value) {{
        message: string = "Text value=" + value to string;
    }}
    void func1(){{
        throw ValueError(3);
        print("text after throw");
    }}
    void main(){{
        try{{
            func1();
            print("after func1");
        }}catch(ValueError e){{
            print(e.message, e.position);
        }}
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == "Text value=3 Line 6, Column 9"


def test_catch_custom_exception_using_builtin_base_exception():
    input_code = f"""
    exception ValueError(int value) {{
        message: string = "Text value=" + value to string;
    }}
    void func1(){{
        throw ValueError(3);
        print("text after throw");
    }}
    void main(){{
        try{{
            func1();
            print("after func1");
        }}catch(BasicException e){{
            print(e.message, e.position);
        }}catch(ValueError e){{
            print("from ValueError:", e.message, e.position);
        }}
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == "Text value=3 Line 6, Column 9"


def test_should_throw_exception_when_exception_class_is_not_matched():
    input_code = f"""
    exception ValueError(int value) {{
        message: string = "Text value=" + value to string;
    }}
    exception RandomError() {{
        message: string = "Text";
    }}
    void func1(){{
        throw ValueError(3);
        print("text after throw");
    }}
    void main(){{
        try{{
            func1();
            print("after func1");
        }}catch(RandomError e){{
            print(e.message, e.position);
        }}
    }}
    """
    captured_output = execute_program(input_code)
    assert captured_output == "\x1b[31mValueError at Line 9, Column 9: Text value=3\033[0m"


def test_should_raise_exception_when_missing_main_function():
    input_code = f"""
    void func1(){{
        x = 2;
    }}
    """
    with pytest.raises(MissingMainFunctionDeclaration):
        execute_program(input_code)


def test_should_raise_exception_when_variable_already_declared():
    input_code = f"""
    int func1(int x, float x){{
        x = 2;
    }}
    void main(){{
        func1(1, 1.0);
    }}
    """
    with pytest.raises(VariableAlreadyDeclaredError):
        execute_program(input_code)


def test_should_raise_exception_when_called_unknown_function():
    input_code = f"""
    void main(){{
        func1();
    }}
    """
    with pytest.raises(UnknownFunctionCallError):
        execute_program(input_code)


@pytest.mark.parametrize(
    "expr", [
        "true + true",
        "true - true",
        "true * true",
        "true / true",
        "true % true",
        "\"text\" - \"text\"",
        "\"text\" * \"text\"",
        "\"text\" / \"text\"",
        "\"text\" % \"text\"",
        "1 and 1",
        "1.0 and 1.0",
        "\"text\" and \"text\"",
        "1 or 1",
        "1.0 or 1.0",
        "\"text\" or \"text\"",
    ]
)
def test_should_raise_when_wrong_expression_type_for_operations(expr):
    input_code = f"""
    void main(){{
        a = {expr};
    }}
    """
    with pytest.raises(WrongExpressionTypeError):
        execute_program(input_code)


@pytest.mark.parametrize(
    "expr", [
        "1/0",
        "1.0/0.0"
    ]
)
def test_should_raise_when_divide_by_zero(expr):
    input_code = f"""
    void main(){{
        x = {expr};
    }}
    """
    with pytest.raises(DivisionByZeroError):
        execute_program(input_code)


def test_should_raise_when_throw_undefined_exception():
    input_code = f"""
    void main(){{
        throw RandomException();
    }}
    """
    with pytest.raises(UndefinedExceptionError):
        execute_program(input_code)

@pytest.mark.parametrize(
    "stmnt", [
        "break",
        "continue",
    ]
)
def test_should_raise_when_loop_control_outside_loop(stmnt):
    input_code = f"""
    int func1(int x){{
        {stmnt};
        return x;
    }}
    void main(){{
        func1(1);
    }}
    """
    with pytest.raises(LoopControlOutsideLoopError):
        execute_program(input_code)

def test_should_raise_when_call_non_existent_attribute():
    input_code = f"""
    exception ValueError(int value) {{
        message: string = "Text value=" + value to string;
    }}
    void func1(){{
        throw ValueError(3);
        print("text after throw");
    }}
    void main(){{
        try{{
            func1();
            print("after func1");
        }}catch(ValueError e){{
            print(e.number);
        }}
    }}
    """
    with pytest.raises(UndefinedAttributeError):
        execute_program(input_code)



def test_should_raise_when_no_value_to_read():
    input_code = f"""
    void func1(){{
        print("text after throw");
    }}
    void main(){{
        x = func1();
        print(x);
    }}
    """
    with pytest.raises(NoLastResultError):
        execute_program(input_code)


def test_should_raise_when_attribute_already_declared():
    input_code = f"""
    exception ValueError(int value) {{
        message: string = "Text value=" + value to string;
        message: string = "Text";
    }}
    void func1(){{
        throw ValueError(3);
        print("text after throw");
    }}
    void main(){{
        try{{
            func1();
            print("after func1");
        }}catch(ValueError e){{
            print(e.message);
        }}
    }}
    """
    with pytest.raises(AttributeAlreadyDeclaredError):
        execute_program(input_code)