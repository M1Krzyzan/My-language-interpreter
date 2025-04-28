from typing import List

from src.lexer.position import Position
from src.lexer.token_ import Token, TokenType
from src.parser.parser import Parser


class MockedLexer:
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
        Token(TokenType.RIGHT_CURLY_BRACKET, Position(1, 1)),
        Token(TokenType.ETX, Position(1, 1))
    ])
    parser = Parser(lexer)
    parser.get_program()


