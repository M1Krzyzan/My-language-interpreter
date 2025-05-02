from typing import List

import pytest
import token_generator
from src.ast.core_structures import Program
from src.ast.expressions import IntLiteral, BoolLiteral, RelationalExpression, Variable, AdditiveExpression, \
    MultiplicativeExpression
from src.ast.statemens import StatementBlock, Parameter, Attribute, AssignmentStatement, IfStatement, ReturnStatement, \
    FunctionCallStatement
from src.ast.types import ReturnType, Type
from src.errors.parser_error import UnexpectedToken, DeclarationExistsError, ExpectedExpressionError, \
    ExpectedSimpleTypeError
from src.lexer.position import Position
from src.lexer.token_ import TokenType, Token
from src.parser.parser import Parser
from tests.parser.mocked_lexer import MockedLexer


def parse_program(tokens: List[Token]) -> Program:
    return Parser(MockedLexer(tokens)).get_program()


def test_parse_program_raises_when_not_function_or_exception():
    """
    input:

    if(x==5){
        x = 0;
    }
    """
    input_tokens = token_generator.if_statement(
        condition=[
            token_generator.get_token(TokenType.IDENTIFIER, "x"),
            token_generator.get_token(TokenType.EQUAL_OPERATOR),
            token_generator.get_token(TokenType.INT_LITERAL, 5)
        ],
        if_block=[
            token_generator.get_token(TokenType.IDENTIFIER, "x"),
            token_generator.get_token(TokenType.ASSIGNMENT),
            token_generator.get_token(TokenType.INT_LITERAL, 0),
            token_generator.get_token(TokenType.SEMICOLON)
        ]
    )
    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(UnexpectedToken) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == f'Unexpected token - expected "{TokenType.ETX}", got "{TokenType.IF_KEYWORD}"'


def test_parse_function_definition():
    """
    input:

    void func1(float x, int y, bool z, string str){}
    int func2(){}
    float func3(){}
    string func4(){}
    """
    input_tokens = token_generator.function(
        name="func1",
        params=token_generator.parameters([
            (TokenType.FLOAT_KEYWORD, "x"),
            (TokenType.INT_KEYWORD, "y"),
            (TokenType.BOOL_KEYWORD, "z"),
            (TokenType.STRING_KEYWORD, "str")
        ]),
        return_type=TokenType.VOID_KEYWORD,
    )
    input_tokens += token_generator.function(
        name="func2",
        return_type=TokenType.INT_KEYWORD,
    )
    input_tokens += token_generator.function(
        name="func3",
        return_type=TokenType.FLOAT_KEYWORD,
    )
    input_tokens += token_generator.function(
        name="func4",
        return_type=TokenType.STRING_KEYWORD,
    )

    input_program = token_generator.get_program(input_tokens)

    program = parse_program(input_program)

    assert len(program.functions) == 4
    assert program.functions.get("func1", False)
    assert program.functions["func1"].return_type == ReturnType(TokenType.VOID_KEYWORD)
    assert len(program.functions["func1"].parameters) == 4
    assert program.functions["func1"].statement_block == StatementBlock([])

    assert program.functions.get("func2", False)
    assert program.functions["func2"].return_type == ReturnType(TokenType.INT_KEYWORD)
    assert len(program.functions["func2"].parameters) == 0
    assert program.functions["func1"].statement_block == StatementBlock([])

    assert program.functions.get("func3", False)
    assert program.functions["func3"].return_type == ReturnType(TokenType.FLOAT_KEYWORD)
    assert len(program.functions["func3"].parameters) == 0
    assert program.functions["func1"].statement_block == StatementBlock([])

    assert program.functions.get("func4", False)
    assert program.functions["func4"].return_type == ReturnType(TokenType.STRING_KEYWORD)
    assert len(program.functions["func4"].parameters) == 0
    assert program.functions["func1"].statement_block == StatementBlock([])


def test_parse_function_raises_when_missing_left_round_bracket():
    """
    input:

    void func1 int x){}
    """
    input_tokens = token_generator.function(
        name="func1",
        params=token_generator.parameters([(TokenType.INT_KEYWORD, "x"), ]),
        return_type=TokenType.VOID_KEYWORD,
    )
    input_tokens.remove(token_generator.get_token(TokenType.LEFT_ROUND_BRACKET))

    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(UnexpectedToken) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == (f'Unexpected token - expected "{TokenType.LEFT_ROUND_BRACKET}"'
                                            f', got "{TokenType.INT_KEYWORD}"')


