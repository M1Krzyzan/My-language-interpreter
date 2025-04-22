from src.lexer.token_ import TokenType


class IntType:
    ...


class FloatType:
    ...


class BoolType:
    ...


class StringType:
    ...


class VoidType:
    ...


simple_types = {
    TokenType.INT_KEYWORD: IntType,
    TokenType.FLOAT_KEYWORD: FloatType,
    TokenType.BOOL_KEYWORD: BoolType,
    TokenType.STRING_KEYWORD: StringType,
}


class Type:
    def __init__(self, token_type: TokenType):
        self.type = simple_types.get(token_type)


class ReturnType(Type):
    def __init__(self, token_type: TokenType):
        super().__init__(token_type)
        if not self.type:
            self.type = VoidType
