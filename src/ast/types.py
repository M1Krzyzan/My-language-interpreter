from src.lexer.token_ import TokenType


class IntType:
    def __eq__(self, other):
        return isinstance(other, IntType)


class FloatType:
    def __eq__(self, other):
        return isinstance(other, FloatType)


class BoolType:
    def __eq__(self, other):
        return isinstance(other, BoolType)


class StringType:
    def __eq__(self, other):
        return isinstance(other, StringType)


class VoidType:
    def __eq__(self, other):
        return isinstance(other, VoidType)


simple_types = {
    TokenType.INT_KEYWORD: IntType,
    TokenType.FLOAT_KEYWORD: FloatType,
    TokenType.BOOL_KEYWORD: BoolType,
    TokenType.STRING_KEYWORD: StringType,
}


class Type:
    def __init__(self, token_type: TokenType):
        self.type = simple_types.get(token_type)

    def __eq__(self, other):
        return self.type == other.type


class ReturnType(Type):
    def __init__(self, token_type: TokenType):
        super().__init__(token_type)
        if not self.type:
            self.type = VoidType

    def __eq__(self, other):
        return self.type == other.type
