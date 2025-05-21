from src.ast.position import Position


def builtin_print(*args) -> None:
    print(*args)


def builtin_input() -> str:
    return input()


builtin_functions = {
    "print": builtin_print,
    "input": builtin_input
}


class BasicException(Exception):
    def __init__(self, position: Position, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.position = position


builtin_exceptions = {
    "BasicException": BasicException
}