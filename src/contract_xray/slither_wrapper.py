"""Wrapper around Slither for analyzing a contract's verified source code."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from slither import Slither
from slither.exceptions import SlitherError

from contract_xray.etherscan import ContractSource

MAIN_FILE_NAME = "Contract.sol"


class SlitherAnalysisError(Exception):
    """Raised when Slither fails to compile or analyze the contract source."""


def _is_json_object(source_code: str) -> bool:
    stripped = source_code.strip()
    return stripped.startswith("{")


def _parse_multi_file_source(source_code: str) -> dict[str, str]:
    """Parse Etherscan's multi-file source formats into {filename: content}.

    Etherscan returns either a standard-json-input payload (single leading
    brace) or a legacy double-braced payload, both containing a "sources"
    mapping of filename -> {"content": "..."}.
    """
    stripped = source_code.strip()
    if stripped.startswith("{{") and stripped.endswith("}}"):
        stripped = stripped[1:-1]

    payload = json.loads(stripped)
    sources = payload.get("sources", {})
    if not sources:
        raise SlitherAnalysisError("Multi-file source payload has no 'sources' entries.")

    return {filename: data["content"] for filename, data in sources.items()}


def _write_source_to_disk(contract: ContractSource, target_dir: Path) -> Path:
    """Write the contract's source code to disk and return the path to compile."""
    if _is_json_object(contract.source_code):
        files = _parse_multi_file_source(contract.source_code)
        for filename, content in files.items():
            file_path = target_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
        # Slither can analyze a whole directory of linked sources.
        return target_dir

    main_file = target_dir / MAIN_FILE_NAME
    main_file.write_text(contract.source_code, encoding="utf-8")
    return main_file


def analyze_source(contract: ContractSource) -> Slither:
    """Compile and analyze a contract's verified source code with Slither.

    Raises SlitherAnalysisError if the source cannot be parsed or compiled.
    """
    with tempfile.TemporaryDirectory(prefix="contract-xray-") as tmp_dir:
        target_path = _write_source_to_disk(contract, Path(tmp_dir))
        try:
            return Slither(str(target_path))
        except SlitherError as exc:
            raise SlitherAnalysisError(
                f"Slither failed to analyze {contract.address}: {exc}"
            ) from exc
        except (json.JSONDecodeError, KeyError) as exc:
            raise SlitherAnalysisError(
                f"Failed to parse source code for {contract.address}: {exc}"
            ) from exc
