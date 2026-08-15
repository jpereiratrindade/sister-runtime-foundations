#!/usr/bin/env python3
"""Focused regression tests for causal RF-A0 evidence modeling."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from epistemic_model import (
    compare_predictions,
    derive_candidate_learning,
    detect_unexpected_observations,
)


def main() -> int:
    commitments = [
        {
            "id": "P-SUPPORTED",
            "comparison_contract": [
                {
                    "check_id": "CHECK-A",
                    "supporting_results": ["PASS"],
                    "contradicting_results": ["FAIL"],
                }
            ],
        },
        {
            "id": "P-CONTRADICTED",
            "comparison_contract": [
                {
                    "check_id": "CHECK-B",
                    "supporting_results": ["PASS"],
                    "contradicting_results": ["FAIL"],
                }
            ],
        },
        {
            "id": "P-INCONCLUSIVE",
            "comparison_contract": [
                {
                    "check_id": "CHECK-MISSING",
                    "supporting_results": ["PASS"],
                    "contradicting_results": ["FAIL"],
                }
            ],
        },
    ]
    checks = [
        {"id": "CHECK-A", "result": "PASS", "evidence": "a.json"},
        {"id": "CHECK-B", "result": "FAIL", "evidence": "b.json"},
        {"id": "UNRELATED", "result": "PASS", "evidence": "unrelated.json"},
    ]
    comparisons = compare_predictions(commitments, checks)
    outcomes = {item["prediction_id"]: item["comparison"] for item in comparisons}
    assert outcomes == {
        "P-SUPPORTED": "SUPPORTED",
        "P-CONTRADICTED": "CONTRADICTED",
        "P-INCONCLUSIVE": "INCONCLUSIVE",
    }
    assert comparisons[0]["evidence_references"] == ["a.json"]
    assert "unrelated.json" not in comparisons[0]["evidence_references"]

    normal_context = {
        "praxis_exit_status": 1,
        "praxis_output": "gate missing — NONE",
        "expected_praxis_marker": "gate missing — NONE",
        "praxis_clean": True,
        "protocol_digest_match": True,
        "historical_prefix_match": True,
        "collector_exit_status": 0,
        "platform_is_fedora": True,
        "gate_failure": None,
    }
    assert detect_unexpected_observations(normal_context) == []
    anomalous = dict(normal_context)
    anomalous.update({"praxis_exit_status": 0, "praxis_clean": False})
    unexpected = detect_unexpected_observations(anomalous)
    assert {item["classification"] for item in unexpected} == {
        "contradiction",
        "unexpected_dependency_state",
    }

    contracts = [
        {"id": "L1", "depends_on": ["P-SUPPORTED"], "proposal": "candidate one"},
        {"id": "L2", "depends_on": ["P-CONTRADICTED"], "proposal": "candidate two"},
    ]
    proposals = derive_candidate_learning(contracts, comparisons)
    assert [item["id"] for item in proposals] == ["L1"]
    assert proposals[0]["governance_adoption"] == "NONE"
    assert proposals[0]["evidence_references"] == ["a.json"]

    print("epistemic causal model: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