def test_parse_function_raises_when_missing_right_round_bracket():
    """
    input:

    void func1 (int x {}
    """
    input_tokens = token_generator.function(
        name="func1",
        params=token_generator.parameters([(TokenType.INT_KEYWORD, "x"), ]),
        return_type=TokenType.VOID_KEYWORD,
    )
    input_tokens.remove(token_generator.get_token(TokenType.RIGHT_ROUND_BRACKET))

    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(UnexpectedToken) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == (f'Unexpected token - expected "{TokenType.RIGHT_ROUND_BRACKET}"'
                                            f', got "{TokenType.LEFT_CURLY_BRACKET}"')


@pytest.mark.parametrize("input_tokens", [token_generator.function(
    name="func1",
    params=token_generator.parameters(params),
    return_type=TokenType.VOID_KEYWORD,
) for params in [
    [(TokenType.INT_KEYWORD, "x")],
    [(TokenType.FLOAT_KEYWORD, "x"), (TokenType.INT_KEYWORD, "y")],
    [(TokenType.FLOAT_KEYWORD, "x"), (TokenType.INT_KEYWORD, "y"), (TokenType.FLOAT_KEYWORD, "z")]
]
])
def test_parse_function_raises_when_missing_type_in_parameter(input_tokens):
    """
    input:

    input_tokens0:
    void func1(x){}

    input_tokens1:
    void func1(float x, y){}

    input_tokens2:
    void func1(float x, y, float z){}
    """
    input_tokens.remove(token_generator.get_token(TokenType.INT_KEYWORD))

    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(UnexpectedToken) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == (f'Unexpected token - expected "{TokenType.RIGHT_ROUND_BRACKET}"'
                                            f', got "{TokenType.IDENTIFIER}"')


def test_parse_function_should_not_allow_void_type_in_parameter():
    """
    input:

    void func1(void x){
        x = 5;
    }
    """
    input_tokens = token_generator.function(
        name="func1",
        params=token_generator.parameters([(TokenType.VOID_KEYWORD, "x")]),
        return_type=TokenType.VOID_KEYWORD,
        statement_block=([
        ])
    )

    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(UnexpectedToken) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == (f'Unexpected token - expected "{TokenType.RIGHT_ROUND_BRACKET}"'
                                            f', got "{TokenType.VOID_KEYWORD}"')


def test_parse_function_raises_when_missing_left_curly_bracket():
    """
    input:

    void func1(int x)
        x = 5;
    }
    """
    input_tokens = token_generator.function(
        name="func1",
        params=token_generator.parameters([(TokenType.INT_KEYWORD, "x")]),
        return_type=TokenType.VOID_KEYWORD,
        statement_block=([
        ])
    )
    input_tokens.remove(token_generator.get_token(TokenType.LEFT_CURLY_BRACKET))

    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(UnexpectedToken) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == (f'Unexpected token - expected "{TokenType.LEFT_CURLY_BRACKET}"'
                                            f', got "{TokenType.RIGHT_CURLY_BRACKET}"')


def test_parse_function_raises_when_missing_right_curly_bracket():
    """
    input:

    void func1(int x){

    """
    input_tokens = token_generator.function(
        name="func1",
        params=token_generator.parameters([(TokenType.INT_KEYWORD, "x")]),
        return_type=TokenType.VOID_KEYWORD,
    )
    input_tokens.remove(token_generator.get_token(TokenType.RIGHT_CURLY_BRACKET))

    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(UnexpectedToken) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == (f'Unexpected token - expected "{TokenType.RIGHT_CURLY_BRACKET}"'
                                            f', got "{TokenType.ETX}"')


def test_parse_function_raises_when_duplicate_function_declaration():
    """
    input:

    void func1(int x){}
    int func1(){}
    """
    input_tokens = token_generator.function(
        name="func1",
        params=token_generator.parameters([(TokenType.INT_KEYWORD, "x")]),
        return_type=TokenType.VOID_KEYWORD
    )
    input_tokens += token_generator.function(
        name="func1",
        return_type=TokenType.INT_KEYWORD
    )

    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(DeclarationExistsError) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == 'Duplicate declaration - name="func1"'


