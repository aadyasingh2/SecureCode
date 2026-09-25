"""
The vulnerability report record.

This module defines the single data structure every security rule emits and
that the GUI consumes. The fields map directly onto the four items the project
proposal requires in the security report: vulnerability type, source-code
location, severity, and recommended corrective action.
"""

from dataclasses import dataclass
from typing import Optional


class Severity:
    """Severity levels, ordered most to least serious."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

    # Used to sort findings so the worst issues surface first.
    RANK = {HIGH: 0, MEDIUM: 1, LOW: 2}

    @classmethod
    def rank(cls, severity: str) -> int:
        return cls.RANK.get(severity, 99)


@dataclass
class Finding:
    """One detected vulnerability."""

    rule_id: str          # Stable machine name, e.g. "DANGEROUS_FUNC"
    type: str             # Human-readable category, e.g. "Dangerous Function Usage"
    line: int             # Source line where the issue occurs
    severity: str         # One of Severity.HIGH / MEDIUM / LOW
    message: str          # What is wrong
    suggested_fix: str    # Recommended corrective action
    function: Optional[str] = None   # Enclosing function, when known

    def to_dict(self) -> dict:
        """
        Serialise to the dict shape the GUI renders.

        This is the agreed integration contract with Member 4 - the keys here
        are the columns of the vulnerability report table.
        """
        return {
            "rule_id": self.rule_id,
            "type": self.type,
            "line": self.line,
            "severity": self.severity,
            "message": self.message,
            "suggested_fix": self.suggested_fix,
            "function": self.function,
        }

    def sort_key(self):
        """Order findings by line, then by severity, then by rule."""
        return (self.line, Severity.rank(self.severity), self.rule_id)

    def __str__(self) -> str:
        where = f" in {self.function}()" if self.function else ""
        return f"[{self.severity}] line {self.line}{where}: {self.type} - {self.message}"
