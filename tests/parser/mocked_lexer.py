from typing import List

from src.lexer.lexer import Lexer
from src.ast.position import Position
from src.lexer.token_ import Token, TokenType
from src.parser.parser import Parser


class MockedLexer(Lexer):
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.index = 0

    def next_token(self) -> Token:
        index_mem = self.index
        self.index += 1
        return self.tokens[index_mem]


if __name__ == '__main__':
    lexer = MockedLexer([
        Token(TokenType.VOID_KEYWORD,Position(1,1)),
        Token(TokenType.IDENTIFIER, Position(1,1),"foo"),
        Token(TokenType.LEFT_ROUND_BRACKET, Position(1,1)),
        Token(TokenType.INT_KEYWORD, Position(1,1)),
        Token(TokenType.IDENTIFIER, Position(1,1), 'x'),
        Token(TokenType.COMMA, Position(1,1)),
        Token(TokenType.FLOAT_KEYWORD, Position(1, 1)),
        Token(TokenType.IDENTIFIER, Position(1, 1), 'y'),
        Token(TokenType.COMMA, Position(1, 1)),
        Token(TokenType.BOOL_KEYWORD, Position(1, 1)),
        Token(TokenType.IDENTIFIER, Position(1, 1), 'z'),
        Token(TokenType.COMMA, Position(1, 1)),
        Token(TokenType.STRING_KEYWORD, Position(1, 1)),
        Token(TokenType.IDENTIFIER, Position(1, 1), 'str'),
        Token(TokenType.RIGHT_ROUND_BRACKET, Position(1, 1)),
        Token(TokenType.LEFT_CURLY_BRACKET, Position(1, 1)),
        Token(TokenType.IF_KEYWORD, Position(1, 1)),
        Token(TokenType.LEFT_ROUND_BRACKET, Position(1, 1)),
        Token(TokenType.IDENTIFIER, Position(1, 1), 'x'),
        Token(TokenType.EQUAL_OPERATOR, Position(1, 1)),
        Token(TokenType.INT_LITERAL, Position(1, 1), 5),
        Token(TokenType.RIGHT_ROUND_BRACKET, Position(1, 1)),
        Token(TokenType.LEFT_CURLY_BRACKET, Position(1, 1)),
        Token(TokenType.IDENTIFIER, Position(1, 1), 'print'),
        Token(TokenType.LEFT_ROUND_BRACKET, Position(1,1)),
        Token(TokenType.INT_LITERAL, Position(1, 1), 3),
        Token(TokenType.MULTIPLICATION_OPERATOR, Position(1, 1)),
        Token(TokenType.INT_LITERAL, Position(1, 1), 3),
        Token(TokenType.PLUS_OPERATOR, Position(1, 1)),
        Token(TokenType.INT_LITERAL, Position(1, 1), 2),
        Token(TokenType.RIGHT_ROUND_BRACKET, Position(1,1)),
        Token(TokenType.SEMICOLON, Position(1, 1)),
        Token(TokenType.RIGHT_CURLY_BRACKET, Position(1, 1)),
        Token(TokenType.RIGHT_CURLY_BRACKET, Position(1, 1)),
        Token(TokenType.EXCEPTION_KEYWORD, Position(1, 1)),
        Token(TokenType.IDENTIFIER, Position(1, 1), 'MyException'),
        Token(TokenType.LEFT_ROUND_BRACKET, Position(1, 1)),
        # Token(TokenType.IDENTIFIER, Position(1, 1), 'msg'),
        # Token(TokenType.COMMA, Position(1, 1)),
        # Token(TokenType.IDENTIFIER, Position(1, 1), 'err'),
        Token(TokenType.RIGHT_ROUND_BRACKET, Position(1, 1)),
        Token(TokenType.LEFT_CURLY_BRACKET, Position(1, 1)),
        Token(TokenType.IDENTIFIER, Position(1, 1),'msg'),
        Token(TokenType.COLON, Position(1, 1)),
        Token(TokenType.STRING_KEYWORD, Position(1, 1)),
        Token(TokenType.ASSIGNMENT, Position(1, 1)),
        Token(TokenType.STRING_LITERAL, Position(1, 1), 'text'),
        Token(TokenType.SEMICOLON, Position(1, 1)),
        Token(TokenType.IDENTIFIER, Position(1, 1), 'err'),
        Token(TokenType.COLON, Position(1, 1)),
        Token(TokenType.INT_KEYWORD, Position(1, 1)),
        Token(TokenType.SEMICOLON, Position(1, 1)),
        # Token(TokenType.LEFT_CURLY_BRACKET, Position(1, 1)),
        Token(TokenType.RIGHT_CURLY_BRACKET, Position(1, 1)),
        Token(TokenType.ETX, Position(1, 1))
    ])
    parser = Parser(lexer)
    x =  parser.get_program()
    print(x)


