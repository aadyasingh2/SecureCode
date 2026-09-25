"""
Rule: statements that no execution path can reach.

This is a pure control-flow property, so it is answered directly from the CFG:
any node other than ENTRY with no incoming edge cannot be reached.

`CFGBuilder.build_statement()` returns an empty continuation list for a
ReturnNode, so the statement following a `return` is never wired to a
predecessor and shows up here exactly as it should. Only the *first* statement
of an unreachable region has in-degree zero - the ones after it are reachable
from it - so each dead region yields a single finding rather than one per line.
"""

from src.rules.base import Rule
from src.rules.finding import Finding, Severity
from src.dataflow.expr_utils import line_of


class UnreachableCodeRule(Rule):

    rule_id = "UNREACHABLE_CODE"
    name = "Unreachable Code"

    def run(self, ctx):
        findings = []

        for func_name, cfg in ctx.cfgs.items():
            entry = cfg.graph.get("entry")

            for node_id in sorted(cfg.nodes):
                if node_id == entry:
                    continue

                if cfg.in_degree(node_id) != 0:
                    continue

                statements = cfg.nodes[node_id].get("statements") or []
                if not statements:
                    # Structural nodes (EXIT, IF MERGE) carry no source line.
                    continue

                line = line_of(statements[0])

                findings.append(Finding(
                    rule_id=self.rule_id,
                    type=self.name,
                    line=line,
                    severity=Severity.LOW,
                    message=(
                        "This statement is unreachable: no path through the "
                        "control-flow graph arrives here, typically because "
                        "an earlier return or loop ends the flow."
                    ),
                    suggested_fix=(
                        "Remove the dead code, or correct the control flow "
                        "above it if this branch was meant to execute."
                    ),
                    function=func_name,
                ))

        return findings
