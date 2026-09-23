# AST and Parser Implementation Plan

## Goal Description
Create a full abstract syntax tree (AST) representation and a recursive‑descent parser for the C‑subset grammar defined in `docs/grammar.md`. The parser will consume the token list produced by `src/lexer/lexer.py` and output a `ProgramNode` tree composed of dataclasses defined in `src/parser/ast_nodes.py`.

## User Review Required
[!IMPORTANT] The parser implementation will be sizable and touches many grammar rules. Please confirm that the following design decisions are acceptable:
- Use dataclasses with a `line` attribute for source location.
- Implement a `Parser` that stores the token list and a current index, advancing with helper methods `peek`, `advance`, and `expect`.
- Disambiguate `*` and `&` as unary operators when they appear where an operand is expected (i.e., after another operator or at the start of an expression).
- Raise `ParserError` exceptions that include `line`, `column`, and an explanatory message.
- The `parse()` entry point returns a `ProgramNode`.
- Tests will be written in `src/parser/test_parser.py` and will print the AST using `repr` for readability.

## Open Questions
- Should the AST node `LiteralNode.literal_type` be a string (e.g., "int", "float", "string") or an enum? We will use a simple string for now.
- Do you want additional helper methods (e.g., `parse_type`) exposed publicly, or kept internal? We'll keep them private (prefixed with `_`).

## Proposed Changes
---
### src/parser/ast_nodes.py
- Add `from __future__ import annotations` for forward references.
- Import `dataclass` and `field`.
- Define all node dataclasses listed in the request, each with a `line: int` field and appropriate type annotations.
- Include a base class `ASTNode` (optional) for common behaviour.

---
### src/parser/parser.py
- Define `ParserError` exception.
- Define `Parser` class with:
  - `__init__(self, tokens: List[Token])` storing tokens, index, and current token.
  - Helper methods `_peek()`, `_advance()`, `_expect(type, value=None)`.
  - Parsing methods for each grammar rule (as requested) implementing precedence climbing for expressions.
  - Logic for pointer (`*`) and address‑of (`&`) unary handling based on previous token context.
  - `parse()` method that calls `parse_program` and ensures EOF.
- Each parsing method constructs the appropriate AST node, passing the starting token's line number.

---
### src/parser/test_parser.py
- Import `Lexer` and `Parser`.
- Define helper `parse_source(src)` that runs the lexer and parser.
- Six test cases covering:
  1. Variable declaration.
  2. Function with `if/else`.
  3. `while` loop.
  4. `for` loop.
  5. Array declaration and access.
  6. Malformed input triggering `ParserError`.
- Each valid test prints the resulting AST (using `repr`).

---
### docs/ast_schema.md
- Replace the placeholder content with a table or list enumerating each node type and its fields (including `line`).

## Verification Plan
### Automated Tests
- Run `python -m unittest src.parser.test_parser` after implementation.
- Ensure all six tests pass and the malformed input raises `ParserError` with a clear message.

### Manual Verification
- Inspect printed AST structures for readability.
- Spot‑check line numbers correspond to source locations.

---
*Implementation will be done in separate steps, editing only files under `src/parser/` and updating `docs/ast_schema.md`.*