def test_return_statement_allows_no_expression():
    """
    input:

    int func1(){
        return;
    }
    """
    input_tokens = token_generator.function(
        name="func",
        return_type=TokenType.INT_KEYWORD,
        statement_block=[token_generator.get_token(TokenType.RETURN_KEYWORD),
                         token_generator.get_token(TokenType.SEMICOLON)]
    )
    input_program = token_generator.get_program(input_tokens)

    program = parse_program(input_program)

    assert len(program.functions) == 1
    assert program.functions.get("func")
    func = program.functions["func"]

    assert len(func.statement_block.statements) == 1
    assert isinstance(func.statement_block.statements[0], ReturnStatement)


def test_parse_return_statement_with_additive_expression_and_recursive_calls():
    """
    input:

    int func(int x){
        return func(1) + func(2) + 5 - x;
    }
    """
    input_tokens = token_generator.function(
        name="func",
        return_type=TokenType.INT_KEYWORD,
        params=token_generator.parameters([(TokenType.INT_KEYWORD, "x")]),
        statement_block=[token_generator.get_token(TokenType.RETURN_KEYWORD),
                         token_generator.get_token(TokenType.IDENTIFIER, "func"),
                         token_generator.get_token(TokenType.LEFT_ROUND_BRACKET),
                         token_generator.get_token(TokenType.INT_LITERAL, 1),
                         token_generator.get_token(TokenType.RIGHT_ROUND_BRACKET),
                         token_generator.get_token(TokenType.PLUS_OPERATOR),
                         token_generator.get_token(TokenType.IDENTIFIER, "func"),
                         token_generator.get_token(TokenType.LEFT_ROUND_BRACKET),
                         token_generator.get_token(TokenType.INT_LITERAL, 2),
                         token_generator.get_token(TokenType.RIGHT_ROUND_BRACKET),
                         token_generator.get_token(TokenType.PLUS_OPERATOR),
                         token_generator.get_token(TokenType.INT_LITERAL, 5),
                         token_generator.get_token(TokenType.MINUS_OPERATOR),
                         token_generator.get_token(TokenType.IDENTIFIER, "x"),
                         token_generator.get_token(TokenType.SEMICOLON)]
    )
    input_program = token_generator.get_program(input_tokens)

    program = parse_program(input_program)

    assert len(program.functions) == 1
    assert program.functions.get("func")
    func = program.functions["func"]

    assert len(func.statement_block.statements) == 1
    return_statement = func.statement_block.statements[0]
    assert isinstance(return_statement, ReturnStatement)

    assert isinstance(return_statement.expression, AdditiveExpression)
    assert return_statement.expression.operator == TokenType.MINUS_OPERATOR
    assert return_statement.expression.right == Variable("x")

    nested_additive_expression = return_statement.expression.left
    assert isinstance(nested_additive_expression, AdditiveExpression)
    assert nested_additive_expression.operator == TokenType.PLUS_OPERATOR
    assert nested_additive_expression.right == IntLiteral(5)

    nested_additive_expression_second_level = nested_additive_expression.left
    assert isinstance(nested_additive_expression_second_level, AdditiveExpression)
    assert nested_additive_expression_second_level.operator == TokenType.PLUS_OPERATOR
    assert nested_additive_expression_second_level.right == FunctionCallStatement(position=Position(1, 1),
                                                                                  name="func",
                                                                                  arguments=[IntLiteral(2)])

    assert nested_additive_expression_second_level.left == FunctionCallStatement(position=Position(1, 1),
                                                                                 name="func",
                                                                                 arguments=[IntLiteral(1)])


