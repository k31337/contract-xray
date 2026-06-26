"""Client for fetching verified Solidity source code from Etherscan-family APIs.

Supports any EVM chain whose explorer exposes the Etherscan-compatible
"getsourcecode" endpoint (Etherscan, BscScan, Polygonscan, ...).
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import requests

REQUEST_TIMEOUT_SECONDS = 30

CHAIN_CONFIG = {
    "ethereum": {
        "api_url": "https://api.etherscan.io/api",
        "api_key_env": "ETHERSCAN_API_KEY",
    },
    "bsc": {
        "api_url": "https://api.bscscan.com/api",
        "api_key_env": "BSCSCAN_API_KEY",
    },
    "polygon": {
        "api_url": "https://api.polygonscan.com/api",
        "api_key_env": "POLYGONSCAN_API_KEY",
    },
}


class EtherscanClientError(Exception):
    """Raised when the Etherscan-family API cannot return a usable response."""


class MissingApiKeyError(EtherscanClientError):
    """Raised when the API key for the requested chain is not configured."""


class ContractNotVerifiedError(EtherscanClientError):
    """Raised when the requested contract has no verified source code."""


class UnsupportedChainError(EtherscanClientError):
    """Raised when the requested chain is not in CHAIN_CONFIG."""


@dataclass
class ContractSource:
    """Verified source code and metadata for a contract."""

    address: str
    chain: str
    contract_name: str
    compiler_version: str
    optimization_used: bool
    source_code: str
    abi: str


def _get_chain_config(chain: str) -> dict:
    try:
        return CHAIN_CONFIG[chain]
    except KeyError as exc:
        supported = ", ".join(CHAIN_CONFIG)
        raise UnsupportedChainError(
            f"Unsupported chain '{chain}'. Supported chains: {supported}."
        ) from exc


def _get_api_key(chain: str) -> str:
    config = _get_chain_config(chain)
    api_key = os.environ.get(config["api_key_env"])
    if not api_key:
        raise MissingApiKeyError(
            f"Missing API key for chain '{chain}'. "
            f"Set the {config['api_key_env']} environment variable."
        )
    return api_key


def fetch_contract_source(address: str, chain: str = "ethereum") -> ContractSource:
    """Fetch the verified source code and metadata for a contract address.

    Raises MissingApiKeyError if the API key for the chain is not set,
    UnsupportedChainError if the chain is not recognized, and
    ContractNotVerifiedError if the contract has no verified source code.
    """
    config = _get_chain_config(chain)
    api_key = _get_api_key(chain)

    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "apikey": api_key,
    }

    response = requests.get(config["api_url"], params=params, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    payload = response.json()

    if payload.get("status") != "1":
        message = payload.get("result") or payload.get("message") or "unknown error"
        raise EtherscanClientError(f"Etherscan API error for {address} on {chain}: {message}")

    results = payload.get("result") or []
    if not results:
        raise ContractNotVerifiedError(f"No source code found for {address} on {chain}.")

    result = results[0]
    source_code = result.get("SourceCode") or ""
    if not source_code:
        raise ContractNotVerifiedError(
            f"Contract {address} on {chain} is not verified (empty source code)."
        )

    return ContractSource(
        address=address,
        chain=chain,
        contract_name=result.get("ContractName", ""),
        compiler_version=result.get("CompilerVersion", ""),
        optimization_used=result.get("OptimizationUsed") == "1",
        source_code=source_code,
        abi=result.get("ABI", ""),
    )
