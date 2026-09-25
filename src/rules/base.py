"""Common base class for security rules."""


class Rule:
    """
    A security rule.

    Rules are independent: each reads an AnalysisContext and returns a list of
    Finding objects. Keeping them separate means one broken rule can be
    disabled without taking the whole engine down.
    """

    rule_id = "RULE"
    name = "Rule"
    uses_dataflow = False

    def run(self, ctx):
        raise NotImplementedError
