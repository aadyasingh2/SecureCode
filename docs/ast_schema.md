# AST Schema Documentation

This document enumerates the fields of each AST node type used by the parser. All nodes include a `line: int` attribute indicating the source line where the node begins.

| Node Type | Fields |
|-----------|--------|
| **ProgramNode** | `declarations: List[ASTNode]`, `line: int` |
| **VarDeclNode** | `var_type: str`, `name: str`, `is_pointer: bool`, `array_size: Optional[int]`, `init_expr: Optional[ASTNode]`, `line: int` |
| **FuncDefNode** | `return_type: str`, `name: str`, `params: List[ParamNode]`, `body: BlockNode`, `line: int` |
| **ParamNode** | `param_type: str`, `name: str`, `is_pointer: bool`, `line: int` |
| **BlockNode** | `statements: List[ASTNode]`, `line: int` |
| **AssignNode** | `target_name: str`, `index_expr: Optional[ASTNode]`, `value_expr: ASTNode`, `line: int` |
| **IfNode** | `condition: ASTNode`, `then_block: BlockNode`, `else_block: Optional[BlockNode]`, `line: int` |
| **WhileNode** | `condition: ASTNode`, `body: BlockNode`, `line: int` |
| **ForNode** | `init: ASTNode` (VarDeclNode or AssignNode), `condition: ASTNode`, `update: ASTNode`, `body: BlockNode`, `line: int` |
| **ReturnNode** | `value: Optional[ASTNode]`, `line: int` |
| **ExprStmtNode** | `expr: ASTNode`, `line: int` |
| **BinOpNode** | `op: str`, `left: ASTNode`, `right: ASTNode`, `line: int` |
| **UnaryOpNode** | `op: str`, `operand: ASTNode`, `line: int` |
| **LiteralNode** | `value: str`, `literal_type: str` ("int", "float", "string"), `line: int` |
| **IdentifierNode** | `name: str`, `line: int` |
| **ArrayAccessNode** | `name: str`, `index_expr: ASTNode`, `line: int` |
| **FuncCallNode** | `name: str`, `args: List[ASTNode]`, `line: int` |

---

Each node corresponds directly to a grammar construct from `docs/grammar.md`. The `line` field helps with error reporting and source‑level diagnostics.
