from src.ast.position import Position
from src.lexer.token_ import TokenType


class ParserError(Exception):
    def __init__(self, message: str, position: Position):
        super().__init__(message)
        self.message = message
        self.position = position

    def __str__(self):
        return f"\033[31mParserError: {self.message} at {self.position}"


class UnexpectedToken(ParserError):
    def __init__(self, position: Position, received: TokenType, expected: TokenType):
        self.received_token = received
        self.expected_token = expected
        message = f'Unexpected token - expected "{self.expected_token}", got "{self.received_token}"'
        super().__init__(message, position)


class ExpectedSimpleTypeError(ParserError):
    def __init__(self, position: Position, prev_token: TokenType):
        message = f"Expected simple type after {prev_token}"
        super().__init__(message, position)


class ExpectedExpressionError(ParserError):
    def __init__(self, position: Position, operator: TokenType):
        message = f"Missing expression after {operator}"
        super().__init__(message, position)


class ExpectedAttributesError(ParserError):
    def __init__(self, position: Position, keyword: str):
        message = f"Missing attributes in {keyword}"
        super().__init__(message, position)


class ExpectedParameterError(ParserError):
    def __init__(self, position: Position):
        message = f"Missing parameters"
        super().__init__(message, position)


class ExpectedConditionError(ParserError):
    def __init__(self, position: Position, keyword: TokenType):
        message = "Missing condition after %s" % keyword
        super().__init__(message, position)


class ExpectedStatementBlockError(ParserError):
    def __init__(self, position: Position, name: str):
        message = f"Missing statement block in {name}"
        super().__init__(message, position)


class UnknownTypeError(ParserError):
    def __init__(self, position: Position, type: TokenType):
        message = f"Unknown type, got {type}"
        super().__init__(message, position)


class ExpectedDeclarationError(ParserError):
    def __init__(self, position: Position):
        message = f'Expected Function or Exception declaration, got unexpected declaration type'
        super().__init__(message, position)


class DeclarationExistsError(ParserError):
    def __init__(self, position: Position, name: str):
        message = f'Duplicate declaration - name="{name}"'
        super().__init__(message, position)
