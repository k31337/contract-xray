"""Rule/heuristic engine for detecting scam and honeypot patterns."""

from contract_xray.rules.base import Finding, Rule, Severity
from contract_xray.rules.excessive_sell_tax import ExcessiveSellTaxRule
from contract_xray.rules.hidden_blacklist import HiddenBlacklistRule
from contract_xray.rules.unrenounced_ownership import UnrenouncedOwnershipRule
from contract_xray.rules.unrestricted_mint import UnrestrictedMintRule

ALL_RULES: list[Rule] = [
    UnrenouncedOwnershipRule(),
    HiddenBlacklistRule(),
    UnrestrictedMintRule(),
    ExcessiveSellTaxRule(),
]

__all__ = ["Finding", "Rule", "Severity", "ALL_RULES"]
