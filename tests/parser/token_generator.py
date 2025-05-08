from typing import List, Tuple, Optional

from src.ast.position import Position
from src.lexer.token_ import Token, TokenType


def get_token(token_type: TokenType, value: [str | float | int | bool] = None) -> Token:
    return Token(token_type, Position(1, 1), value)


def get_program(tokens: List[Token]) -> List[Token]:
    return tokens + [get_token(TokenType.ETX)]


def function(name: str,
             return_type: TokenType,
             params: Optional[List[Token]] = None,
             statement_block: Optional[List[Token]] = None
             ) -> List[Token]:
    tokens = [get_token(return_type),
              get_token(TokenType.IDENTIFIER, name),
              get_token(TokenType.LEFT_ROUND_BRACKET)]
    if params:
        tokens += params
    tokens.append(get_token(TokenType.RIGHT_ROUND_BRACKET))
    tokens.append(get_token(TokenType.LEFT_CURLY_BRACKET))
    if statement_block:
        tokens += statement_block
    tokens.append(get_token(TokenType.RIGHT_CURLY_BRACKET))

    return tokens


def parameter(type: TokenType, name: str) -> List[Token]:
    return [get_token(type),
            get_token(TokenType.IDENTIFIER, name)]


def parameters(params: List[Tuple[TokenType, str]]) -> List[Token]:
    tokens = []

    for param in params:
        tokens += parameter(param[0], param[1])
        if param != params[-1]:
            tokens.append(get_token(TokenType.COMMA))

    return tokens


def if_statement(condition: List[Token], if_block: List[Token]) -> List[Token]:
    tokens = [get_token(TokenType.IF_KEYWORD),
              get_token(TokenType.LEFT_ROUND_BRACKET)]
    tokens += condition
    tokens.append(get_token(TokenType.RIGHT_ROUND_BRACKET))
    tokens.append(get_token(TokenType.LEFT_CURLY_BRACKET))
    tokens += if_block
    tokens.append(get_token(TokenType.RIGHT_CURLY_BRACKET))

    return tokens


def elif_statement(condition: List[Token], elif_block: List[Token]) -> List[Token]:
    tokens = [get_token(TokenType.ELIF_KEYWORD),
              get_token(TokenType.LEFT_ROUND_BRACKET)]
    tokens += condition
    tokens.append(get_token(TokenType.RIGHT_ROUND_BRACKET))
    tokens.append(get_token(TokenType.LEFT_CURLY_BRACKET))
    tokens += elif_block
    tokens.append(get_token(TokenType.RIGHT_CURLY_BRACKET))

    return tokens


def else_statement(else_block: List[Token]) -> List[Token]:
    tokens = [get_token(TokenType.ELSE_KEYWORD),
              get_token(TokenType.LEFT_CURLY_BRACKET)]
    tokens += else_block
    tokens.append(get_token(TokenType.RIGHT_CURLY_BRACKET))

    return tokens


def while_statement(condition: List[Token], statement_block: List[Token]) -> List[Token]:
    tokens = [get_token(TokenType.WHILE_KEYWORD),
              get_token(TokenType.LEFT_ROUND_BRACKET)]

    tokens += condition
    tokens.append(get_token(TokenType.RIGHT_ROUND_BRACKET))
    tokens.append(get_token(TokenType.LEFT_CURLY_BRACKET))
    tokens += statement_block
    tokens.append(get_token(TokenType.RIGHT_CURLY_BRACKET))

    return tokens


def return_statement(expression: List[Token]) -> List[Token]:
    tokens = [get_token(TokenType.RETURN_KEYWORD)]

    tokens += expression
    tokens.append(get_token(TokenType.SEMICOLON))

    return tokens


def exception(name: str,
              params: Optional[List[Token]] = None,
              attr: Optional[List[Token]] = None
              ) -> List[Token]:
    tokens = [get_token(TokenType.EXCEPTION_KEYWORD),
              get_token(TokenType.IDENTIFIER, name),
              get_token(TokenType.LEFT_ROUND_BRACKET)]
    if params:
        tokens += params
    tokens.append(get_token(TokenType.RIGHT_ROUND_BRACKET))
    tokens.append(get_token(TokenType.LEFT_CURLY_BRACKET))
    if attr:
        tokens += attr
    tokens.append(get_token(TokenType.RIGHT_CURLY_BRACKET))

    return tokens


def attribute(name: str, type: TokenType, expression: List[Token] = None) -> List[Token]:
    tokens = [get_token(TokenType.IDENTIFIER, name),
              get_token(TokenType.COLON),
              get_token(type)]

    if expression:
        tokens.append(get_token(TokenType.ASSIGNMENT))
        tokens += expression

    return tokens


def attributes(attribute_list: List[List[Token]]) -> List[Token]:
    tokens = []

    for attr in attribute_list:
        tokens += attr

    return tokens


def catch(catch_exception: List[Token], catch_block: List[Token]) -> List[Token]:
    tokens = [get_token(TokenType.CATCH_KEYWORD),
              get_token(TokenType.LEFT_ROUND_BRACKET)]
    tokens += catch_exception
    tokens.append(get_token(TokenType.RIGHT_ROUND_BRACKET))

    tokens.append(get_token(TokenType.LEFT_CURLY_BRACKET))
    tokens += catch_block
    tokens.append(get_token(TokenType.RIGHT_CURLY_BRACKET))

    return tokens


def try_catch(try_block: List[Token], catch_statements: List[List[Token]]) -> List[Token]:
    tokens = [get_token(TokenType.TRY_KEYWORD),
              get_token(TokenType.LEFT_CURLY_BRACKET)]
    tokens += try_block
    tokens.append(get_token(TokenType.RIGHT_CURLY_BRACKET))

    for catch_statement in catch_statements:
        tokens += catch_statement

    return tokens


def throw(exception_name: str, args: List[Token]) -> List[Token]:
    tokens = [get_token(TokenType.THROW_KEYWORD),
              get_token(TokenType.IDENTIFIER, exception_name),
              get_token(TokenType.LEFT_ROUND_BRACKET)]
    tokens += args
    tokens.append(get_token(TokenType.RIGHT_ROUND_BRACKET))
    tokens.append(get_token(TokenType.SEMICOLON))

    return tokens
