from contextlib import AbstractContextManager
from dataclasses import dataclass

from src.lexer.position import Position


@dataclass
class Error:
    position: Position

class FatalError(Exception):
    ...


class ErrorManager(AbstractContextManager):
    def __enter__(self):
        self._errors = []
        return self

    def __exit__(self, __exc_type, __exc_value, __traceback):
        if self._errors:
            print("Errors found during program work: \n".join([str(error) for error in self._errors]))

    def critical_error(self, error: Error):
        self.add_error(error)
        raise FatalError

    def add_error(self, error: Error):
        self._errors.append(error)
        if len(self._errors) > 100:
            return False
        return True