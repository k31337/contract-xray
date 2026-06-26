"""Base interfaces for the rule/heuristic engine."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from slither import Slither


class Severity(str, Enum):
    """Risk severity assigned to a finding."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Finding:
    """A single red flag detected by a rule."""

    rule_id: str
    title: str
    description: str
    severity: Severity
    contract_name: str


class Rule(ABC):
    """A single heuristic that inspects a Slither analysis for red flags."""

    rule_id: str
    title: str
    default_severity: Severity

    @abstractmethod
    def evaluate(self, slither: Slither) -> list[Finding]:
        """Return the findings produced by this rule for the given analysis."""
