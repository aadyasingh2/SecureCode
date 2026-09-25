"""
Reaching-definitions analysis.

A classic forward "may" data-flow analysis solved with a worklist algorithm
until it reaches a fixed point:

    IN[n]  = union of OUT[p] for every predecessor p of n
    OUT[n] = GEN[n] union (IN[n] - KILL[n])

GEN[n] is the definition made by node n. KILL[n] is every *other* definition
of the same variable anywhere in the function - assigning to x invalidates all
previously reaching definitions of x.

"May" means a definition reaches n if it survives along *at least one* path.
That is the right question for "which assignment could this value have come
from", which is what the null-dereference rule asks.

`CFGBuilder` places at most one statement in each CFG node, so GEN and KILL are
computed per statement and no intra-node ordering is required.
"""

from collections import deque
from dataclasses import dataclass

from src.dataflow.expr_utils import stmt_defs


@dataclass(frozen=True)
class Definition:
    """One assignment to a variable, identified by where it happened."""

    var: str
    line: int
    node_id: int

    def __str__(self):
        return f"{self.var}@{self.line}"


class ReachingDefinitions:
    """Solves reaching definitions for a single function's CFG."""

    def __init__(self, cfg, entry_defs=None):
        """
        `entry_defs` are definitions considered live on entry - function
        parameters and initialised globals. Without them, parameters look
        undefined to every rule downstream.
        """
        self.cfg = cfg
        self.entry = cfg.graph.get("entry")
        self.entry_defs = set(entry_defs or ())

        self.gen = {}
        self.kill = {}
        self.IN = {}
        self.OUT = {}
        self.iterations = 0

        self._build_gen_kill()
        self._solve()

    # -----------------------------------------------------------
    # GEN / KILL
    # -----------------------------------------------------------

    def _build_gen_kill(self):
        # Every definition in the function, grouped by variable.
        all_defs = {}

        for node_id in self.cfg.nodes:
            gen = set()

            for stmt in self.cfg.nodes[node_id].get("statements") or []:
                for name, line in stmt_defs(stmt):
                    gen.add(Definition(name, line, node_id))

            if node_id == self.entry:
                gen |= self.entry_defs

            self.gen[node_id] = gen

            for definition in gen:
                all_defs.setdefault(definition.var, set()).add(definition)

        # Killing x means invalidating every other definition of x.
        for node_id in self.cfg.nodes:
            kill = set()
            for definition in self.gen[node_id]:
                kill |= all_defs.get(definition.var, set())
            self.kill[node_id] = kill - self.gen[node_id]

        self.all_defs = all_defs

    # -----------------------------------------------------------
    # FIXED-POINT SOLVER
    # -----------------------------------------------------------

    def _solve(self):
        for node_id in self.cfg.nodes:
            self.IN[node_id] = set()
            self.OUT[node_id] = set(self.gen[node_id])

        worklist = deque(sorted(self.cfg.nodes))
        queued = set(worklist)

        while worklist:
            self.iterations += 1
            node_id = worklist.popleft()
            queued.discard(node_id)

            incoming = set()
            for pred in self.cfg.predecessors(node_id):
                incoming |= self.OUT[pred]
            self.IN[node_id] = incoming

            new_out = self.gen[node_id] | (incoming - self.kill[node_id])

            if new_out != self.OUT[node_id]:
                self.OUT[node_id] = new_out

                # Only successors can be affected by this change.
                for succ in self.cfg.successors(node_id):
                    if succ not in queued:
                        worklist.append(succ)
                        queued.add(succ)

    # -----------------------------------------------------------
    # QUERIES / PRESENTATION
    # -----------------------------------------------------------

    def reaching(self, node_id, var):
        """Definitions of `var` that reach the start of `node_id`."""
        return {d for d in self.IN.get(node_id, set()) if d.var == var}

    def table(self):
        """
        Per-node IN/OUT rows, for display.

        This is the evidence that the analysis actually runs to a fixed point
        rather than pattern-matching, so it is worth showing at the review.
        """
        rows = []
        for node_id in sorted(self.cfg.nodes):
            data = self.cfg.nodes[node_id]
            rows.append({
                "node": node_id,
                "label": data.get("label", ""),
                "gen": sorted(str(d) for d in self.gen[node_id]),
                "kill": sorted(str(d) for d in self.kill[node_id]),
                "in": sorted(str(d) for d in self.IN[node_id]),
                "out": sorted(str(d) for d in self.OUT[node_id]),
            })
        return rows

    def format_table(self):
        """Render `table()` as aligned text."""
        rows = self.table()
        header = (f"{'Node':<6}{'Label':<16}{'GEN':<16}{'KILL':<16}"
                  f"{'IN':<32}OUT")
        lines = [header, "-" * len(header)]

        for row in rows:
            lines.append(
                f"{row['node']:<6}{row['label'][:15]:<16}"
                f"{','.join(row['gen'])[:15]:<16}"
                f"{','.join(row['kill'])[:15]:<16}"
                f"{','.join(row['in'])[:31]:<32}"
                f"{','.join(row['out'])}"
            )

        lines.append(f"\nFixed point reached after {self.iterations} node visits.")
        return "\n".join(lines)
