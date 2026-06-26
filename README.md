# contract-xray

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-k31337-181717?logo=github)](https://github.com/k31337)

Static analysis tool that scans Solidity smart contracts for common scam and honeypot patterns and generates a red-flag report.

`contract-xray` takes a contract address on an EVM-compatible chain, fetches its verified source code, runs it through [Slither](https://github.com/crytic/slither), and applies a set of heuristics to flag known scam/honeypot patterns. It produces a human-readable report in the terminal and an optional JSON export.

## What it detects

- Hidden blacklist functions (addresses can be silently blocked from transferring/selling)
- Unrestricted or hidden `mint` functions
- Ownership that has not been renounced (or can be reclaimed)
- Disproportionate buy/sell tax (including taxes that can be changed after deployment)
- Pause/transfer traps (the contract owner can disable transfers or trading at will)
- Other known red flags surfaced by Slither's detector suite

## What it does NOT do

- It does **not** guarantee a contract is safe. Absence of detected red flags is not proof of safety.
- It does **not** perform formal verification or a full manual security audit.
- It does **not** analyze unverified contracts (no source code available means no static analysis).
- It does **not** detect off-chain risks (rug pulls via liquidity removal, team behavior, social engineering, etc.) beyond what is visible in the contract code itself.

**Use this tool as a first-pass triage, not as a final verdict. Always do your own research.**

## Installation

```bash
git clone https://github.com/k31337/contract-xray.git
cd contract-xray
pip install -e .
```

Copy `.env.example` to `.env` and fill in the API key(s) for the chain(s) you want to analyze:

```bash
cp .env.example .env
```

## Usage

```bash
contract-xray scan <CONTRACT_ADDRESS> --chain ethereum
```

Export the report as JSON:

```bash
contract-xray scan <CONTRACT_ADDRESS> --chain ethereum --json report.json
```

Supported chains: `ethereum`, `bsc`, `polygon` (configurable via environment variables, see `.env.example`).

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT — see [LICENSE](LICENSE).

## Author

[k31337](https://github.com/k31337)
