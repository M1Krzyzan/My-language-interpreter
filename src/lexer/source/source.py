from abc import ABC, abstractmethod

class Source(ABC):
    @abstractmethod
    def peek(self) -> str:
        """Look at the current character without consuming it."""
        pass

    @abstractmethod
    def next(self) -> str:
        """Consume and return the current character, moving to the next."""
        pass

    @abstractmethod
    def eof(self) -> bool:
        """Check if end of source is reached."""
        pass
