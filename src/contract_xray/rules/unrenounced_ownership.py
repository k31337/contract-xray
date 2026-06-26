"""Rule: detect privileged ownership that has not been verifiably renounced."""

from __future__ import annotations

from slither import Slither

from contract_xray.rules.base import Finding, Rule, Severity

OWNER_VARIABLE_NAMES = {"owner", "_owner"}
RENOUNCE_FUNCTION_NAMES = {"renounceownership"}
TRANSFER_FUNCTION_NAMES = {"transferownership"}


class UnrenouncedOwnershipRule(Rule):
    """Flags contracts with an Ownable-style privileged role.

    Static source analysis cannot confirm the current on-chain value of the
    owner variable, so any contract exposing owner-only privileges is flagged
    for manual verification that ownership has actually been renounced
    (i.e. transferred to the zero address) on-chain.
    """

    rule_id = "unrenounced-ownership"
    title = "Ownership not verifiably renounced"
    default_severity = Severity.MEDIUM

    def evaluate(self, slither: Slither) -> list[Finding]:
        findings: list[Finding] = []

        for contract in slither.contracts:
            has_owner_variable = any(
                variable.name and variable.name.lower() in OWNER_VARIABLE_NAMES
                for variable in contract.state_variables
            )
            function_names = {function.name.lower() for function in contract.functions if function.name}
            has_ownership_functions = bool(function_names & (RENOUNCE_FUNCTION_NAMES | TRANSFER_FUNCTION_NAMES))

            if not (has_owner_variable or has_ownership_functions):
                continue

            findings.append(
                Finding(
                    rule_id=self.rule_id,
                    title=self.title,
                    description=(
                        f"Contract '{contract.name}' exposes owner-only privileges. "
                        "Verify on-chain that ownership has been renounced "
                        "(owner address set to 0x0) before trusting this contract."
                    ),
                    severity=self.default_severity,
                    contract_name=contract.name,
                )
            )

        return findings
