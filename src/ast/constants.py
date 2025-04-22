from dataclasses import dataclass


@dataclass
class BoolLiteral:
    value: bool


@dataclass
class FloatLiteral:
    value: float


@dataclass
class IntLiteral:
    value: int


@dataclass
class StringLiteral:
    value: str