def test_parse_return_statement_with_complex_arithmetic_expression():
    """
    input:

    int func(){
        return 1 + 2 / ((3 - 4) * 5) - 6;
    }
    """
    input_tokens = token_generator.function(
        name="func",
        return_type=TokenType.INT_KEYWORD,
        statement_block=[token_generator.get_token(TokenType.RETURN_KEYWORD),
                         token_generator.get_token(TokenType.INT_LITERAL, 1),
                         token_generator.get_token(TokenType.PLUS_OPERATOR),
                         token_generator.get_token(TokenType.INT_LITERAL, 2),
                         token_generator.get_token(TokenType.DIVISION_OPERATOR),
                         token_generator.get_token(TokenType.LEFT_ROUND_BRACKET),
                         token_generator.get_token(TokenType.LEFT_ROUND_BRACKET),
                         token_generator.get_token(TokenType.INT_LITERAL, 3),
                         token_generator.get_token(TokenType.MINUS_OPERATOR),
                         token_generator.get_token(TokenType.INT_LITERAL, 4),
                         token_generator.get_token(TokenType.RIGHT_ROUND_BRACKET),
                         token_generator.get_token(TokenType.MULTIPLICATION_OPERATOR),
                         token_generator.get_token(TokenType.INT_LITERAL, 5),
                         token_generator.get_token(TokenType.RIGHT_ROUND_BRACKET),
                         token_generator.get_token(TokenType.MINUS_OPERATOR),
                         token_generator.get_token(TokenType.INT_LITERAL, 6),
                         token_generator.get_token(TokenType.SEMICOLON)]
    )
    input_program = token_generator.get_program(input_tokens)

    program = parse_program(input_program)

    assert len(program.functions) == 1
    assert program.functions.get("func")
    func = program.functions["func"]

    assert len(func.statement_block.statements) == 1
    return_statement = func.statement_block.statements[0]
    assert isinstance(return_statement, ReturnStatement)

    assert isinstance(return_statement.expression, AdditiveExpression)
    assert return_statement.expression.operator == TokenType.MINUS_OPERATOR
    assert return_statement.expression.right == IntLiteral(6)

    nested_additive_expression = return_statement.expression.left
    assert isinstance(nested_additive_expression, AdditiveExpression)
    assert nested_additive_expression.operator == TokenType.PLUS_OPERATOR
    assert nested_additive_expression.left == IntLiteral(1)

    multiplicative_expression = nested_additive_expression.right
    assert isinstance(multiplicative_expression, MultiplicativeExpression)
    assert multiplicative_expression.operator == TokenType.DIVISION_OPERATOR
    assert multiplicative_expression.left == IntLiteral(2)

    nested_multiplicative_expression = multiplicative_expression.right
    assert isinstance(nested_multiplicative_expression, MultiplicativeExpression)
    assert nested_multiplicative_expression.operator == TokenType.MULTIPLICATION_OPERATOR
    assert nested_multiplicative_expression.right == IntLiteral(5)

    additive_expression = nested_multiplicative_expression.left
    assert isinstance(additive_expression, AdditiveExpression)
    assert additive_expression.operator == TokenType.MINUS_OPERATOR
    assert additive_expression.left == IntLiteral(3)
    assert additive_expression.right == IntLiteral(4)


def test_parse_exception():
    """
    input:

    exception CustomException(int x){
        number: int = 5;
        is_even: bool = false;
    }
    """
    attribute1 = token_generator.attribute(
        name="number",
        type=TokenType.INT_KEYWORD,
        expression=[token_generator.get_token(TokenType.INT_LITERAL, 5),
                    token_generator.get_token(TokenType.SEMICOLON)],
    )

    attribute2 = token_generator.attribute(
        name="is_even",
        type=TokenType.BOOL_KEYWORD,
        expression=[token_generator.get_token(TokenType.BOOLEAN_LITERAL, False),
                    token_generator.get_token(TokenType.SEMICOLON)]
    )

    input_tokens = token_generator.exception(
        name="CustomException",
        params=token_generator.parameters([(TokenType.INT_KEYWORD, "x")]),
        attr=token_generator.attributes([attribute1, attribute2])
    )
    input_program = token_generator.get_program(input_tokens)

    program = parse_program(input_program)

    assert len(program.exceptions) == 1
    assert program.exceptions.get("CustomException", False)
    exception = program.exceptions["CustomException"]

    assert exception.name == "CustomException"
    assert len(exception.parameters) == 1
    assert exception.parameters == [Parameter(type=Type(TokenType.INT_KEYWORD), name="x")]
    assert len(exception.attributes) == 2
    assert (exception.attributes[0] == Attribute(type=Type(TokenType.INT_KEYWORD),
                                                 name="number",
                                                 expression=IntLiteral(5)))
    assert (exception.attributes[1] == Attribute(type=Type(TokenType.BOOL_KEYWORD),
                                                 name="is_even",
                                                 expression=BoolLiteral(False)))


