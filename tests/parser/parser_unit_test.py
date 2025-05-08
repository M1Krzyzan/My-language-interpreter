import pytest
import token_generator
from src.ast.core_structures import Program
from src.ast.expressions import *
from src.ast.statemens import *
from src.ast.types import ReturnType, StringType, IntType, BoolType
from src.errors.parser_error import (
    UnexpectedToken,
    DeclarationExistsError,
    ExpectedExpressionError,
    ExpectedSimpleTypeError,
    ExpectedConditionError,
    InternalParserError)
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

    with pytest.raises(InternalParserError) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == ("Expected Function or Exception declaration, "
                                            "got unexpected declaration type")


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

    assert isinstance(return_statement.expression, MinusExpression)
    assert return_statement.expression.right == Variable("x")

    nested_additive_expression = return_statement.expression.left
    assert isinstance(nested_additive_expression, PlusExpression)
    assert nested_additive_expression.right == IntLiteral(5)

    nested_additive_expression_second_level = nested_additive_expression.left
    assert isinstance(nested_additive_expression_second_level, PlusExpression)
    assert nested_additive_expression_second_level.right == FunctionCall(position=Position(1, 1),
                                                                         name="func",
                                                                         arguments=[IntLiteral(2)])

    assert nested_additive_expression_second_level.left == FunctionCall(position=Position(1, 1),
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

    assert isinstance(return_statement.expression, MinusExpression)
    assert return_statement.expression.right == IntLiteral(6)

    nested_additive_expression = return_statement.expression.left
    assert isinstance(nested_additive_expression, PlusExpression)
    assert nested_additive_expression.left == IntLiteral(1)

    multiplicative_expression = nested_additive_expression.right
    assert isinstance(multiplicative_expression, DivideExpression)
    assert multiplicative_expression.left == IntLiteral(2)

    nested_multiplicative_expression = multiplicative_expression.right
    assert isinstance(nested_multiplicative_expression, MultiplyExpression)
    assert nested_multiplicative_expression.right == IntLiteral(5)

    additive_expression = nested_multiplicative_expression.left
    assert isinstance(additive_expression, MinusExpression)
    assert additive_expression.left == IntLiteral(3)
    assert additive_expression.right == IntLiteral(4)


def test_parse_additive_expression():
    """
    input:

    float func(float x){
        return x + 1.35;
    }
    """
    input_tokens = token_generator.function(
        name="func",
        return_type=TokenType.BOOL_KEYWORD,
        params=token_generator.parameters([(TokenType.INT_KEYWORD, "x")]),
        statement_block=[token_generator.get_token(TokenType.RETURN_KEYWORD),
                         token_generator.get_token(TokenType.IDENTIFIER, "x"),
                         token_generator.get_token(TokenType.PLUS_OPERATOR),
                         token_generator.get_token(TokenType.FLOAT_LITERAL, 1.35),
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

    additive_expression = return_statement.expression
    assert isinstance(additive_expression, PlusExpression)
    assert additive_expression.left == Variable("x")
    assert additive_expression.right == FloatLiteral(1.35)


def test_parse_relational_expression():
    """
    input:

    bool func(int x, int y){
        return not(x == 1) or y != 9 and x < 10;
    }
    """
    input_tokens = token_generator.function(
        name="func",
        return_type=TokenType.BOOL_KEYWORD,
        params=token_generator.parameters([(TokenType.INT_KEYWORD, "x"),
                                           (TokenType.INT_KEYWORD, "y")]),
        statement_block=[token_generator.get_token(TokenType.RETURN_KEYWORD),
                         token_generator.get_token(TokenType.NEGATION_OPERATOR),
                         token_generator.get_token(TokenType.LEFT_ROUND_BRACKET),
                         token_generator.get_token(TokenType.IDENTIFIER, "x"),
                         token_generator.get_token(TokenType.EQUAL_OPERATOR),
                         token_generator.get_token(TokenType.INT_LITERAL, 1),
                         token_generator.get_token(TokenType.RIGHT_ROUND_BRACKET),
                         token_generator.get_token(TokenType.OR_OPERATOR),
                         token_generator.get_token(TokenType.IDENTIFIER, "y"),
                         token_generator.get_token(TokenType.NOT_EQUAL_OPERATOR),
                         token_generator.get_token(TokenType.INT_LITERAL, 9),
                         token_generator.get_token(TokenType.AND_OPERATOR),
                         token_generator.get_token(TokenType.IDENTIFIER, "x"),
                         token_generator.get_token(TokenType.LESS_THAN_OPERATOR),
                         token_generator.get_token(TokenType.INT_LITERAL, 10),
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

    or_expression = return_statement.expression
    assert isinstance(or_expression, OrExpression)
    assert or_expression.left == NegatedExpression(expression=EqualsExpression(left=Variable("x"),
                                                                               right=IntLiteral(1)))

    and_expression = or_expression.right
    assert isinstance(and_expression, AndExpression)
    assert and_expression.left == NotEqualsExpression(left=Variable("y"),
                                                      right=IntLiteral(9))
    assert and_expression.right == LessThanExpression(left=Variable("x"),
                                                      right=IntLiteral(10))


def test_parse_relational_expression_raises_when_missing_expression_after_relational_operator():
    """
    input:

    bool func(int x){
        return x == ;
    }
    """
    input_tokens = token_generator.function(
        name="func",
        return_type=TokenType.BOOL_KEYWORD,
        params=token_generator.parameters([(TokenType.INT_KEYWORD, "x")]),
        statement_block=[token_generator.get_token(TokenType.RETURN_KEYWORD),
                         token_generator.get_token(TokenType.IDENTIFIER, "x"),
                         token_generator.get_token(TokenType.EQUAL_OPERATOR),
                         token_generator.get_token(TokenType.SEMICOLON)]
    )
    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(ExpectedExpressionError) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == f'Missing expression after {TokenType.EQUAL_OPERATOR}'


def test_parse_unary_minus_expression():
    """
    input:

    int func(){
        return -1;
    }
    """
    input_tokens = token_generator.function(
        name="func",
        return_type=TokenType.INT_KEYWORD,
        statement_block=[token_generator.get_token(TokenType.RETURN_KEYWORD),
                         token_generator.get_token(TokenType.MINUS_OPERATOR),
                         token_generator.get_token(TokenType.INT_LITERAL, 1),
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

    unary_minus_expression = return_statement.expression
    assert isinstance(unary_minus_expression, UnaryMinusExpression)
    assert unary_minus_expression.expression == IntLiteral(1)


def test_parse_casted_expression():
    """
    input:

    string func(){
        return -1 to string;
    }
    """
    input_tokens = token_generator.function(
        name="func",
        return_type=TokenType.STRING_KEYWORD,
        statement_block=[token_generator.get_token(TokenType.RETURN_KEYWORD),
                         token_generator.get_token(TokenType.MINUS_OPERATOR),
                         token_generator.get_token(TokenType.INT_LITERAL, 1),
                         token_generator.get_token(TokenType.TO_KEYWORD),
                         token_generator.get_token(TokenType.STRING_KEYWORD),
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

    casted_expression = return_statement.expression
    assert isinstance(casted_expression, CastedExpression)
    assert casted_expression.to_type == StringType()

    unary_minus_expression = casted_expression.expression
    assert isinstance(unary_minus_expression, UnaryMinusExpression)
    assert unary_minus_expression.expression == IntLiteral(1)


def test_parse_casted_expression_raises_when_missing_simple_type_after_to_operator():
    """
    input:

    string func(){
        return 1 to;
    }
    """
    input_tokens = token_generator.function(
        name="func",
        return_type=TokenType.STRING_KEYWORD,
        statement_block=[token_generator.get_token(TokenType.RETURN_KEYWORD),
                         token_generator.get_token(TokenType.INT_LITERAL, 1),
                         token_generator.get_token(TokenType.TO_KEYWORD),
                         token_generator.get_token(TokenType.SEMICOLON)]
    )
    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(ExpectedSimpleTypeError) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == f"Expected simple type after {TokenType.TO_KEYWORD}"


def test_parse_assigment_raises_when_missing_expression():
    """
    input:

    void func(){
        x = ;
    }
    """
    input_tokens = token_generator.function(
        name="func",
        return_type=TokenType.VOID_KEYWORD,
        statement_block=[token_generator.get_token(TokenType.IDENTIFIER, "x"),
                         token_generator.get_token(TokenType.ASSIGNMENT),
                         token_generator.get_token(TokenType.SEMICOLON)]
    )
    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(ExpectedExpressionError) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == f"Missing expression after {TokenType.ASSIGNMENT}"


def test_parse_while_statement():
    """
    input:

    void func(int x){
        while(x > 0){
            rand_func();
            x = x - 1;
            while(y){}
        }
    }
    """
    input_tokens = token_generator.function(
        name="func",
        return_type=TokenType.VOID_KEYWORD,
        statement_block=token_generator.while_statement(
            condition=[token_generator.get_token(TokenType.IDENTIFIER, "x"),
                       token_generator.get_token(TokenType.GREATER_THAN_OPERATOR),
                       token_generator.get_token(TokenType.INT_LITERAL, 0)],
            statement_block=[token_generator.get_token(TokenType.IDENTIFIER, "rand_func"),
                             token_generator.get_token(TokenType.LEFT_ROUND_BRACKET),
                             token_generator.get_token(TokenType.RIGHT_ROUND_BRACKET),
                             token_generator.get_token(TokenType.SEMICOLON),
                             token_generator.get_token(TokenType.IDENTIFIER, "x"),
                             token_generator.get_token(TokenType.ASSIGNMENT),
                             token_generator.get_token(TokenType.IDENTIFIER, "x"),
                             token_generator.get_token(TokenType.MINUS_OPERATOR),
                             token_generator.get_token(TokenType.INT_LITERAL, 1),
                             token_generator.get_token(TokenType.SEMICOLON),
                             token_generator.get_token(TokenType.WHILE_KEYWORD),
                             token_generator.get_token(TokenType.LEFT_ROUND_BRACKET),
                             token_generator.get_token(TokenType.IDENTIFIER, "y"),
                             token_generator.get_token(TokenType.RIGHT_ROUND_BRACKET),
                             token_generator.get_token(TokenType.LEFT_CURLY_BRACKET),
                             token_generator.get_token(TokenType.RIGHT_CURLY_BRACKET)]
        )
    )
    input_program = token_generator.get_program(input_tokens)

    program = parse_program(input_program)

    assert len(program.functions) == 1
    assert program.functions.get("func")
    func = program.functions["func"]

    assert len(func.statement_block.statements) == 1
    while_statement = func.statement_block.statements[0]
    assert isinstance(while_statement, WhileStatement)

    condition = while_statement.condition
    assert isinstance(condition, GreaterThanExpression)
    assert condition.left == Variable("x")
    assert condition.right == IntLiteral(0)

    statement_block = while_statement.block
    assert isinstance(statement_block, StatementBlock)
    assert len(statement_block.statements) == 3

    assert statement_block.statements[0] == FunctionCall(name="rand_func",
                                                         arguments=[],
                                                         position=Position(1, 1))

    assert statement_block.statements[1] == AssignmentStatement(
        name="x",
        expression=MinusExpression(left=Variable("x"),
                                   right=IntLiteral(1)),
        position=Position(1, 1)
    )

    assert statement_block.statements[2] == WhileStatement(condition=Variable("y"),
                                                           block=StatementBlock([]),
                                                           position=Position(1, 1))


def test_parse_while_statement_raises_when_condition_missing():
    """
        input:

        void func(){
            while(){
                rand_func();
            }
        }
        """
    input_tokens = token_generator.function(
        name="func",
        return_type=TokenType.VOID_KEYWORD,
        statement_block=token_generator.while_statement(
            condition=[],
            statement_block=[token_generator.get_token(TokenType.IDENTIFIER, "rand_func"),
                             token_generator.get_token(TokenType.LEFT_ROUND_BRACKET),
                             token_generator.get_token(TokenType.RIGHT_ROUND_BRACKET),
                             token_generator.get_token(TokenType.SEMICOLON)]
        )
    )
    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(ExpectedConditionError) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == f"Missing condition after {TokenType.WHILE_KEYWORD}"


def test_parse_if_statement():
    """
    input:

    void main(){
        if(x == 5){
            a = x;
        }elif(x == 4){
            b = x;
        }elif(x == 3){
            continue;
        }else{
            break;
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
    elif_statement1 = token_generator.elif_statement(
        condition=[token_generator.get_token(TokenType.IDENTIFIER, "x"),
                   token_generator.get_token(TokenType.EQUAL_OPERATOR),
                   token_generator.get_token(TokenType.INT_LITERAL, 4)],
        elif_block=[token_generator.get_token(TokenType.IDENTIFIER, "b"),
                    token_generator.get_token(TokenType.ASSIGNMENT),
                    token_generator.get_token(TokenType.IDENTIFIER, "x"),
                    token_generator.get_token(TokenType.SEMICOLON)]
    )
    elif_statement2 = token_generator.elif_statement(
        condition=[token_generator.get_token(TokenType.IDENTIFIER, "x"),
                   token_generator.get_token(TokenType.EQUAL_OPERATOR),
                   token_generator.get_token(TokenType.INT_LITERAL, 3)],
        elif_block=[token_generator.get_token(TokenType.CONTINUE_KEYWORD),
                    token_generator.get_token(TokenType.SEMICOLON)]
    )

    else_block = token_generator.else_statement([
        token_generator.get_token(TokenType.BREAK_KEYWORD),
        token_generator.get_token(TokenType.SEMICOLON)
    ])

    input_tokens = token_generator.function(
        name="main",
        params=token_generator.parameters([]),
        return_type=TokenType.VOID_KEYWORD,
        statement_block=if_statement + elif_statement1 + elif_statement2 + else_block
    )
    input_program = token_generator.get_program(input_tokens)

    program = parse_program(input_program)

    assert len(program.functions["main"].statement_block.statements) == 1
    parsed_if_statement = program.functions["main"].statement_block.statements[0]
    assert isinstance(parsed_if_statement, IfStatement)

    assert parsed_if_statement.condition == EqualsExpression(
        left=Variable("x"),
        right=IntLiteral(5)
    )
    assert len(parsed_if_statement.if_block.statements) == 1
    assert parsed_if_statement.if_block.statements[0] == AssignmentStatement(
        position=Position(1, 1),
        expression=Variable("x"),
        name='a'
    )

    assert len(parsed_if_statement.elif_statement) == 2
    elif_condition1, elif_block1 = parsed_if_statement.elif_statement[0]
    elif_condition2, elif_block2 = parsed_if_statement.elif_statement[1]

    assert isinstance(elif_condition1, RelationalExpression)
    assert elif_condition1 == EqualsExpression(
        left=Variable("x"),
        right=IntLiteral(4)
    )

    assert isinstance(elif_block1, StatementBlock)
    assert len(elif_block1.statements) == 1
    assert elif_block1.statements[0] == AssignmentStatement(
        position=Position(1, 1),
        expression=Variable("x"),
        name='b'
    )

    assert isinstance(elif_condition2, RelationalExpression)
    assert elif_condition2 == EqualsExpression(
        left=Variable("x"),
        right=IntLiteral(3)
    )

    assert isinstance(elif_block2, StatementBlock)
    assert len(elif_block2.statements) == 1
    assert elif_block2.statements[0] == LoopControlStatement(
        position=Position(1, 1),
        type=LoopControlType.CONTINUE
    )

    else_block = parsed_if_statement.else_block
    assert isinstance(else_block, StatementBlock)
    assert len(parsed_if_statement.else_block.statements) == 1
    assert parsed_if_statement.else_block.statements[0] == LoopControlStatement(
        position=Position(1, 1),
        type=LoopControlType.BREAK
    )


def test_parse_if_statement_raises_when_condition_missing_after_if():
    """
    input:

    void main(){
        if(){
            a = x;
        }
    }
    """
    if_statement = token_generator.if_statement(
        condition=[],
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

    with pytest.raises(ExpectedConditionError) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == f"Missing condition after {TokenType.IF_KEYWORD}"


def test_parse_if_statement_raises_when_condition_missing_after_elif():
    """
    input:

    void main(){
        if(x == 5){
            a = x;
        }elif(){
            break;
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
    elif_statements = token_generator.elif_statement(
        condition=[],
        elif_block=[token_generator.get_token(TokenType.BREAK_KEYWORD, "a"),
                    token_generator.get_token(TokenType.SEMICOLON)]
    )
    input_tokens = token_generator.function(
        name="main",
        params=token_generator.parameters([]),
        return_type=TokenType.VOID_KEYWORD,
        statement_block=if_statement + elif_statements
    )
    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(ExpectedConditionError) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == f"Missing condition after {TokenType.ELIF_KEYWORD}"


def test_parse_try_catch_statement():
    """
    input:

    void main(){
        try{
            a = x;
        }catch (CustomException e){
            a = 0;
        }catch (Exception e){
            print(e.message);
        }
    }
    """
    catch1 = token_generator.catch(
        catch_exception=[token_generator.get_token(TokenType.IDENTIFIER, "CustomException"),
                         token_generator.get_token(TokenType.IDENTIFIER, "e")],
        catch_block=[token_generator.get_token(TokenType.IDENTIFIER, "a"),
                     token_generator.get_token(TokenType.ASSIGNMENT),
                     token_generator.get_token(TokenType.INT_LITERAL, 0),
                     token_generator.get_token(TokenType.SEMICOLON)]
    )
    catch2 = token_generator.catch(
        catch_exception=[token_generator.get_token(TokenType.IDENTIFIER, "Exception"),
                         token_generator.get_token(TokenType.IDENTIFIER, "e")],
        catch_block=[token_generator.get_token(TokenType.IDENTIFIER, "print"),
                     token_generator.get_token(TokenType.LEFT_ROUND_BRACKET),
                     token_generator.get_token(TokenType.IDENTIFIER, "e"),
                     token_generator.get_token(TokenType.DOT),
                     token_generator.get_token(TokenType.IDENTIFIER, "message"),
                     token_generator.get_token(TokenType.RIGHT_ROUND_BRACKET),
                     token_generator.get_token(TokenType.SEMICOLON)]
    )
    input_tokens = token_generator.function(
        name="main",
        return_type=TokenType.VOID_KEYWORD,
        statement_block=token_generator.try_catch(
            try_block=[
                token_generator.get_token(TokenType.IDENTIFIER, "a"),
                token_generator.get_token(TokenType.ASSIGNMENT),
                token_generator.get_token(TokenType.IDENTIFIER, "x"),
                token_generator.get_token(TokenType.SEMICOLON)
            ],
            catch_statements=[catch1, catch2]
        )
    )
    input_program = token_generator.get_program(input_tokens)

    program = parse_program(input_program)

    assert len(program.functions["main"].statement_block.statements) == 1
    parsed_try_statement = program.functions["main"].statement_block.statements[0]
    assert isinstance(parsed_try_statement, TryCatchStatement)

    try_block = parsed_try_statement.try_block
    assert isinstance(try_block, StatementBlock)
    assert len(try_block.statements) == 1
    assert try_block.statements[0] == AssignmentStatement(
        position=Position(1, 1),
        expression=Variable("x"),
        name='a'
    )

    assert len(parsed_try_statement.catch_statements) == 2
    catch_statement1 = parsed_try_statement.catch_statements[0]
    catch_statement2 = parsed_try_statement.catch_statements[1]

    assert isinstance(catch_statement1, CatchStatement)
    assert catch_statement1 == CatchStatement(
        exception="CustomException",
        name="e",
        block=StatementBlock([AssignmentStatement(
            position=Position(1, 1),
            expression=IntLiteral(0),
            name='a'
        )]),
        position=Position(1, 1),
    )

    assert isinstance(catch_statement2, CatchStatement)
    assert catch_statement2 == CatchStatement(
        exception="Exception",
        name="e",
        block=StatementBlock([FunctionCall(
            position=Position(1, 1),
            name="print",
            arguments=[AttributeCall(
                var_name="e",
                attr_name="message"
            )]
        )]),
        position=Position(1, 1),
    )


def test_parse_throw_statement():
    """
    input:

    void main(){
        throw CustomException(a+b);
    }
    """
    input_tokens = token_generator.function(
        name="main",
        return_type=TokenType.VOID_KEYWORD,
        statement_block=token_generator.throw(
            exception_name="CustomException",
            args=[
                token_generator.get_token(TokenType.IDENTIFIER, "a"),
                token_generator.get_token(TokenType.PLUS_OPERATOR),
                token_generator.get_token(TokenType.IDENTIFIER, "b"),
            ],
        )
    )
    input_program = token_generator.get_program(input_tokens)

    program = parse_program(input_program)

    assert len(program.functions["main"].statement_block.statements) == 1
    parsed_throw_statement = program.functions["main"].statement_block.statements[0]
    assert isinstance(parsed_throw_statement, ThrowStatement)

    assert parsed_throw_statement.name == "CustomException"
    assert len(parsed_throw_statement.args) == 1
    assert parsed_throw_statement.args[0] == PlusExpression(
        left=Variable("a"),
        right=Variable("b")
    )


def test_parse_return_statement_raises_when_missing_semicolon():
    """
    input:

    int func(int x){
        return x
    }
    """
    input_tokens = token_generator.function(
        name="func",
        return_type=TokenType.INT_KEYWORD,
        params=token_generator.parameters([(TokenType.INT_KEYWORD, "x")]),
        statement_block=[token_generator.get_token(TokenType.RETURN_KEYWORD),
                         token_generator.get_token(TokenType.IDENTIFIER, "x")]
    )
    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(UnexpectedToken) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == (f'Unexpected token - expected "{TokenType.SEMICOLON}"'
                                            f', got "{TokenType.RIGHT_CURLY_BRACKET}"')


@pytest.mark.parametrize("operator", [
    TokenType.PLUS_OPERATOR,
    TokenType.MINUS_OPERATOR,
    TokenType.DIVISION_OPERATOR,
    TokenType.MODULO_OPERATOR,
    TokenType.MULTIPLICATION_OPERATOR,
    TokenType.OR_OPERATOR,
    TokenType.AND_OPERATOR
])
def test_parse_expression_raises_when_missing_right_expression(operator):
    """
    input example:
    int func(){
        return 1 +;
    }
    """
    input_tokens = token_generator.function(
        name="func",
        return_type=TokenType.INT_KEYWORD,
        statement_block=[token_generator.get_token(TokenType.RETURN_KEYWORD),
                         token_generator.get_token(TokenType.INT_LITERAL, 1),
                         token_generator.get_token(operator),
                         token_generator.get_token(TokenType.SEMICOLON)]
    )
    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(ExpectedExpressionError) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == f'Missing expression after {operator}'


@pytest.mark.parametrize("operator", [
    TokenType.LEFT_ROUND_BRACKET,
    TokenType.MINUS_OPERATOR,
    TokenType.NEGATION_OPERATOR
])
def test_parse_expression_raises_when_missing_expression_after_unary_operator(operator):
    """
    input example:
    int func(){
        return not;
    }
    """
    input_tokens = token_generator.function(
        name="func",
        return_type=TokenType.INT_KEYWORD,
        statement_block=[token_generator.get_token(TokenType.RETURN_KEYWORD),
                         token_generator.get_token(operator),
                         token_generator.get_token(TokenType.SEMICOLON)]
    )
    input_program = token_generator.get_program(input_tokens)

    with pytest.raises(ExpectedExpressionError) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == f'Missing expression after {operator}'


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
    assert exception.parameters == [Parameter(type=IntType(), name="x")]
    assert len(exception.attributes) == 2
    assert (exception.attributes[0] == Attribute(type=IntType(),
                                                 name="number",
                                                 expression=IntLiteral(5)))
    assert (exception.attributes[1] == Attribute(type=BoolType(),
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

    with pytest.raises(ExpectedSimpleTypeError) as exception_info:
        parse_program(input_program)

    assert exception_info.value.message == f"Expected simple type after {TokenType.COLON}"
