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
    def __init__(self, token_type, value):
        if token_type not in TokenType:
            raise TypeError("token_type must be specified TokenType")
        self.token_type = token_type
        self.value = value

    def __eq__(self, value):
        return self.token_type == value.token_type and self.value == value.value


class Lexer(object):
    """TODO: move tokenize() from template.py"""