def test_parse_exception_raises_when_duplicate_exception_declaration():
    """
    input:

    exception CustomException(int x){
        number: int = 5;
    }
    exception CustomException(){}
    """
    input_tokens = token_generator.exception(
        name="CustomException",
        params=token_generator.parameters([(TokenType.INT_KEYWORD, "x")]),
        attr=token_generator.attribute(
            name="number",
            type=TokenType.INT_KEYWORD,
            expression=[token_generator.get_token(TokenType.INT_LITERAL, 5),
                        token_generator.get_token(TokenType.SEMICOLON)]
        )
    )
    input_tokens += token_generator.exception(
        name="CustomException"
    )

    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(DeclarationExistsError) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == 'Duplicate declaration - name="CustomException"'


def test_parse_exception_raises_when_missing_left_round_bracket():
    """
    input:

    exception CustomException int x){
        number: int = 5;
    }
    """
    input_tokens = token_generator.exception(
        name="CustomException",
        params=token_generator.parameters([(TokenType.INT_KEYWORD, "x")]),
        attr=token_generator.attribute(
            name="number",
            type=TokenType.INT_KEYWORD,
            expression=[token_generator.get_token(TokenType.INT_LITERAL, 5)]
        )
    )
    input_tokens.remove(token_generator.get_token(TokenType.LEFT_ROUND_BRACKET))
    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(UnexpectedToken) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == (f'Unexpected token - expected "{TokenType.LEFT_ROUND_BRACKET}"'
                                            f', got "{TokenType.INT_KEYWORD}"')


def test_parse_exception_raises_when_missing_right_round_bracket():
    """
    input:

    exception CustomException(int x{
        number: int = 5;
    }
    """
    input_tokens = token_generator.exception(
        name="CustomException",
        params=token_generator.parameters([(TokenType.INT_KEYWORD, "x")]),
        attr=token_generator.attribute(
            name="number",
            type=TokenType.INT_KEYWORD,
            expression=[token_generator.get_token(TokenType.INT_LITERAL, 5)]
        )
    )
    input_tokens.remove(token_generator.get_token(TokenType.RIGHT_ROUND_BRACKET))
    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(UnexpectedToken) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == (f'Unexpected token - expected "{TokenType.RIGHT_ROUND_BRACKET}"'
                                            f', got "{TokenType.LEFT_CURLY_BRACKET}"')


def test_parse_exception_raises_when_missing_left_curly_bracket():
    """
    input:

    exception CustomException(int x)
        number: int = 5;
    }
    """
    input_tokens = token_generator.exception(
        name="CustomException",
        params=token_generator.parameters([(TokenType.INT_KEYWORD, "x")]),
        attr=token_generator.attribute(
            name="number",
            type=TokenType.INT_KEYWORD,
            expression=[token_generator.get_token(TokenType.INT_LITERAL, 5),
                        token_generator.get_token(TokenType.SEMICOLON)]
        )
    )
    input_tokens.remove(token_generator.get_token(TokenType.LEFT_CURLY_BRACKET))
    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(UnexpectedToken) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == (f'Unexpected token - expected "{TokenType.LEFT_CURLY_BRACKET}"'
                                            f', got "{TokenType.IDENTIFIER}"')


def test_parse_exception_raises_when_missing_right_curly_bracket():
    """
    input:

    exception CustomException(int x){
        number: int = 5;

    """
    input_tokens = token_generator.exception(
        name="CustomException",
        params=token_generator.parameters([(TokenType.INT_KEYWORD, "x")]),
        attr=token_generator.attribute(
            name="number",
            type=TokenType.INT_KEYWORD,
            expression=[token_generator.get_token(TokenType.INT_LITERAL, 5),
                        token_generator.get_token(TokenType.SEMICOLON)]
        )
    )
    input_tokens.remove(token_generator.get_token(TokenType.RIGHT_CURLY_BRACKET))
    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(UnexpectedToken) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == (f'Unexpected token - expected "{TokenType.RIGHT_CURLY_BRACKET}"'
                                            f', got "{TokenType.ETX}"')


