"""
Review 1 demonstration script - Member 3 (data-flow analysis + rule engine).

Run from the repository root:

    python scratch/demo_review1.py

Four sections, in the order they are worth presenting:

  1. Validation set    - detection rate over the seeded test corpus
  2. Full report       - the security report for a multi-vulnerability file
  3. Data-flow tables  - evidence the analysis runs to a fixed point
  4. The contrast      - what the symbol table alone gets wrong
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.rules.engine import RuleEngine, summarize          # noqa: E402
from src.lexer.lexer import Lexer                           # noqa: E402
from src.parser.parser import Parser                        # noqa: E402
from src.analysis.semantic_analyzer import SemanticAnalyzer  # noqa: E402
from src.rules.context import AnalysisContext               # noqa: E402
from src.dataflow.expr_utils import stmt_uses               # noqa: E402

FIXTURES = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures")


def rule(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def read(name):
    with open(os.path.join(FIXTURES, name), encoding="utf-8") as handle:
        return handle.read()


# ---------------------------------------------------------------
# 1. VALIDATION SET
# ---------------------------------------------------------------

def section_validation():
    rule("1. VALIDATION SET - detection across the seeded test corpus")

    files = sorted(f for f in os.listdir(FIXTURES) if f.endswith(".c"))

    total_findings = 0
    clean_files = 0
    false_positives = 0

    print(f"{'File':<28}{'Parsed':<9}{'Findings':<10}Categories")
    print("-" * 78)

    for name in files:
        result = RuleEngine().analyze_source(read(name))

        if not result["ok"]:
            print(f"{name:<28}{'NO':<9}{'-':<10}{result['error']}")
            continue

        findings = result["findings"]
        categories = sorted({f.rule_id for f in findings})

        total_findings += len(findings)

        if name in ("clean.c", "loops.c"):
            clean_files += 1
            false_positives += len(findings)

        print(f"{name:<28}{'yes':<9}{len(findings):<10}"
              f"{', '.join(categories) if categories else '(none)'}")

    print("-" * 78)
    print(f"{total_findings} findings across {len(files)} files.")
    print(f"{false_positives} false positive(s) on {clean_files} clean file(s).")


# ---------------------------------------------------------------
# 2. FULL REPORT
# ---------------------------------------------------------------

def section_report(name="combined.c"):
    rule(f"2. SECURITY REPORT - {name}")

    source = read(name)
    result = RuleEngine().analyze_source(source)
    findings = result["findings"]

    lines = source.splitlines()

    for finding in findings:
        snippet = ""
        if 0 < finding.line <= len(lines):
            snippet = lines[finding.line - 1].strip()

        print()
        print(f"  [{finding.severity}] line {finding.line} - {finding.type}")
        if finding.function:
            print(f"    in function : {finding.function}()")
        if snippet:
            print(f"    source      : {snippet}")
        print(f"    problem     : {finding.message}")
        print(f"    fix         : {finding.suggested_fix}")

    print()
    print(f"  Summary: {summarize(findings)}")


# ---------------------------------------------------------------
# 3. DATA-FLOW TABLES
# ---------------------------------------------------------------

def context_for(source):
    ast = Parser(Lexer(source).tokenize()).parse()
    analyzer = SemanticAnalyzer()
    symbol_table = analyzer.analyze(ast)
    return AnalysisContext(ast, symbol_table), symbol_table


def section_dataflow(name="uninitialized_variable.c", function="compute"):
    rule(f"3. DATA-FLOW ANALYSIS - {function}() in {name}")

    ctx, _ = context_for(read(name))

    print()
    print("Control-flow graph")
    print("-" * 78)
    cfg = ctx.cfgs[function]
    for node_id in sorted(cfg.nodes):
        label = cfg.nodes[node_id].get("label", "")
        successors = [
            f"{succ}({cfg.edges[node_id, succ].get('edge_type')})"
            for succ in cfg.successors(node_id)
        ]
        print(f"  {node_id:<4}{label:<18}-> {', '.join(successors) or '(exit)'}")

    print()
    print("Reaching definitions  (forward 'may' analysis, union at joins)")
    print("-" * 78)
    print(ctx.reaching_defs(function).format_table())

    print()
    print("Definite assignment  (forward 'must' analysis, intersection at joins)")
    print("-" * 78)
    print(ctx.definite_assignment(function).format_table())


# ---------------------------------------------------------------
# 4. THE CONTRAST
# ---------------------------------------------------------------

def section_contrast(name="uninitialized_variable.c", function="compute"):
    rule("4. WHY DATA-FLOW AND NOT JUST THE SYMBOL TABLE")

    source = read(name)
    ctx, symbol_table = context_for(source)

    print()
    print("The symbol table's view (flow-insensitive - one flag per variable):")
    print("-" * 78)
    print(f"  {'Variable':<12}{'Type':<10}{'Declared':<11}is_initialized")
    for symbol in symbol_table.get_all_symbols():
        print(f"  {symbol.name:<12}{symbol.type:<10}"
              f"line {symbol.line_declared:<6}{symbol.is_initialized}")

    print()
    print("  'total' is assigned ONLY inside the if-branch, yet the flag reads")
    print("  True. mark_initialized() is called once and never reset, so it")
    print("  means 'assigned somewhere', not 'assigned on every path'.")

    analysis = ctx.definite_assignment(function)
    cfg = ctx.cfgs[function]

    use_node = None
    for node_id in sorted(cfg.nodes):
        for stmt in cfg.nodes[node_id].get("statements") or []:
            if "total" in {name for name, _line in stmt_uses(stmt)}:
                use_node = node_id
                break
        if use_node is not None:
            break

    print()
    print("The data-flow view (path-sensitive):")
    print("-" * 78)
    print(f"  At CFG node {use_node}, ASSIGNED_IN = "
          f"{sorted(analysis.IN[use_node])}")
    print(f"  'total' definitely assigned here? "
          f"{analysis.is_assigned(use_node, 'total')}")

    print()
    print("Resulting finding:")
    print("-" * 78)
    for finding in RuleEngine().analyze_source(source)["findings"]:
        print(f"  {finding}")


SECTIONS = {
    "1": section_validation,
    "2": section_report,
    "3": section_dataflow,
    "4": section_contrast,
}


def main():
    """
    Run every section, or just one:

        python scratch/demo_review1.py       # all four
        python scratch/demo_review1.py 2     # only the security report

    Running one section at a time keeps each screenshot to a single screen.
    """
    choice = sys.argv[1] if len(sys.argv) > 1 else None

    if choice is None:
        for section in SECTIONS.values():
            section()
    elif choice in SECTIONS:
        SECTIONS[choice]()
    else:
        print(f"Unknown section {choice!r}. Choose one of: "
              f"{', '.join(sorted(SECTIONS))}")
        return 1

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
