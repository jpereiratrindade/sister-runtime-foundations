#!/usr/bin/env python3
"""Minimal tamper-evident ledger for decisive SRF experimental runs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


GENESIS_HASH = "0" * 64


class LedgerError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def empty_ledger() -> dict[str, Any]:
    return {
        "artifact": "srf-experimental-run-ledger/0.1",
        "genesis_hash": GENESIS_HASH,
        "entries": [],
    }


def load_ledger(evidence_root: Path) -> dict[str, Any]:
    path = evidence_root / "ledger.json"
    if not path.exists():
        return empty_ledger()
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("artifact") != "srf-experimental-run-ledger/0.1":
        raise LedgerError("unknown ledger artifact")
    if value.get("genesis_hash") != GENESIS_HASH:
        raise LedgerError("ledger genesis hash")
    if not isinstance(value.get("entries"), list):
        raise LedgerError("ledger entries")
    return value


def validate_ledger(evidence_root: Path) -> dict[str, Any]:
    ledger = load_ledger(evidence_root)
    previous = GENESIS_HASH
    seen: set[str] = set()

    for entry in ledger["entries"]:
        run_id = entry.get("run_id")
        if not isinstance(run_id, str) or not run_id or run_id in seen:
            raise LedgerError("invalid or duplicate run identity")
        seen.add(run_id)
        record_path = evidence_root / entry.get("record", "")
        if not record_path.is_file():
            raise LedgerError(f"run record missing: {run_id}")
        record = json.loads(record_path.read_text(encoding="utf-8"))
        if record.get("run_id") != run_id:
            raise LedgerError(f"run identity mismatch: {run_id}")
        if record.get("previous_chain_hash") != previous:
            raise LedgerError(f"previous hash mismatch: {run_id}")

        run_directory = record_path.parent
        evidence = record.get("evidence_sha256")
        if not isinstance(evidence, dict):
            raise LedgerError(f"evidence manifest missing: {run_id}")
        for relative, expected in evidence.items():
            path = run_directory / relative
            if not path.is_file() or sha256_file(path) != expected:
                raise LedgerError(f"evidence digest mismatch: {run_id}/{relative}")

        protocol_snapshot = record.get("protocol_snapshot")
        if protocol_snapshot is not None:
            snapshot = run_directory / protocol_snapshot
            if (
                not snapshot.is_file()
                or sha256_file(snapshot) != record.get("protocol_sha256")
                or protocol_snapshot not in evidence
            ):
                raise LedgerError(f"protocol snapshot mismatch: {run_id}")

        payload = dict(record)
        observed_chain = payload.pop("chain_hash", None)
        expected_chain = hashlib.sha256(
            bytes.fromhex(previous) + canonical_bytes(payload)
        ).hexdigest()
        if observed_chain != expected_chain or entry.get("chain_hash") != expected_chain:
            raise LedgerError(f"chain hash mismatch: {run_id}")
        previous = expected_chain

    latest_path = evidence_root / "latest-run.json"
    if ledger["entries"]:
        if not latest_path.is_file():
            raise LedgerError("latest-run pointer missing")
        latest = json.loads(latest_path.read_text(encoding="utf-8"))
        final = ledger["entries"][-1]
        if latest.get("run_id") != final["run_id"] or latest.get("chain_hash") != previous:
            raise LedgerError("latest-run pointer mismatch")
    elif latest_path.exists():
        raise LedgerError("latest-run pointer exists for empty ledger")

    return {
        "runs": len(ledger["entries"]),
        "head_chain_hash": previous,
        "valid": True,
    }


def append_run(evidence_root: Path, run_directory: Path, record: dict[str, Any]) -> str:
    ledger = load_ledger(evidence_root)
    validation = validate_ledger(evidence_root)
    previous = validation["head_chain_hash"]
    if record.get("previous_chain_hash") != previous:
        raise LedgerError("new run does not extend current ledger head")

    relative_record = run_directory.relative_to(evidence_root) / "run-record.json"
    if (run_directory / "run-record.json").exists():
        raise LedgerError("run record already exists")

    evidence_manifest: dict[str, str] = {}
    for path in sorted(run_directory.iterdir(), key=lambda item: item.name):
        if path.is_file() and path.name != "run-record.json":
            evidence_manifest[path.name] = sha256_file(path)
    record["evidence_sha256"] = evidence_manifest
    payload = dict(record)
    chain_hash = hashlib.sha256(
        bytes.fromhex(previous) + canonical_bytes(payload)
    ).hexdigest()
    record["chain_hash"] = chain_hash
    (run_directory / "run-record.json").write_text(
        json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    ledger["entries"].append(
        {
            "run_id": record["run_id"],
            "record": relative_record.as_posix(),
            "chain_hash": chain_hash,
        }
    )
    (evidence_root / "ledger.json").write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (evidence_root / "latest-run.json").write_text(
        json.dumps(
            {
                "run_id": record["run_id"],
                "record": relative_record.as_posix(),
                "chain_hash": chain_hash,
                "result": record["result"],
                "protocol_sha256": record["protocol_sha256"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    validate_ledger(evidence_root)
    return chain_hash


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", metavar="PROJECT_ROOT", required=True)
    arguments = parser.parse_args()
    evidence_root = (
        Path(arguments.verify).resolve() / "docs/experiments/evidence/rf-a0"
    )
    try:
        result = validate_ledger(evidence_root)
    except (LedgerError, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL RF-A0 experimental run ledger: {error}")
        return 1
    print(
        "PASS RF-A0 experimental run ledger: "
        f"runs={result['runs']} head={result['head_chain_hash']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
