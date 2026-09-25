"""
Rule: dereferencing a pointer that may hold null.

This rule consumes the *reaching-definitions* solution rather than definite
assignment: the question is "which assignment could this pointer's value have
come from", and if any of those assignments stores null on some path, the
dereference is unsafe. That is a "may" question, which is exactly what
reaching definitions answers.

Grammar limitation
------------------
`docs/grammar.md` defines an assignment target as
`IDENTIFIER ('[' expr ']')? '=' expr`, so `*p = 5;` does not parse in this C
subset. This rule therefore covers dereferences that *read*: `x = *p;` and
`p[i]`. Writes through a pointer cannot be analysed until the grammar supports
them, and that is stated rather than silently ignored.
"""

from src.rules.base import Rule
from src.rules.finding import Finding, Severity
from src.parser.ast_nodes import (
    UnaryOpNode,
    IdentifierNode,
    ArrayAccessNode,
    LiteralNode,
    VarDeclNode,
    AssignNode,
)


def _is_null(expr):
    """True if an expression is a null pointer constant."""
    if isinstance(expr, LiteralNode):
        return expr.literal_type == "int" and expr.value.strip() == "0"

    # The C subset has no preprocessor, so NULL is not normally available,
    # but accept it if a program declares it.
    if isinstance(expr, IdentifierNode):
        return expr.name == "NULL"

    return False


def _assigned_expr(cfg, definition):
    """Recover the expression a Definition assigned, if we can see it."""
    data = cfg.nodes.get(definition.node_id)
    if data is None:
        return None

    for stmt in data.get("statements") or []:
        if isinstance(stmt, VarDeclNode) and stmt.name == definition.var:
            return stmt.init_expr
        if (isinstance(stmt, AssignNode)
                and stmt.target_name == definition.var
                and stmt.index_expr is None):
            return stmt.value_expr

    return None


class NullDereferenceRule(Rule):

    rule_id = "NULL_DEREFERENCE"
    name = "Null Pointer Dereference"
    uses_dataflow = True

    def run(self, ctx):
        findings = []

        for func_name in ctx.functions:
            findings.extend(self._run_function(ctx, func_name))

        return findings

    def _run_function(self, ctx, func_name):
        findings = []

        cfg = ctx.cfgs[func_name]
        reaching = ctx.reaching_defs(func_name)
        reported = set()

        for node_id in sorted(cfg.nodes):
            for stmt in cfg.nodes[node_id].get("statements") or []:
                for name, line in self._dereferenced(stmt):

                    if (name, line) in reported:
                        continue

                    null_lines = self._null_definitions(
                        cfg, reaching, node_id, name)

                    if not null_lines:
                        continue

                    reported.add((name, line))

                    origins = ", ".join(str(n) for n in sorted(null_lines))

                    findings.append(Finding(
                        rule_id=self.rule_id,
                        type=self.name,
                        line=line,
                        severity=Severity.HIGH,
                        message=(
                            f"Pointer '{name}' is dereferenced here, but on at "
                            f"least one path reaching this point it was set to "
                            f"null (assigned at line {origins}). Dereferencing "
                            f"null crashes the program."
                        ),
                        suggested_fix=(
                            f"Check `if ({name} != 0)` before dereferencing "
                            f"'{name}', or ensure it is assigned a valid "
                            f"address on every path."
                        ),
                        function=func_name,
                    ))

        return findings

    def _dereferenced(self, stmt):
        """Yield (pointer_name, line) for each pointer read through."""
        from src.dataflow.expr_utils import walk

        for node in walk(stmt):
            if (isinstance(node, UnaryOpNode)
                    and node.op == "*"
                    and isinstance(node.operand, IdentifierNode)):
                yield node.operand.name, node.line

            elif isinstance(node, ArrayAccessNode):
                # p[i] dereferences p just as *(p + i) does.
                yield node.name, node.line

    def _null_definitions(self, cfg, reaching, node_id, name):
        """Lines of the reaching definitions of `name` that assign null."""
        lines = set()

        for definition in reaching.reaching(node_id, name):
            expr = _assigned_expr(cfg, definition)
            if expr is not None and _is_null(expr):
                lines.add(definition.line)

        return lines
