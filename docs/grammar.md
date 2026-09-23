# Grammar Specification

This document contains the formal BNF grammar for the language.

### Declarations
Rules defining the structure of programs, variables, types, and function definitions.
```bnf
program         → (func_def | decl)*
type            → ('int' | 'char' | 'float') '*'*
decl            → type IDENTIFIER ('[' INT_LIT ']')? ('=' expr)? ';'
func_def        → type IDENTIFIER '(' params? ')' block
params          → param (',' param)*
param           → type IDENTIFIER
```

### Statements
Rules outlining blocks, control flow, assignments, and execution statements.
```bnf
block           → '{' stmt* '}'
stmt            → decl
                | assign_stmt
                | if_stmt
                | while_stmt
                | for_stmt
                | return_stmt
                | expr_stmt
                | block
assign_stmt     → IDENTIFIER ('[' expr ']')? '=' expr ';'
if_stmt         → 'if' '(' expr ')' block ('else' (if_stmt | block))?
while_stmt      → 'while' '(' expr ')' block
for_stmt        → 'for' '(' (assign_stmt | decl) expr ';' assign_expr ')' block
return_stmt     → 'return' expr? ';'
expr_stmt       → func_call ';'
```

### Expressions
Rules determining the precedence, associativity, and structure of expressions.
```bnf
expr            → logic_or
logic_or        → logic_and ('||' logic_and)*
logic_and       → equality ('&&' equality)*
equality        → comparison (('==' | '!=') comparison)*
comparison      → term (('<' | '>' | '<=' | '>=') term)*
term            → factor (('+' | '-') factor)*
factor          → unary (('*' | '/' | '%') unary)*
unary           → ('!' | '-' | '*' | '&') unary
                | primary
primary         → INT_LIT
                | FLOAT_LIT
                | STRING_LIT
                | IDENTIFIER ('[' expr ']')?
                | func_call
                | '(' expr ')'
func_call       → IDENTIFIER '(' args? ')'
args            → expr (',' expr)*
assign_expr     → IDENTIFIER '=' expr
```