def test_parse_exception_raises_when_missing_colon_in_attributes():
    """
    input:

    exception CustomException(int x){
        number int = 5;
    }
    """
    input_tokens = token_generator.exception(
        name="CustomException",
        params=token_generator.parameters([(TokenType.INT_KEYWORD, "x")]),
        attr=token_generator.attribute(
            name="number",
            type=TokenType.INT_KEYWORD,
            expression=[token_generator.get_token(TokenType.INT_LITERAL, 5),
                        token_generator.get_token(TokenType.SEMICOLON)]
        )
    )
    input_tokens.remove(token_generator.get_token(TokenType.COLON))
    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(UnexpectedToken) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == (f'Unexpected token - expected "{TokenType.COLON}"'
                                            f', got "{TokenType.INT_KEYWORD}"')


def test_parse_exception_raises_when_missing_expression_after_assignment():
    """
    input:

    exception CustomException(int x){
        number: int =
    }
    """
    input_tokens = token_generator.exception(
        name="CustomException",
        params=token_generator.parameters([(TokenType.INT_KEYWORD, "x")]),
        attr=token_generator.attribute(
            name="number",
            type=TokenType.INT_KEYWORD,
            expression=[token_generator.get_token(TokenType.INT_LITERAL, 5)]
        )
    )
    input_tokens.remove(token_generator.get_token(TokenType.INT_LITERAL, 5))
    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(ExpectedExpressionError):
        parse_program(input_program)


def test_parse_exception_raises_when_missing_semicolon_after_expression():
    """
    input:

    exception CustomException(int x){
        number: int = 5;
    }
    """
    input_tokens = token_generator.exception(
        name="CustomException",
        params=token_generator.parameters([(TokenType.INT_KEYWORD, "x")]),
        attr=token_generator.attribute(
            name="number",
            type=TokenType.INT_KEYWORD,
            expression=[token_generator.get_token(TokenType.INT_LITERAL, 5)]
        )
    )
    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(UnexpectedToken) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == (f'Unexpected token - expected "{TokenType.SEMICOLON}"'
                                            f', got "{TokenType.RIGHT_CURLY_BRACKET}"')


def test_parse_exception_should_not_allow_void_type_in_attributes():
    """
    input:

    exception CustomException(int x){
        number: void;
    }
    """
    input_tokens = token_generator.exception(
        name="CustomException",
        params=token_generator.parameters([(TokenType.INT_KEYWORD, "x")]),
        attr=token_generator.attribute(
            name="number",
            type=TokenType.VOID_KEYWORD,
        )
    )
    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(ExpectedSimpleTypeError):
        parse_program(input_program)


def test_parse_if_statement():
    """
    input:

    void main(){
        if(x == 5){
            a = x;
        }
    }
    """
    if_statement = token_generator.if_statement(
        condition=[token_generator.get_token(TokenType.IDENTIFIER, "x"),
                   token_generator.get_token(TokenType.EQUAL_OPERATOR),
                   token_generator.get_token(TokenType.INT_LITERAL, 5)],
        if_block=[token_generator.get_token(TokenType.IDENTIFIER, "a"),
                  token_generator.get_token(TokenType.ASSIGNMENT),
                  token_generator.get_token(TokenType.IDENTIFIER, "x"),
                  token_generator.get_token(TokenType.SEMICOLON)]
    )
    input_tokens = token_generator.function(
        name="main",
        params=token_generator.parameters([]),
        return_type=TokenType.VOID_KEYWORD,
        statement_block=if_statement
    )
    input_program = token_generator.get_program(input_tokens)

    program = parse_program(input_program)

    assert len(program.functions["main"].statement_block.statements) == 1
    parsed_if_statement = program.functions["main"].statement_block.statements[0]
    assert isinstance(parsed_if_statement, IfStatement)

    assert parsed_if_statement.condition == RelationalExpression(
        left=Variable("x"),
        right=IntLiteral(5),
        operator=TokenType.EQUAL_OPERATOR
    )
    assert len(parsed_if_statement.if_block.statements) == 1
    assert parsed_if_statement.if_block.statements[0] == AssignmentStatement(
        position=Position(1, 1),
        expression=Variable("x"),
        name='a'
    )
