import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.analysis.cfg_builder import CFGBuilder

source = """
int foo(int a) {
    while (a < 5) {
        if (a > 2) {
            while (a < 10) {
                a = a + 1;
            }
        }
    }
    return a;
}
"""

try:
    lexer = Lexer(source)
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    func_node = ast.declarations[0]

    builder = CFGBuilder()
    cfg = builder.build(func_node)

    print("No exception raised — CFG built successfully.\n")

    print("Nodes:")
    for node_id, data in cfg.nodes(data=True):
        print(f"  {node_id}: {data.get('label')}")

    print("\nEdges:")
    for u, v, data in cfg.edges(data=True):
        print(f"  {u} -> {v} (type: {data.get('edge_type')})")

except Exception as e:
    print(f"EXCEPTION: {type(e).__name__}: {e}")
