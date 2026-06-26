"""Report generation: aggregates findings into a risk-rated report."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from contract_xray.etherscan import ContractSource
from contract_xray.rules.base import Finding, Severity

SEVERITY_ORDER = [Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]

SEVERITY_STYLE = {
    Severity.LOW: "yellow",
    Severity.MEDIUM: "orange3",
    Severity.HIGH: "red",
    Severity.CRITICAL: "bold red",
}


@dataclass
class Report:
    """Aggregated scan result for a single contract."""

    address: str
    chain: str
    contract_name: str
    risk_level: Severity
    findings: list[Finding] = field(default_factory=list)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["risk_level"] = self.risk_level.value
        data["findings"] = [
            {**asdict(finding), "severity": finding.severity.value} for finding in self.findings
        ]
        return data


def build_report(contract: ContractSource, findings: list[Finding]) -> Report:
    """Build a Report from a contract and the findings produced by the rule engine."""
    risk_level = max(
        (finding.severity for finding in findings),
        key=SEVERITY_ORDER.index,
        default=Severity.LOW,
    ) if findings else Severity.LOW

    return Report(
        address=contract.address,
        chain=contract.chain,
        contract_name=contract.contract_name,
        risk_level=risk_level,
        findings=findings,
    )


def render_terminal_report(report: Report, console: Console) -> None:
    """Render a Report as human-readable output in the terminal."""
    risk_style = SEVERITY_STYLE[report.risk_level]
    console.print(
        Panel(
            f"[bold]Contract:[/bold] {report.contract_name}\n"
            f"[bold]Address:[/bold] {report.address}\n"
            f"[bold]Chain:[/bold] {report.chain}\n"
            f"[bold]Risk level:[/bold] [{risk_style}]{report.risk_level.value.upper()}[/{risk_style}]\n"
            f"[bold]Findings:[/bold] {len(report.findings)}",
            title="Scan Summary",
        )
    )

    if not report.findings:
        console.print("[bold green]No red flags detected by the current rule set.[/bold green]")
        return

    for finding in report.findings:
        style = SEVERITY_STYLE[finding.severity]
        console.print(
            Panel(
                f"[bold]Severity:[/bold] [{style}]{finding.severity.value.upper()}[/{style}]\n"
                f"[bold]Contract:[/bold] {finding.contract_name}\n"
                f"{finding.description}",
                title=f"[{style}]{finding.title}[/{style}]",
            )
        )


def export_json_report(report: Report, path: Path) -> None:
    """Write a Report to disk as JSON."""
    path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
