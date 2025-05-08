from io import StringIO

import pytest

from src.ast.core_structures import Function, Exception
from src.ast.expressions import *
from src.ast.statemens import *
from src.errors.parser_error import UnexpectedToken, ExpectedDeclarationError
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

    assert is_even_function == Function(
        position=Position(11, 5),
        name="is_even",
        return_type=Type.BoolType,
        parameters=[
            Parameter(
                name="number",
                type=Type.IntType
            )
        ],
        statement_block=StatementBlock([
            ReturnStatement(
                position=Position(12, 9),
                expression=EqualsExpression(
                    position=Position(12, 16),
                    left=ModuloExpression(
                        position=Position(12, 16),
                        left=Variable(Position(12, 16), "number"),
                        right=IntLiteral(Position(12, 25), 2)
                    ),
                    right=IntLiteral(Position(12, 30), 0)
                )
            )
        ])
    )

    assert print_even_function == Function(
        position=Position(15, 5),
        name="print_even_if_not_divisible_by_5",
        return_type=Type.VoidType,
        parameters=[
            Parameter(
                name="number",
                type=Type.IntType
            )
        ],
        statement_block=StatementBlock([
            WhileStatement(
                position=Position(16, 9),
                condition=GreaterThanExpression(
                    position=Position(16, 16),
                    left=Variable(Position(16, 16), "number"),
                    right=IntLiteral(Position(16, 25), 0)
                ),
                block=StatementBlock([
                    IfStatement(
                        position=Position(18, 13),
                        condition=EqualsExpression(
                            position=Position(18, 17),
                            left=ModuloExpression(
                                position=Position(18, 17),
                                left=Variable(Position(18, 17), "number"),
                                right=IntLiteral(Position(18, 26), 5)
                            ),
                            right=IntLiteral(Position(18, 31), 0)
                        ),
                        if_block=StatementBlock([
                            BreakStatement(
                                position=Position(19, 17),
                            )
                        ]),
                        elif_statement=[(
                            FunctionCall(
                                position=Position(20, 20),
                                name="is_even",
                                arguments=[Variable(Position(20, 28), "number")]
                            ), StatementBlock([
                                ContinueStatement(
                                    position=Position(21, 17)
                                )]
                            )
                        )],
                        else_block=StatementBlock([
                            FunctionCall(
                                position=Position(23, 17),
                                name="print",
                                arguments=[
                                    StringLiteral(Position(23, 23), "x: "),
                                    Variable(Position(23, 30), "number")
                                ]
                            ),
                            AssignmentStatement(
                                position=Position(24, 17),
                                name="number",
                                expression=MinusExpression(
                                    position=Position(24, 35),
                                    left=Variable(Position(24, 26), "number"),
                                    right=IntLiteral(Position(24, 35), 1)
                                )
                            )
                        ])
                    )
                ])
            )
        ])
    )

    assert main_function == Function(
        position=Position(28, 5),
        name="main",
        return_type=Type.VoidType,
        parameters=[],
        statement_block=StatementBlock([
            TryCatchStatement(
                position=Position(29, 9),
                try_block=StatementBlock([
                    AssignmentStatement(
                        position=Position(30, 13),
                        name="x",
                        expression=CastedExpression(
                            position=Position(30, 17),
                            to_type=Type.IntType,
                            expression=FunctionCall(
                                position=Position(30, 17),
                                name="input",
                                arguments=[]
                            )
                        )
                    ),
                    IfStatement(
                        position=Position(31, 13),
                        condition=LessThanOrEqualsExpression(
                            position=Position(31, 17),
                            left=Variable(Position(31, 17), "x"),
                            right=IntLiteral(Position(31, 22), 0)
                        ),
                        if_block=StatementBlock([
                            ThrowStatement(
                                position=Position(32, 17),
                                name="ValueError",
                                args=[Variable(Position(32, 34), "x")]
                            )
                        ]),
                    ),
                    FunctionCall(
                        position=Position(34, 13),
                        name="print_even_if_not_divisible_by_5",
                        arguments=[Variable(Position(34, 46), "x")]
                    )
                ]),
                catch_statements=[
                    CatchStatement(
                        position=Position(35, 10),
                        exception="BaseException",
                        name="e",
                        block=StatementBlock([
                            FunctionCall(
                                position=Position(36, 13),
                                name="print",
                                arguments=[
                                    StringLiteral(Position(36, 19), "Error: "),
                                    AttributeCall(
                                        position=Position(36, 30),
                                        var_name="e",
                                        attr_name="message"
                                    ),
                                    StringLiteral(Position(36, 41), "\n \t Value="),
                                    AttributeCall(
                                        position=Position(36, 57),
                                        var_name="e",
                                        attr_name="value"
                                    ),
                                    AttributeCall(
                                        position=Position(36, 66),
                                        var_name="e",
                                        attr_name="line"
                                    ),
                                    StringLiteral(Position(36, 74), "\n"),
                                ]
                            )
                        ])
                    )
                ]
            )
        ])
    )

    assert value_error_exception == Exception(
        position=Position(2, 5),
        name="ValueError",
        parameters=[
            Parameter(
                name="value",
                type=Type.IntType,
            )
        ],
        attributes=[
            Attribute(
                name="message",
                type=Type.StringType,
                expression=PlusExpression(
                    position=Position(3, 27),
                    left=PlusExpression(
                        position=Position(3, 27),
                        left=StringLiteral(Position(18, 13), "Wrong value="),
                        right=CastedExpression(
                            position=Position(3, 42),
                            to_type=Type.StringType,
                            expression=Variable(Position(3, 42), "value")
                        ),
                    ),
                    right=StringLiteral(Position(3, 59), " - should be higher than 0: ")
                )
            )
        ]
    )


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
