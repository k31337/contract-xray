"""Rule: detect hidden blacklist mechanisms that can block addresses from transferring."""

from __future__ import annotations

from typing import TYPE_CHECKING

from contract_xray.rules.base import Finding, Rule, Severity

if TYPE_CHECKING:
    from slither import Slither

BLACKLIST_NAME_FRAGMENTS = ("blacklist", "blocked", "isblocked", "isexcluded", "isbanned")


class HiddenBlacklistRule(Rule):
    """Flags contracts that can prevent specific addresses from transferring tokens.

    A mapping-based blacklist controlled by a privileged function lets the
    contract owner silently block holders from selling or transferring,
    which is a common honeypot mechanism.
    """

    rule_id = "hidden-blacklist"
    title = "Hidden blacklist mechanism"
    default_severity = Severity.HIGH

    def evaluate(self, slither: Slither) -> list[Finding]:
        findings: list[Finding] = []

        for contract in slither.contracts:
            blacklist_variables = [
                variable
                for variable in contract.state_variables
                if variable.name and self._matches_blacklist_name(variable.name)
            ]
            if not blacklist_variables:
                continue

            setter_functions = [
                function
                for function in contract.functions
                if function.name and self._matches_blacklist_name(function.name) and not function.view and not function.pure
            ]

            variable_names = ", ".join(variable.name for variable in blacklist_variables)
            findings.append(
                Finding(
                    rule_id=self.rule_id,
                    title=self.title,
                    description=(
                        f"Contract '{contract.name}' defines blacklist-like state ({variable_names}) "
                        + (
                            f"with {len(setter_functions)} function(s) able to modify it. "
                            if setter_functions
                            else "but no obvious setter was found; manual review recommended. "
                        )
                        + "This can be used to block specific addresses from transferring or selling."
                    ),
                    severity=self.default_severity,
                    contract_name=contract.name,
                )
            )

        return findings

    @staticmethod
    def _matches_blacklist_name(name: str) -> bool:
        lowered = name.lower()
        return any(fragment in lowered for fragment in BLACKLIST_NAME_FRAGMENTS)
