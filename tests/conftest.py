"""Shared test doubles that mimic the minimal Slither object shape used by rules."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StubVariable:
    name: str
    expression: str | None = None


@dataclass
class StubModifier:
    name: str


@dataclass
class StubFunction:
    name: str
    view: bool = False
    pure: bool = False
    is_constructor: bool = False
    modifiers: list[StubModifier] = field(default_factory=list)


@dataclass
class StubContract:
    name: str
    state_variables: list[StubVariable] = field(default_factory=list)
    functions: list[StubFunction] = field(default_factory=list)


@dataclass
class StubSlither:
    contracts: list[StubContract] = field(default_factory=list)
