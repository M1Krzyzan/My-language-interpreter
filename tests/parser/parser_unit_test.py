from typing import List

import pytest
import token_generator
from src.ast.core_structures import Program
from src.ast.statemens import StatementBlock
from src.ast.types import ReturnType
from src.errors.parser_error import UnexpectedToken, InternalParserError
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
