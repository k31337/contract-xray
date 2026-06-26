"""Command-line interface for contract-xray."""

from __future__ import annotations

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from contract_xray.etherscan import EtherscanClientError, fetch_contract_source
from contract_xray.rules import ALL_RULES
from contract_xray.slither_wrapper import SlitherAnalysisError, analyze_source

load_dotenv()

app = typer.Typer(help="Scan a Solidity smart contract for common scam/honeypot patterns.")
console = Console()


@app.command()
def scan(
    address: str = typer.Argument(..., help="Contract address to analyze."),
    chain: str = typer.Option("ethereum", "--chain", "-c", help="Chain to query (ethereum, bsc, polygon)."),
) -> None:
    """Fetch a contract's verified source code and display its metadata."""
    try:
        contract = fetch_contract_source(address, chain)
    except EtherscanClientError as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1)

    console.print(
        Panel(
            f"[bold]Contract:[/bold] {contract.contract_name}\n"
            f"[bold]Address:[/bold] {contract.address}\n"
            f"[bold]Chain:[/bold] {contract.chain}\n"
            f"[bold]Compiler:[/bold] {contract.compiler_version}\n"
            f"[bold]Optimization used:[/bold] {contract.optimization_used}",
            title="Contract Metadata",
        )
    )
    console.print(Syntax(contract.source_code, "solidity", line_numbers=True))

    try:
        slither = analyze_source(contract)
    except SlitherAnalysisError as exc:
        console.print(f"[bold red]Slither error:[/bold red] {exc}")
        raise typer.Exit(code=1)

    contract_names = ", ".join(c.name for c in slither.contracts)
    console.print(Panel(f"[bold]Contracts found:[/bold] {contract_names}", title="Slither Analysis"))

    findings = [finding for rule in ALL_RULES for finding in rule.evaluate(slither)]
    if not findings:
        console.print("[bold green]No red flags detected by the current rule set.[/bold green]")
        return

    for finding in findings:
        console.print(
            Panel(
                f"[bold]Severity:[/bold] {finding.severity.value.upper()}\n"
                f"[bold]Contract:[/bold] {finding.contract_name}\n"
                f"{finding.description}",
                title=f"[bold red]{finding.title}[/bold red]",
            )
        )


if __name__ == "__main__":
    app()
