import unittest

from jingu.template import Environment, Template, Token, TokenType, NameNode, DataNode, GetNode, RootNode, SkipNode, CalcNode, ConstNode


class TestEnvironment(unittest.TestCase):
    def test_get_template(self):
        env = Environment()
        testfile = 'tests/data/test_template.html'
        tmpl = env.get_template(testfile)
        with open(testfile, "r") as f:
            source = f.read()

        self.assertEqual(tmpl.source, source)


class TestTemplate(unittest.TestCase):
    def test_render(self):
        tmpl = Template("Hello {{ name }}!")
        actual = tmpl.render(name='John Doe')
        expected = "Hello John Doe!"
        self.assertEqual(actual, expected)

    def test_reder__variable_end(self):
        tmpl = Template("Hello {{ name }}")
        actual = tmpl.render(name='John Doe')
        expected = "Hello John Doe"
        self.assertEqual(actual, expected)

    def test_render__multi_variable(self):
        tmpl = Template("Hello {{ name1 }} and {{ name2 }}!")
        actual = tmpl.render(name1='John Doe', name2="Jane Doe")
        expected = "Hello John Doe and Jane Doe!"
        self.assertEqual(actual, expected)

    def test_render__newline(self):
        tmpl = Template("<html>\n{{ body }}\n</html>")
        actual = tmpl.render(body='test')
        expected = "<html>\ntest\n</html>"
        self.assertEqual(actual, expected)

    def test_render__list_variable(self):
        tmpl = Template("Hello {{ name[0] }}!")
        actual = tmpl.render(name=['John Doe'])
        expected = "Hello John Doe!"
        self.assertEqual(actual, expected)

    def test_render__dict_variable(self):
        tmpl = Template("Hello {{ person['name'] }}!")
        actual = tmpl.render(person={'name': 'John Doe'})
        expected = "Hello John Doe!"
        self.assertEqual(actual, expected)

    def test_render__dict_variable_as_attribute(self):
        tmpl = Template("Hello {{ person.name }}!")
        actual = tmpl.render(person={'name': 'John Doe'})
        expected = "Hello John Doe!"
        self.assertEqual(actual, expected)

    def test_render__calculate(self):
        for s in [
            ("1 + 1 = {{ 1 + 1 }}", "1 + 1 = 2"),
            ("1 - 1 = {{ 1 - 1 }}", "1 - 1 = 0"),
            ("2 * 2 = {{ 2 * 2 }}", "2 * 2 = 4"),
            ("4 / 2 = {{ 4 / 2 }}", "4 / 2 = 2.0"),
            ("5 % 2 = {{ 5 % 2 }}", "5 % 2 = 1"),
        ]:
            with self.subTest(s=s):
                tmpl = Template(s[0])
                actual = tmpl.render()
                expected = s[1]
                self.assertEqual(actual, expected)

    def test_render__calculate_with_more_values(self):
        for s in [
            ("1 + 2 + 3 = {{ 1 + 2 + 3 }}", "1 + 2 + 3 = 6"),
            ("1 + 2 - 3 = {{ 1 + 2 - 3 }}", "1 + 2 - 3 = 0"),
            ("1 + 2 - 3 + 4 = {{ 1 + 2 - 3 + 4 }}", "1 + 2 - 3 + 4 = 4"),
            # TODO: Implement order of operations
            # ("1 + 2 * 3 = {{ 1 + 2 * 3 }}", "1 + 2 * 3 = 7"),
            # ("1 + 2 / 4 = {{ 1 + 2 / 4 }}", "1 + 2 / 4 = 1.5"),
            # ("1 + 2 % 5 = {{ 1 + 2 % 5 }}", "1 + 2 % 5 = 3"),
        ]:
            with self.subTest(s=s):
                tmpl = Template(s[0])
                actual = tmpl.render()
                expected = s[1]
                self.assertEqual(actual, expected)

    def test_render__calculate_with_variables(self):
        for s in [
            ("1 + n = {{ 1 + n }}", 2, "1 + n = 3"),
            # TODO:
            # ("1 + n + n = {{ 1 + n + n }}", 2, "1 + n + n = 5")
        ]:
            with self.subTest(s=s):
                tmpl = Template(s[0])
                actual = tmpl.render(n=s[1])
                expected = s[2]
                self.assertEqual(actual, expected)

    def test_tokenize__variable(self):
        tmpl = Template("")
        self.assertEqual(tmpl.tokenize("test"), [Token(TokenType.DATA, "test")])

        tokens = tmpl.tokenize("<html>{{ dummy }}</html>")
        self.assertEqual(len(tokens), 5)
        self.assertEqual(tokens[0], Token(TokenType.DATA, "<html>"))
        self.assertEqual(tokens[1], Token(TokenType.VARIABLE_BEGIN, "{{"))
        self.assertEqual(tokens[2], Token(TokenType.NAME, "dummy"))
        self.assertEqual(tokens[3], Token(TokenType.VARIABLE_END, "}}"))
        self.assertEqual(tokens[4], Token(TokenType.DATA, "</html>"))

    def test_tokenize__multi_variables(self):
        tmpl = Template("")

        tokens = tmpl.tokenize("""<html>
{{ dummy }}
{{ dummy2 }}
</html>""")
        self.assertEqual(len(tokens), 9)
        self.assertEqual(tokens[0], Token(TokenType.DATA, "<html>\n"))
        self.assertEqual(tokens[1], Token(TokenType.VARIABLE_BEGIN, "{{"))
        self.assertEqual(tokens[2], Token(TokenType.NAME, "dummy"))
        self.assertEqual(tokens[3], Token(TokenType.VARIABLE_END, "}}"))
        self.assertEqual(tokens[4], Token(TokenType.DATA, "\n"))
        self.assertEqual(tokens[5], Token(TokenType.VARIABLE_BEGIN, "{{"))
        self.assertEqual(tokens[6], Token(TokenType.NAME, "dummy2"))
        self.assertEqual(tokens[7], Token(TokenType.VARIABLE_END, "}}"))
        self.assertEqual(tokens[8], Token(TokenType.DATA, "\n</html>"))

    def test_tokenize__list_variable(self):
        tmpl = Template("")

        tokens = tmpl.tokenize("<html>{{ dummy[0] }}</html>")
        self.assertEqual(len(tokens), 8)
        self.assertEqual(tokens[0], Token(TokenType.DATA, "<html>"))
        self.assertEqual(tokens[1], Token(TokenType.VARIABLE_BEGIN, "{{"))
        self.assertEqual(tokens[2], Token(TokenType.NAME, "dummy"))
        self.assertEqual(tokens[3], Token(TokenType.LBRACKET, "["))
        self.assertEqual(tokens[4], Token(TokenType.INTEGER, "0"))
        self.assertEqual(tokens[5], Token(TokenType.RBRACKET, "]"))
        self.assertEqual(tokens[6], Token(TokenType.VARIABLE_END, "}}"))
        self.assertEqual(tokens[7], Token(TokenType.DATA, "</html>"))

    def test_tokenize__multi_list_variable(self):
        tmpl = Template("")

        tokens = tmpl.tokenize("<html>{{ dummy[0] }} and {{ dummy[1] }}</html>")
        self.assertEqual(len(tokens), 15)
        self.assertEqual(tokens[0], Token(TokenType.DATA, "<html>"))
        self.assertEqual(tokens[1], Token(TokenType.VARIABLE_BEGIN, "{{"))
        self.assertEqual(tokens[2], Token(TokenType.NAME, "dummy"))
        self.assertEqual(tokens[3], Token(TokenType.LBRACKET, "["))
        self.assertEqual(tokens[4], Token(TokenType.INTEGER, "0"))
        self.assertEqual(tokens[5], Token(TokenType.RBRACKET, "]"))
        self.assertEqual(tokens[6], Token(TokenType.VARIABLE_END, "}}"))
        self.assertEqual(tokens[7], Token(TokenType.DATA, " and "))
        self.assertEqual(tokens[8], Token(TokenType.VARIABLE_BEGIN, "{{"))
        self.assertEqual(tokens[9], Token(TokenType.NAME, "dummy"))
        self.assertEqual(tokens[10], Token(TokenType.LBRACKET, "["))
        self.assertEqual(tokens[11], Token(TokenType.INTEGER, "1"))
        self.assertEqual(tokens[12], Token(TokenType.RBRACKET, "]"))
        self.assertEqual(tokens[13], Token(TokenType.VARIABLE_END, "}}"))
        self.assertEqual(tokens[14], Token(TokenType.DATA, "</html>"))

    def test_tokenize__dict_variable(self):
        tmpl = Template("")

        tokens = tmpl.tokenize("<html>{{ dummy['key'] }}</html>")
        self.assertEqual(len(tokens), 8)
        self.assertEqual(tokens[0], Token(TokenType.DATA, "<html>"))
        self.assertEqual(tokens[1], Token(TokenType.VARIABLE_BEGIN, "{{"))
        self.assertEqual(tokens[2], Token(TokenType.NAME, "dummy"))
        self.assertEqual(tokens[3], Token(TokenType.LBRACKET, "["))
        self.assertEqual(tokens[4], Token(TokenType.STRING, "key"))
        self.assertEqual(tokens[5], Token(TokenType.RBRACKET, "]"))
        self.assertEqual(tokens[6], Token(TokenType.VARIABLE_END, "}}"))
        self.assertEqual(tokens[7], Token(TokenType.DATA, "</html>"))

    def test_tokenize__dict_variable_as_attribute(self):
        tmpl = Template("")

        tokens = tmpl.tokenize("<html>{{ dummy.key }}</html>")
        self.assertEqual(len(tokens), 7)
        self.assertEqual(tokens[0], Token(TokenType.DATA, "<html>"))
        self.assertEqual(tokens[1], Token(TokenType.VARIABLE_BEGIN, "{{"))
        self.assertEqual(tokens[2], Token(TokenType.NAME, "dummy"))
        self.assertEqual(tokens[3], Token(TokenType.DOT, "."))
        self.assertEqual(tokens[4], Token(TokenType.NAME, "key"))
        self.assertEqual(tokens[5], Token(TokenType.VARIABLE_END, "}}"))
        self.assertEqual(tokens[6], Token(TokenType.DATA, "</html>"))

    def test_tokenize__multi_dict_variable(self):
        tmpl = Template("")

        tokens = tmpl.tokenize("<html>{{ dummy['key'] }} and {{ dummy2['key'] }}</html>")
        self.assertEqual(len(tokens), 15)
        self.assertEqual(tokens[0], Token(TokenType.DATA, "<html>"))
        self.assertEqual(tokens[1], Token(TokenType.VARIABLE_BEGIN, "{{"))
        self.assertEqual(tokens[2], Token(TokenType.NAME, "dummy"))
        self.assertEqual(tokens[3], Token(TokenType.LBRACKET, "["))
        self.assertEqual(tokens[4], Token(TokenType.STRING, "key"))
        self.assertEqual(tokens[5], Token(TokenType.RBRACKET, "]"))
        self.assertEqual(tokens[6], Token(TokenType.VARIABLE_END, "}}"))
        self.assertEqual(tokens[7], Token(TokenType.DATA, " and "))
        self.assertEqual(tokens[8], Token(TokenType.VARIABLE_BEGIN, "{{"))
        self.assertEqual(tokens[9], Token(TokenType.NAME, "dummy2"))
        self.assertEqual(tokens[10], Token(TokenType.LBRACKET, "["))
        self.assertEqual(tokens[11], Token(TokenType.STRING, "key"))
        self.assertEqual(tokens[12], Token(TokenType.RBRACKET, "]"))
        self.assertEqual(tokens[13], Token(TokenType.VARIABLE_END, "}}"))
        self.assertEqual(tokens[14], Token(TokenType.DATA, "</html>"))

    def test_tokenize__calculate(self):
        tmpl = Template("")

        tokens = tmpl.tokenize("{{ 1 + 2 - num1 * num2 / num3 % num4 }}")
        self.assertEqual(len(tokens), 13)
        self.assertEqual(tokens[0], Token(TokenType.VARIABLE_BEGIN, "{{"))
        self.assertEqual(tokens[1], Token(TokenType.INTEGER, "1"))
        self.assertEqual(tokens[2], Token(TokenType.ADD, "+"))
        self.assertEqual(tokens[3], Token(TokenType.INTEGER, "2"))
        self.assertEqual(tokens[4], Token(TokenType.SUB, "-"))
        self.assertEqual(tokens[5], Token(TokenType.NAME, "num1"))
        self.assertEqual(tokens[6], Token(TokenType.MUL, "*"))
        self.assertEqual(tokens[7], Token(TokenType.NAME, "num2"))
        self.assertEqual(tokens[8], Token(TokenType.DIV, "/"))
        self.assertEqual(tokens[9], Token(TokenType.NAME, "num3"))
        self.assertEqual(tokens[10], Token(TokenType.MOD, "%"))
        self.assertEqual(tokens[11], Token(TokenType.NAME, "num4"))
        self.assertEqual(tokens[12], Token(TokenType.VARIABLE_END, "}}"))

    def test_tokenize__newline(self):
        tmpl = Template("")
        tokens = tmpl.tokenize("<html>\n{{ dummy }}\n</html>")
        self.assertEqual(len(tokens), 5)
        self.assertEqual(tokens[0], Token(TokenType.DATA, "<html>\n"))
        self.assertEqual(tokens[1], Token(TokenType.VARIABLE_BEGIN, "{{"))
        self.assertEqual(tokens[2], Token(TokenType.NAME, "dummy"))
        self.assertEqual(tokens[3], Token(TokenType.VARIABLE_END, "}}"))
        self.assertEqual(tokens[4], Token(TokenType.DATA, "\n</html>"))

    def test_tokenize__syntax_error(self):
        tmpl = Template("")

        for s in [
            "<html>{{ dummy }</html>",
            "<html>{{ dummy </html>",
            "<html>{{ }}</html>"
        ]:
            with self.subTest(s=s):
                with self.assertRaises(SyntaxError):
                    tmpl.tokenize(s)

    def test_parse(self):
        tmpl = Template("")

        tokens = [
            Token(TokenType.DATA, "<html>"),
            Token(TokenType.VARIABLE_BEGIN, "{{"),
            Token(TokenType.NAME, "dummy"),
            Token(TokenType.VARIABLE_END, "}}"),
            Token(TokenType.DATA, "</html>"),
        ]
        actual = tmpl.parse(tokens)
        self.assertIsInstance(actual[0], RootNode)
        self.assertIsInstance(actual[1], DataNode)
        self.assertIsInstance(actual[2], SkipNode)
        self.assertIsInstance(actual[3], NameNode)
        self.assertIsInstance(actual[4], SkipNode)
        self.assertIsInstance(actual[5], DataNode)

    def test_parse__list_variable(self):
        tmpl = Template("")

        tokens = [
            Token(TokenType.DATA, "<html>"),
            Token(TokenType.VARIABLE_BEGIN, "{{"),
            Token(TokenType.NAME, "dummy"),
            Token(TokenType.LBRACKET, "["),
            Token(TokenType.INTEGER, "0"),
            Token(TokenType.RBRACKET, "]"),
            Token(TokenType.VARIABLE_END, "}}"),
            Token(TokenType.DATA, "</html>"),
        ]
        actual = tmpl.parse(tokens)
        self.assertIsInstance(actual[0], RootNode)
        self.assertIsInstance(actual[1], DataNode)
        self.assertIsInstance(actual[2], SkipNode)
        self.assertIsInstance(actual[3], GetNode)
        self.assertIsInstance(actual[4], SkipNode)
        self.assertIsInstance(actual[5], DataNode)

    def test_parse__dict_variable(self):
        tmpl = Template("")

        tokens = [
            Token(TokenType.DATA, "<html>"),
            Token(TokenType.VARIABLE_BEGIN, "{{"),
            Token(TokenType.NAME, "dummy"),
            Token(TokenType.LBRACKET, "["),
            Token(TokenType.STRING, "key"),
            Token(TokenType.RBRACKET, "]"),
            Token(TokenType.VARIABLE_END, "}}"),
            Token(TokenType.DATA, "</html>"),
        ]
        actual = tmpl.parse(tokens)
        self.assertIsInstance(actual[0], RootNode)
        self.assertIsInstance(actual[1], DataNode)
        self.assertIsInstance(actual[2], SkipNode)
        self.assertIsInstance(actual[3], GetNode)
        self.assertIsInstance(actual[4], SkipNode)
        self.assertIsInstance(actual[5], DataNode)

    def test_parse__dict_variable_as_attribute(self):
        tmpl = Template("")

        tokens = [
            Token(TokenType.DATA, "<html>"),
            Token(TokenType.VARIABLE_BEGIN, "{{"),
            Token(TokenType.NAME, "dummy"),
            Token(TokenType.DOT, "."),
            Token(TokenType.NAME, "key"),
            Token(TokenType.VARIABLE_END, "}}"),
            Token(TokenType.DATA, "</html>"),
        ]
        actual = tmpl.parse(tokens)
        self.assertIsInstance(actual[0], RootNode)
        self.assertIsInstance(actual[1], DataNode)
        self.assertIsInstance(actual[2], SkipNode)
        self.assertIsInstance(actual[3], GetNode)
        self.assertIsInstance(actual[4], SkipNode)
        self.assertIsInstance(actual[5], DataNode)

    def test_parse__calculate(self):
        tmpl = Template("")

        tokens = [
            Token(TokenType.VARIABLE_BEGIN, "{{"),
            Token(TokenType.INTEGER, "1"),
            Token(TokenType.ADD, "+"),
            Token(TokenType.INTEGER, "2"),
            Token(TokenType.VARIABLE_END, "}}"),
        ]
        actual = tmpl.parse(tokens)
        self.assertIsInstance(actual[0], RootNode)
        self.assertIsInstance(actual[1], SkipNode)
        self.assertIsInstance(actual[2], CalcNode)

        self.assertEqual(actual[2].op, "+")
        self.assertIsInstance(actual[2].left, ConstNode)
        self.assertIsInstance(actual[2].right, ConstNode)

    def test_parse__calculate_with_more_values(self):
        tmpl = Template("")

        tokens = [
            Token(TokenType.VARIABLE_BEGIN, "{{"),
            Token(TokenType.INTEGER, "1"),
            Token(TokenType.ADD, "+"),
            Token(TokenType.INTEGER, "2"),
            Token(TokenType.SUB, "-"),
            Token(TokenType.INTEGER, "3"),
            Token(TokenType.VARIABLE_END, "}}"),
        ]
        actual = tmpl.parse(tokens)
        self.assertIsInstance(actual[0], RootNode)
        self.assertIsInstance(actual[1], SkipNode)
        self.assertIsInstance(actual[2], CalcNode)

        self.assertEqual(actual[2].op, "-")
        self.assertIsInstance(actual[2].left, CalcNode)
        self.assertIsInstance(actual[2].right, ConstNode)

        self.assertEqual(actual[2].left.op, "+")
        self.assertIsInstance(actual[2].left.left, ConstNode)
        self.assertIsInstance(actual[2].left.right, ConstNode)
