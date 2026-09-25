"""
Rule: use of C library functions that are unsafe by construction.

Pure AST pattern matching - no data-flow needed. Every FuncCallNode anywhere
in the program is matched against a blocklist.
"""

from src.rules.base import Rule
from src.rules.finding import Finding, Severity
from src.parser.ast_nodes import FuncCallNode
from src.dataflow.expr_utils import find_all


# name -> (severity, why it is dangerous, recommended fix)
BLOCKLIST = {
    "gets": (
        Severity.HIGH,
        "gets() performs no bounds checking and will overflow the destination "
        "buffer on any input longer than the buffer",
        "Use fgets(buf, sizeof(buf), stdin), which takes an explicit size.",
    ),
    "strcpy": (
        Severity.HIGH,
        "strcpy() copies until a null terminator with no regard for the size "
        "of the destination buffer",
        "Use strncpy(dst, src, sizeof(dst) - 1) and null-terminate manually, "
        "or snprintf().",
    ),
    "strcat": (
        Severity.HIGH,
        "strcat() appends without checking the remaining space in the "
        "destination buffer",
        "Use strncat(dst, src, sizeof(dst) - strlen(dst) - 1).",
    ),
    "sprintf": (
        Severity.HIGH,
        "sprintf() writes a formatted string with no output size limit",
        "Use snprintf(buf, sizeof(buf), ...).",
    ),
    "vsprintf": (
        Severity.HIGH,
        "vsprintf() writes a formatted string with no output size limit",
        "Use vsnprintf(buf, sizeof(buf), ...).",
    ),
    "system": (
        Severity.HIGH,
        "system() passes its argument to a shell, so any attacker-controlled "
        "part of the string becomes command injection",
        "Use execve() with an argument vector, and validate all inputs.",
    ),
    "popen": (
        Severity.HIGH,
        "popen() runs its argument through a shell, allowing command injection",
        "Use pipe() with execve(), and validate all inputs.",
    ),
    "scanf": (
        Severity.MEDIUM,
        "scanf() with an unbounded %s conversion overflows the destination "
        "buffer",
        "Specify a maximum field width such as %31s, or read with fgets().",
    ),
    "memcpy": (
        Severity.MEDIUM,
        "memcpy() copies a caller-supplied length with no bounds check; an "
        "attacker-controlled length overflows the destination",
        "Validate that the length does not exceed the destination size.",
    ),
    "alloca": (
        Severity.MEDIUM,
        "alloca() allocates on the stack and has no failure mode, so a large "
        "or attacker-controlled size smashes the stack",
        "Use malloc() and check the returned pointer.",
    ),
    "strncpy": (
        Severity.LOW,
        "strncpy() does not null-terminate when the source is at least as "
        "long as the given size",
        "Null-terminate explicitly, or prefer snprintf().",
    ),
    "rand": (
        Severity.LOW,
        "rand() is not cryptographically secure and is predictable from its "
        "seed",
        "Use a CSPRNG such as getrandom() or arc4random() for security uses.",
    ),
}


class DangerousFunctionRule(Rule):

    rule_id = "DANGEROUS_FUNC"
    name = "Dangerous Function Usage"

    def run(self, ctx):
        findings = []

        for func_name, func_node in ctx.functions.items():
            for call in find_all(func_node, FuncCallNode):
                entry = BLOCKLIST.get(call.name)

                if entry is None:
                    continue

                severity, why, fix = entry

                findings.append(Finding(
                    rule_id=self.rule_id,
                    type=self.name,
                    line=call.line,
                    severity=severity,
                    message=f"Call to unsafe function '{call.name}()' - {why}.",
                    suggested_fix=fix,
                    function=func_name,
                ))

        return findings
