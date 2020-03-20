from enum import Enum


class TokenType(Enum):
    DATA = 1
    NAME = 2
    VARIABLE_BEGIN = 3
    VARIABLE_END = 4
    BLOCK_BEGIN = 15
    BLOCK_END = 16
    LBRACKET = 5
    RBRACKET = 6
    INTEGER = 7
    STRING = 8
    DOT = 9
    ADD = 10
    SUB = 11
    MUL = 12
    DIV = 13
    MOD = 14


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
