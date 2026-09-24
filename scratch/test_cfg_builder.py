import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.analysis.cfg_builder import CFGBuilder

source = """
int foo(int a) {
    if (a > 0) {
        return 1;
    } else {
        return 0;
    }
}
"""

lexer = Lexer(source)
parser = Parser(lexer.tokenize())
ast = parser.parse()

# Get the FuncDefNode
func_node = ast.declarations[0]

builder = CFGBuilder()
cfg = builder.build(func_node)

print("Nodes:")
for node_id, data in cfg.nodes(data=True):
    print(f"  {node_id}: {data.get('label')}")

print("\nEdges:")
for u, v, data in cfg.edges(data=True):
    print(f"  {u} -> {v} (type: {data.get('edge_type')})")
