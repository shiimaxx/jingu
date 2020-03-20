from enum import Enum, auto


class TokenType(Enum):
    DATA = auto()
    NAME = auto()
    VARIABLE_BEGIN = auto()
    VARIABLE_END = auto()
    BLOCK_BEGIN = auto()
    BLOCK_END = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    INTEGER = auto()
    STRING = auto()
    DOT = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()


class Token(object):
    def __init__(self, type, value):
        if type not in TokenType:
            raise TypeError("type must be specified TokenType object")
        self.type = type
        self.value = value

    def __eq__(self, value):
        return self.type == value.type and self.value == value.value

    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}')"


class Lexer(object):
    """TODO: move tokenize() from template.py"""
