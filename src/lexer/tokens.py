from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    INT_LITERAL = auto()
    FLOAT_LITERAL = auto()
    STRING_LITERAL = auto()
    OPERATOR = auto()
    PUNCTUATION = auto()
    EOF = auto()

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int
