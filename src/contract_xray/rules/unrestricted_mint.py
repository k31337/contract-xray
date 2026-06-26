"""Rule: detect mint functions that are not properly access-controlled."""

from __future__ import annotations

from typing import TYPE_CHECKING

from contract_xray.rules.base import Finding, Rule, Severity

if TYPE_CHECKING:
    from slither import Slither

MINT_FUNCTION_FRAGMENTS = ("mint",)
ACCESS_CONTROL_MODIFIER_FRAGMENTS = ("onlyowner", "onlyrole", "onlyminter", "onlyadmin", "onlygovernance")


class UnrestrictedMintRule(Rule):
    """Flags mint functions that lack a recognizable access-control modifier.

    A mint function without restriction lets anyone inflate the token
    supply; even when restricted to the owner, an unbounded mint is still a
    centralization risk worth surfacing.
    """

    rule_id = "unrestricted-mint"
    title = "Unrestricted or uncontrolled mint function"
    default_severity = Severity.HIGH

    def evaluate(self, slither: Slither) -> list[Finding]:
        findings: list[Finding] = []

        for contract in slither.contracts:
            mint_functions = [
                function
                for function in contract.functions
                if function.name
                and any(fragment in function.name.lower() for fragment in MINT_FUNCTION_FRAGMENTS)
                and not function.view
                and not function.pure
                and not function.is_constructor
            ]

            for function in mint_functions:
                modifier_names = {modifier.name.lower() for modifier in function.modifiers}
                is_access_controlled = bool(modifier_names & set(ACCESS_CONTROL_MODIFIER_FRAGMENTS))

                if is_access_controlled:
                    continue

                findings.append(
                    Finding(
                        rule_id=self.rule_id,
                        title=self.title,
                        description=(
                            f"Function '{function.name}' in contract '{contract.name}' can mint new tokens "
                            "without a recognizable access-control modifier (e.g. onlyOwner). "
                            "This may allow unrestricted supply inflation."
                        ),
                        severity=self.default_severity,
                        contract_name=contract.name,
                    )
                )

        return findings
