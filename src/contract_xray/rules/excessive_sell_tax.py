"""Rule: detect disproportionate or owner-adjustable sell tax/fee."""

from __future__ import annotations

from typing import TYPE_CHECKING

from contract_xray.rules.base import Finding, Rule, Severity

if TYPE_CHECKING:
    from slither import Slither

TAX_VARIABLE_FRAGMENTS = ("selltax", "sellfee", "taxfee", "feepercent", "taxpercent")
MAX_REASONABLE_TAX_PERCENT = 25
SETTER_PREFIX_FRAGMENTS = ("set", "update")
SETTER_TARGET_FRAGMENTS = ("tax", "fee")


class ExcessiveSellTaxRule(Rule):
    """Flags sell tax/fee values that are disproportionate or owner-adjustable.

    Static analysis cannot evaluate the live value of a tax variable
    reliably in all cases, so this rule flags both: tax-like constants above
    a reasonable threshold, and the presence of an owner-only setter that
    can change the tax after deployment (allowing a bait-and-switch).
    """

    rule_id = "excessive-sell-tax"
    title = "Disproportionate or adjustable sell tax"
    default_severity = Severity.HIGH

    def evaluate(self, slither: Slither) -> list[Finding]:
        findings: list[Finding] = []

        for contract in slither.contracts:
            tax_variables = [
                variable
                for variable in contract.state_variables
                if variable.name and self._matches_tax_name(variable.name)
            ]
            if not tax_variables:
                continue

            high_constant_taxes = [
                variable
                for variable in tax_variables
                if variable.expression is not None
                and self._exceeds_threshold(str(variable.expression))
            ]

            tax_setters = [
                function
                for function in contract.functions
                if function.name and self._is_tax_setter(function.name)
            ]

            if not high_constant_taxes and not tax_setters:
                continue

            details = []
            if high_constant_taxes:
                names = ", ".join(variable.name for variable in high_constant_taxes)
                details.append(f"tax variable(s) above {MAX_REASONABLE_TAX_PERCENT}%: {names}")
            if tax_setters:
                names = ", ".join(function.name for function in tax_setters)
                details.append(f"tax can be changed after deployment via: {names}")

            findings.append(
                Finding(
                    rule_id=self.rule_id,
                    title=self.title,
                    description=(
                        f"Contract '{contract.name}' has a sell tax/fee mechanism that is risky "
                        f"({'; '.join(details)}). This can be used to trap sellers with high fees."
                    ),
                    severity=self.default_severity,
                    contract_name=contract.name,
                )
            )

        return findings

    @staticmethod
    def _matches_tax_name(name: str) -> bool:
        lowered = name.lower()
        return any(fragment in lowered for fragment in TAX_VARIABLE_FRAGMENTS)

    @staticmethod
    def _is_tax_setter(name: str) -> bool:
        lowered = name.lower()
        has_prefix = any(lowered.startswith(prefix) for prefix in SETTER_PREFIX_FRAGMENTS)
        has_target = any(fragment in lowered for fragment in SETTER_TARGET_FRAGMENTS)
        return has_prefix and has_target

    @staticmethod
    def _exceeds_threshold(expression: str) -> bool:
        digits = "".join(character for character in expression if character.isdigit())
        if not digits:
            return False
        return int(digits) > MAX_REASONABLE_TAX_PERCENT
