from io import StringIO
import re

from .lexer import Lexer, Token, TokenType


class ParseError(Exception):
    pass


class Environment(object):
    def __init__(self):
        pass

    def get_template(self, template_file):
        with open(template_file, "r") as f:
            return Template(f.read())


class Template(object):
    NAME_PATTERN = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")
    VARIABLE_BEGIN_PATTERN = re.compile(r"{{")
    VARIABLE_END_PATTERN = re.compile(r"}}")
    BLOCK_BEGIN_PATTERN = re.compile(r"{%")
    BLOCK_END_PATTERN = re.compile(r"%}")
    LBRACKET_PATTERN = re.compile(r"\[")
    RBRACKET_PATTERN = re.compile(r"]")
    INTEGER_PATTERN = re.compile(r"[0-9]+")
    STRING_PATTERN = re.compile(r"'(.*?)'|\"(.*?)\"")
    DOT_PATTERN = re.compile(r"\.")
    ADD_PATTERN = re.compile(r"\+")
    SUB_PATTERN = re.compile(r"-")
    MUL_PATTERN = re.compile(r"\*")
    DIV_PATTERN = re.compile(r"/")
    MOD_PATTERN = re.compile(r"%")

    def __init__(self, source):
        self.source = source
        self.stream = StringIO()

    def _match_operators(self, content, pos):
        return self.ADD_PATTERN.match(content, pos) \
            or self.SUB_PATTERN.match(content, pos) \
            or self.MUL_PATTERN.match(content, pos) \
            or self.DIV_PATTERN.match(content, pos) \
            or self.MOD_PATTERN.match(content, pos)

    def render(self, *args, **kwargs):
        tokens = self.tokenize(self.source)
        nodes = self.parse(tokens)
        for n in nodes:
            self.stream.write(n.visit())

        code = self.stream.getvalue()
        source = compile(code, "", "exec")

        globals_ = kwargs
        locals_ = {}
        exec(source, globals_, locals_)
        return ''.join(locals_['output']())

    def tokenize(self, content):
        text = ""
        tokens = []
        pos = 0
        inner_block = False

        def skip_whitespace(pos):
            while True:
                if content[pos] == " ":
                    pos += 1
                    continue
                else:
                    break
            return pos

        # tokenize
        while True:
            m = self.VARIABLE_BEGIN_PATTERN.match(content, pos) or self.BLOCK_BEGIN_PATTERN.match(content, pos)
            if m:
                # flush text
                if len(text) > 0:
                    tokens.append(Token(TokenType.DATA, text))
                    text = ""

                # variable block
                if m.re is self.VARIABLE_BEGIN_PATTERN:
                    g = m.group()
                    tokens.append(Token(TokenType.VARIABLE_BEGIN, g))
                    pos = m.end()

                    pos = skip_whitespace(pos)

                    name_or_int_m = self.NAME_PATTERN.match(content, pos) or self.INTEGER_PATTERN.match(content, pos)
                    if name_or_int_m is None:
                        raise SyntaxError()

                    if name_or_int_m.re is self.INTEGER_PATTERN:
                        tokens.append(Token(TokenType.INTEGER, name_or_int_m.group()))
                        pos = name_or_int_m.end()
                    elif name_or_int_m.re is self.NAME_PATTERN:
                        tokens.append(Token(TokenType.NAME, name_or_int_m.group()))
                        pos = name_or_int_m.end()
                    else:
                        raise SyntaxError()

                    if name_or_int_m.re is self.NAME_PATTERN:
                        lbracket_or_dot_m = self.LBRACKET_PATTERN.match(content, pos) or self.DOT_PATTERN.match(content, pos)
                        if lbracket_or_dot_m:
                            if lbracket_or_dot_m.re is self.LBRACKET_PATTERN:
                                lbracket_m = lbracket_or_dot_m
                                tokens.append(Token(TokenType.LBRACKET, lbracket_m.group()))
                                pos = lbracket_m.end()

                                int_or_str_m = self.INTEGER_PATTERN.match(content, pos) or self.STRING_PATTERN.match(content, pos)
                                if int_or_str_m is None:
                                    raise SyntaxError()

                                if int_or_str_m.re is self.INTEGER_PATTERN:
                                    tokens.append(Token(TokenType.INTEGER, int_or_str_m.group()))
                                elif int_or_str_m.re is self.STRING_PATTERN:
                                    if int_or_str_m.group().startswith("'"):
                                        s = int_or_str_m.group().strip("'")
                                    elif int_or_str_m.group().startswith('"'):
                                        s = int_or_str_m.group().strip('"')
                                    tokens.append(Token(TokenType.STRING, s))
                                else:
                                    raise SyntaxError()

                                pos = int_or_str_m.end()

                                rbracket_m = self.RBRACKET_PATTERN.match(content, pos)
                                if rbracket_m is None:
                                    raise SyntaxError()
                                tokens.append(Token(TokenType.RBRACKET, rbracket_m.group()))
                                pos = rbracket_m.end()

                            elif lbracket_or_dot_m.re is self.DOT_PATTERN:
                                dot_m = lbracket_or_dot_m
                                if dot_m is None:
                                    raise SyntaxError()
                                tokens.append(Token(TokenType.DOT, dot_m.group()))
                                pos = dot_m.end()

                                str_m = self.NAME_PATTERN.match(content, pos)
                                if str_m is None:
                                    raise SyntaxError()
                                tokens.append(Token(TokenType.NAME, str_m.group()))
                                pos = str_m.end()

                    pos = skip_whitespace(pos)

                    # calculate
                    while True:
                        op_m = self._match_operators(content, pos)
                        if op_m is None:
                            break

                        if op_m.re is self.ADD_PATTERN:
                            tokens.append(Token(TokenType.ADD, op_m.group()))
                        if op_m.re is self.SUB_PATTERN:
                            tokens.append(Token(TokenType.SUB, op_m.group()))
                        if op_m.re is self.MUL_PATTERN:
                            tokens.append(Token(TokenType.MUL, op_m.group()))
                        if op_m.re is self.DIV_PATTERN:
                            tokens.append(Token(TokenType.DIV, op_m.group()))
                        if op_m.re is self.MOD_PATTERN:
                            tokens.append(Token(TokenType.MOD, op_m.group()))
                        pos = op_m.end()

                        pos = skip_whitespace(pos)

                        name_or_int_m = self.NAME_PATTERN.match(content, pos) or self.INTEGER_PATTERN.match(content, pos)
                        if name_or_int_m is None:
                            raise SyntaxError()

                        if name_or_int_m.re is self.INTEGER_PATTERN:
                            tokens.append(Token(TokenType.INTEGER, name_or_int_m.group()))
                            pos = name_or_int_m.end()
                        elif name_or_int_m.re is self.NAME_PATTERN:
                            tokens.append(Token(TokenType.NAME, name_or_int_m.group()))
                            pos = name_or_int_m.end()

                        if name_or_int_m.re is self.NAME_PATTERN:
                            lbracket_or_dot_m = self.LBRACKET_PATTERN.match(content, pos) or self.DOT_PATTERN.match(content, pos)
                            if lbracket_or_dot_m:
                                if lbracket_or_dot_m.re is self.LBRACKET_PATTERN:
                                    lbracket_m = lbracket_or_dot_m
                                    tokens.append(Token(TokenType.LBRACKET, lbracket_m.group()))
                                    pos = lbracket_m.end()

                                    int_or_str_m = self.INTEGER_PATTERN.match(content, pos) or self.STRING_PATTERN.match(content, pos)
                                    if int_or_str_m is None:
                                        raise SyntaxError()

                                    if int_or_str_m.re is self.INTEGER_PATTERN:
                                        tokens.append(Token(TokenType.INTEGER, int_or_str_m.group()))
                                    elif int_or_str_m.re is self.STRING_PATTERN:
                                        if int_or_str_m.group().startswith("'"):
                                            s = int_or_str_m.group().strip("'")
                                        elif int_or_str_m.group().startswith('"'):
                                            s = int_or_str_m.group().strip('"')
                                        tokens.append(Token(TokenType.STRING, s))
                                    else:
                                        raise SyntaxError()

                                    pos = int_or_str_m.end()

                                    rbracket_m = self.RBRACKET_PATTERN.match(content, pos)
                                    if rbracket_m is None:
                                        raise SyntaxError()
                                    tokens.append(Token(TokenType.RBRACKET, rbracket_m.group()))
                                    pos = rbracket_m.end()

                                elif lbracket_or_dot_m.re is self.DOT_PATTERN:
                                    dot_m = lbracket_or_dot_m
                                    if dot_m is None:
                                        raise SyntaxError()
                                    tokens.append(Token(TokenType.DOT, dot_m.group()))
                                    pos = dot_m.end()

                                    str_m = self.NAME_PATTERN.match(content, pos)
                                    if str_m is None:
                                        raise SyntaxError()
                                    tokens.append(Token(TokenType.NAME, str_m.group()))
                                    pos = str_m.end()
                        pos = skip_whitespace(pos)

                    pos = skip_whitespace(pos)

                    mmm = self.VARIABLE_END_PATTERN.match(content, pos)
                    if mmm is None:
                        raise SyntaxError()

                    g = mmm.group()
                    tokens.append(Token(TokenType.VARIABLE_END, g))
                    pos = mmm.end()

                    if pos >= len(content):
                        break

                    continue

                if m.re is self.BLOCK_BEGIN_PATTERN:
                    g = m.group()
                    tokens.append(Token(TokenType.BLOCK_BEGIN, g))
                    pos = m.end()

                    pos = skip_whitespace(pos)

                    if not inner_block:
                        name_m = self.NAME_PATTERN.match(content, pos)
                        if name_m is None:
                            raise SyntaxError()
                        g = name_m.group()
                        tokens.append(Token(TokenType.NAME, g))
                        pos = name_m.end()

                        pos = skip_whitespace(pos)

                        name_or_int_m = self.NAME_PATTERN.match(content, pos) or self.INTEGER_PATTERN.match(content, pos)
                        if name_or_int_m is None:
                            raise SyntaxError()

                        if name_or_int_m.re is self.INTEGER_PATTERN:
                            tokens.append(Token(TokenType.INTEGER, name_or_int_m.group()))
                            pos = name_or_int_m.end()
                        elif name_or_int_m.re is self.NAME_PATTERN:
                            tokens.append(Token(TokenType.NAME, name_or_int_m.group()))
                            pos = name_or_int_m.end()
                        else:
                            raise SyntaxError()
                    else:
                        name_m = self.NAME_PATTERN.match(content, pos)
                        if name_m is None:
                            raise SyntaxError()
                        g = name_m.group()
                        tokens.append(Token(TokenType.NAME, g))
                        pos = name_m.end()

                        pos = skip_whitespace(pos)

                    inner_block = not inner_block

                    pos = skip_whitespace(pos)

                    mmm = self.BLOCK_END_PATTERN.match(content, pos)
                    if mmm is None:
                        raise SyntaxError()

                    g = mmm.group()
                    tokens.append(Token(TokenType.BLOCK_END, g))
                    pos = mmm.end()

                    if pos >= len(content):
                        break

                    continue

            text += content[pos]
            pos += 1

            if pos >= len(content):
                if len(text) > 0:
                    tokens.append(Token(TokenType.DATA, text))
                break

        return tokens

    def parse(self, tokens):
        nodes = [RootNode()]

        i = 0
        while True:
            t = tokens[i]
            if t.token_type == TokenType.DATA:
                nodes.append(DataNode(t.value))
            elif t.token_type == TokenType.VARIABLE_BEGIN:
                nodes.append(SkipNode(t.value))
                i += 1

                while True:
                    t = tokens[i]

                    if t.token_type == TokenType.NAME:
                        j = i + 1
                        if tokens[j].token_type == TokenType.LBRACKET:
                            j += 1
                            next_t = tokens[j]
                            if next_t.token_type not in (TokenType.INTEGER, TokenType.STRING):
                                raise ParseError()
                            index = next_t.value

                            j += 1
                            next_t = tokens[j]
                            if next_t.token_type != TokenType.RBRACKET:
                                raise ParseError()
                            nodes.append(GetNode(t.value, index))
                            j += 1

                            i = j
                        elif tokens[j].token_type == TokenType.DOT:
                            j += 1
                            next_t = tokens[j]
                            if next_t.token_type != TokenType.NAME:
                                raise ParseError()
                            index = next_t.value
                            nodes.append(GetNode(t.value, index))
                            j += 1

                            i = j
                        else:
                            nodes.append(NameNode(t.value))
                            i += 1
                    elif t.token_type == TokenType.INTEGER:
                        nodes.append(ConstNode(t.value))
                        i += 1

                    t = tokens[i]

                    if t.token_type in [TokenType.ADD, TokenType.SUB, TokenType.MUL, TokenType.DIV, TokenType.MOD]:
                        left = nodes.pop()
                        op = t.value

                        right = None
                        i = i + 1
                        t = tokens[i]
                        if t.token_type == TokenType.NAME:
                            j = i + 1
                            if tokens[j].token_type == TokenType.LBRACKET:
                                j += 1
                                next_t = tokens[j]
                                if next_t.token_type not in (TokenType.INTEGER, TokenType.STRING):
                                    raise ParseError()
                                index = next_t.value

                                j += 1
                                next_t = tokens[j]
                                if next_t.token_type != TokenType.RBRACKET:
                                    raise ParseError()
                                right = GetNode(t.value, index)
                                j += 1

                                i = j
                            elif tokens[j].token_type == TokenType.DOT:
                                j += 1
                                next_t = tokens[j]
                                if next_t.token_type != TokenType.NAME:
                                    raise ParseError()
                                index = next_t.value
                                right = GetNode(t.value, index)
                                j += 1

                                i = j
                            else:
                                right = NameNode(t.value)
                                i += 1
                        elif t.token_type == TokenType.INTEGER:
                            right = ConstNode(t.value)
                            i += 1

                        nodes.append(CalcNode(op, left, right))

                    t = tokens[i]
                    if t.token_type == TokenType.VARIABLE_END:
                        nodes.append(SkipNode(t.value))
                        break

            elif t.token_type == TokenType.BLOCK_BEGIN:
                i += 1
                t = tokens[i]
                if t.token_type == TokenType.NAME and t.value == "if":
                    i += 1
                    if tokens[i].token_type == TokenType.NAME:
                        test = tokens[i].value

                    i += 1
                    if tokens[i].token_type == TokenType.BLOCK_END:
                        if_node = IfNode(test)

                    i += 1
                    if tokens[i].token_type == TokenType.DATA:
                        data = DataNode(tokens[i].value)

                    i += 1
                    if tokens[i].token_type == TokenType.BLOCK_BEGIN:
                        i += 1
                        if tokens[i].token_type == TokenType.NAME and tokens[i].value == "endif":
                            i += 1
                            if tokens[i].token_type == TokenType.BLOCK_END:
                                if_node.body = data
                                nodes.append(if_node)

            i += 1
            if i >= len(tokens):
                break

        return nodes


