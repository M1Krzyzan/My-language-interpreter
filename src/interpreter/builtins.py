from src.ast.position import Position


def builtin_print(*args) -> None:
    print(*args)


def builtin_input() -> str:
    return input()


builtin_functions = {
    "print": builtin_print,
    "input": builtin_input
}


class BasicException:
    def __init__(self, position: Position, message: str) -> None:
        self.position = position
        self.message = message


builtin_exceptions = {
    "BasicException": BasicException
}