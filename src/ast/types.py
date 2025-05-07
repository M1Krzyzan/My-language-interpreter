from src.lexer.token_ import TokenType


class SimpleType:
    def __eq__(self, other):
        return isinstance(other, type(self))


class IntType(SimpleType):
    def __str__(self):
        return "int"


class FloatType(SimpleType):
    def __str__(self):
        return "float"


class BoolType(SimpleType):
    def __str__(self):
        return "bool"


class StringType(SimpleType):
    def __str__(self):
        return "string"


class VoidType:
    def __str__(self):
        return "void"

    def __eq__(self, other):
        return isinstance(other, VoidType)


TOKEN_TO_TYPE_MAP = {
    TokenType.INT_KEYWORD: IntType,
    TokenType.FLOAT_KEYWORD: FloatType,
    TokenType.BOOL_KEYWORD: BoolType,
    TokenType.STRING_KEYWORD: StringType,
}


class ReturnType:
    def __init__(self, token_type: TokenType):
        if token_type == TokenType.VOID_KEYWORD:
            self.type = VoidType()
        else:
            type_cls = TOKEN_TO_TYPE_MAP.get(token_type)
            self.type = type_cls()

    def __eq__(self, other):
        return self.type == other.type
