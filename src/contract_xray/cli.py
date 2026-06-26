"""Command-line interface for contract-xray."""

from __future__ import annotations

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from contract_xray.etherscan import EtherscanClientError, fetch_contract_source

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


if __name__ == "__main__":
    app()
