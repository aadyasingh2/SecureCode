"""
Rule: secrets written directly into the source.

Matches a string literal assigned to an identifier whose name looks like a
credential. Works off the AST alone - no token stream needed, which keeps this
rule independent of the lexer's output format.

Two confidence tiers, because name matching is inherently heuristic:
names like `password` are near-certain, while `token` or `key` occur often
enough in ordinary code to deserve a softer severity.
"""

import re

from src.rules.base import Rule
from src.rules.finding import Finding, Severity
from src.parser.ast_nodes import VarDeclNode, AssignNode, LiteralNode
from src.dataflow.expr_utils import walk, global_decls


STRONG_NAME = re.compile(
    r"(password|passwd|pwd|passphrase|secret|api_?key|private_?key|"
    r"access_?key|credentials?)",
    re.IGNORECASE,
)

WEAK_NAME = re.compile(
    r"(auth|token|session_?key|key|pin|salt)",
    re.IGNORECASE,
)

FIX = (
    "Load this value from an environment variable or a configuration file "
    "kept out of version control, and rotate the exposed secret."
)


def _classify(name):
    """Return a severity for a credential-looking name, or None."""
    if STRONG_NAME.search(name):
        return Severity.HIGH
    if WEAK_NAME.search(name):
        return Severity.MEDIUM
    return None


def _string_literal(expr):
    """Return a non-empty string literal, or None."""
    if isinstance(expr, LiteralNode) and expr.literal_type == "string":
        if expr.value != "":
            return expr
    return None


class HardcodedCredentialRule(Rule):

    rule_id = "HARDCODED_CREDENTIAL"
    name = "Hardcoded Credential"

    def run(self, ctx):
        findings = []

        # Globals first, then each function body. `global_decls` yields only
        # top-level VarDeclNodes, so we do not descend into function bodies
        # here and report their declarations a second time.
        findings.extend(self._scan(global_decls(ctx.ast), function=None))

        for func_name, func_node in ctx.functions.items():
            findings.extend(self._scan([func_node], function=func_name))

        return findings

    def _scan(self, roots, function):
        findings = []

        for root in roots:
            for node in walk(root):

                if isinstance(node, VarDeclNode):
                    name, value = node.name, node.init_expr
                elif isinstance(node, AssignNode):
                    name, value = node.target_name, node.value_expr
                else:
                    continue

                severity = _classify(name)
                if severity is None:
                    continue

                literal = _string_literal(value)
                if literal is None:
                    continue

                findings.append(Finding(
                    rule_id=self.rule_id,
                    type=self.name,
                    line=node.line,
                    severity=severity,
                    message=(
                        f"Variable '{name}' is assigned a hardcoded string "
                        f"literal. Anyone with read access to the source or "
                        f"the compiled binary can recover this value."
                    ),
                    suggested_fix=FIX,
                    function=function,
                ))

        return findings
