"""Rule/heuristic engine for detecting scam and honeypot patterns."""

from contract_xray.rules.base import Finding, Rule, Severity
from contract_xray.rules.hidden_blacklist import HiddenBlacklistRule
from contract_xray.rules.unrenounced_ownership import UnrenouncedOwnershipRule

ALL_RULES: list[Rule] = [
    UnrenouncedOwnershipRule(),
    HiddenBlacklistRule(),
]

__all__ = ["Finding", "Rule", "Severity", "ALL_RULES"]
