import unittest
from .lexer import Lexer, LexerError
from .tokens import TokenType

class TestLexer(unittest.TestCase):
    def test_simple_declaration(self):
        source = "int x = 42;"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 6) # int, x, =, 42, ;, EOF
        
        self.assertEqual(tokens[0].type, TokenType.KEYWORD)
        self.assertEqual(tokens[0].value, "int")
        
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].value, "x")
        
        self.assertEqual(tokens[2].type, TokenType.OPERATOR)
        self.assertEqual(tokens[2].value, "=")
        
        self.assertEqual(tokens[3].type, TokenType.INT_LITERAL)
        self.assertEqual(tokens[3].value, "42")
        
        self.assertEqual(tokens[4].type, TokenType.PUNCTUATION)
        self.assertEqual(tokens[4].value, ";")

    def test_if_else_block(self):
        source = """
        if (x == 10) {
            return x;
        } else {
            return 0;
        }
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        types = [t.type for t in tokens]
        values = [t.value for t in tokens]
        
        self.assertIn("if", values)
        self.assertIn("else", values)
        self.assertIn("return", values)
        self.assertIn("==", values)
        self.assertIn("{", values)
        self.assertIn("}", values)
        self.assertEqual(tokens[-1].type, TokenType.EOF)

    def test_function_call(self):
        source = "print(x, 3.14);"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        self.assertEqual(tokens[0].value, "print")
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        
        self.assertEqual(tokens[1].value, "(")
        self.assertEqual(tokens[1].type, TokenType.PUNCTUATION)
        
        self.assertEqual(tokens[3].value, ",")
        self.assertEqual(tokens[3].type, TokenType.PUNCTUATION)
        
        self.assertEqual(tokens[4].value, "3.14")
        self.assertEqual(tokens[4].type, TokenType.FLOAT_LITERAL)

    def test_string_literal(self):
        source = 'char* s = "hello world";'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        self.assertEqual(tokens[0].value, "char")
        self.assertEqual(tokens[1].value, "*")
        self.assertEqual(tokens[1].type, TokenType.OPERATOR)
        
        string_token = next(t for t in tokens if t.type == TokenType.STRING_LITERAL)
        self.assertEqual(string_token.value, "hello world")
        self.assertEqual(string_token.line, 1)

    def test_invalid_character(self):
        source = "int x = 42; @invalid"
        lexer = Lexer(source)
        
        with self.assertRaises(LexerError) as context:
            lexer.tokenize()
            
        self.assertIn("Unrecognized character '@'", str(context.exception))
        self.assertEqual(context.exception.line, 1)
        self.assertEqual(context.exception.column, 13)

if __name__ == '__main__':
    unittest.main()
