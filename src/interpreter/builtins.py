from src.ast.position import Position


def builtin_print(*args) -> None:
    transform = lambda x: "true" if x is True else "false" if x is False else x
    print(*map(transform, args))


def builtin_input() -> str:
    return input()


builtin_functions = {
    "print": builtin_print,
    "input": builtin_input
}


class BasicException:
    def __init__(self, position: Position, message: str = "BasicException") -> None:
        self.position = position
        self.message = message


builtin_exceptions = {
    "BasicException": BasicException
}