class Node(object):
    code = ""


class RootNode(Node):

    def visit(self):
        return "def output():\n"


class SkipNode(Node):

    def __init__(self, value):
        self.value = value

    def visit(self):
        """skip"""
        return ""


class DataNode(Node):

    def __init__(self, value):
        self.value = value

    def _escape_newline(self):
        if '\n' in self.value:
            v = self.value.split('\n')
            return '\\n'.join(v)
        return self.value

    def visit(self):
        v = self._escape_newline()
        return f"    yield '{v}'\n"


class NameNode(Node):

    def __init__(self, value):
        self.value = value

    def visit(self):
        return f"    yield {self.value}\n"


class GetNode(Node):

    def __init__(self, value, index):
        self.value = value
        self.index = index

    def visit(self):
        if self.index.isdigit():
            return f"    yield {self.value}[{self.index}]\n"
        else:
            return f"    yield {self.value}['{self.index}']\n"


class ConstNode(Node):

    def __init__(self, value):
        self.value = value


class CalcNode(Node):

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    @property
    def expand(self):
        if isinstance(self.left, CalcNode):
            left = self.left.expand
        elif isinstance(self.left, NameNode):
            left = self.left.value
        else:
            left = int(self.left.value)

        if isinstance(self.right, CalcNode):
            right = self.right.expand
        elif isinstance(self.right, NameNode):
            right = self.right.value
        else:
            right = int(self.right.value)

        return f"{left} {self.op} {right}"

    def visit(self):
        if isinstance(self.left, CalcNode):
            left = self.left.expand
        elif isinstance(self.left, NameNode):
            left = self.left.value
        else:
            left = int(self.left.value)

        if isinstance(self.right, CalcNode):
            right = self.right.expand
        elif isinstance(self.right, NameNode):
            right = self.right.value
        else:
            right = int(self.right.value)

        return f"    yield str({left} {self.op} {right})\n"


class IfNode(Node):

    def __init__(self, test, body=None):
        self.test = test
        self.body = body

    def visit(self):
        b = self.body._escape_newline()
        return f"""
    if {self.test}:
        yield '{b}'
"""
