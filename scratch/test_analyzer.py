import sys
import os

# Add root project dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.analysis.semantic_analyzer import SemanticAnalyzer

source = "int arr[3] = {1, 2, 3, 4};"
lexer = Lexer(source)
parser = Parser(lexer.tokenize())
ast = parser.parse()

analyzer = SemanticAnalyzer()
analyzer.analyze(ast)

errors = analyzer.get_errors()
for error in errors:
    print(error)
