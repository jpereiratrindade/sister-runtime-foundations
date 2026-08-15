#!/usr/bin/env python3
"""Pure causal models for RF-A0 comparisons, anomalies, and learning candidates."""

from __future__ import annotations

from typing import Any


class EpistemicModelError(RuntimeError):
    pass


def compare_predictions(
    commitments: list[dict[str, Any]], checks: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Compare each prediction using only its declared check contracts."""
    check_index: dict[str, dict[str, Any]] = {}
    for check in checks:
        identity = check.get("id")
        if not isinstance(identity, str) or identity in check_index:
            raise EpistemicModelError("checks require unique string identities")
        check_index[identity] = check

    comparisons: list[dict[str, Any]] = []
    for commitment in commitments:
        prediction_id = commitment.get("id")
        contracts = commitment.get("comparison_contract")
        if not isinstance(prediction_id, str) or not isinstance(contracts, list) or not contracts:
            raise EpistemicModelError(f"comparison contract missing: {prediction_id}")

        relevant: list[dict[str, Any]] = []
        missing: list[str] = []
        contradicted = False
        supported = True
        evidence: set[str] = set()
        for contract in contracts:
            check_id = contract.get("check_id")
            if check_id not in check_index:
                missing.append(str(check_id))
                supported = False
                continue
            check = check_index[check_id]
            result = check.get("result")
            supporting_results = contract.get("supporting_results", [])
            contradicting_results = contract.get("contradicting_results", [])
            if result in contradicting_results:
                contradicted = True
                supported = False
            elif result not in supporting_results:
                supported = False
            references = [
                item.strip()
                for item in str(check.get("evidence", "")).split(";")
                if item.strip()
            ]
            evidence.update(references)
            relevant.append(
                {
                    "check_id": check_id,
                    "observed_result": result,
                    "supporting_results": supporting_results,
                    "contradicting_results": contradicting_results,
                    "evidence": references,
                }
            )

        if contradicted:
            comparison = "CONTRADICTED"
        elif supported and not missing:
            comparison = "SUPPORTED"
        else:
            comparison = "INCONCLUSIVE"
        comparisons.append(
            {
                "prediction_id": prediction_id,
                "comparison": comparison,
                "relevant_checks": relevant,
                "missing_check_ids": missing,
                "evidence_references": sorted(evidence),
                "causal_boundary": "Only declared relevant checks contribute; global gate status is not an input.",
            }
        )
    return comparisons


def detect_unexpected_observations(context: dict[str, Any]) -> list[dict[str, Any]]:
    """Derive anomaly records from actual run outcomes; an empty result is meaningful."""
    observations: list[dict[str, Any]] = []

    def add(identity: str, classification: str, observation: str, evidence: str) -> None:
        observations.append(
            {
                "id": identity,
                "classification": classification,
                "observation": observation,
                "evidence": evidence,
                "status": "UNRESOLVED",
                "scope_consequence": "record_only",
            }
        )

    praxis_exit = context.get("praxis_exit_status")
    praxis_output = str(context.get("praxis_output", ""))
    expected_marker = str(context.get("expected_praxis_marker", ""))
    if praxis_exit == 0:
        add(
            "RF-A0-U01",
            "contradiction",
            "Praxis validator unexpectedly passed the uncommitted pre-history state.",
            "praxis-validator.json;action-praxis-validator.txt",
        )
    elif praxis_exit is not None and expected_marker and expected_marker not in praxis_output:
        add(
            "RF-A0-U02",
            "unexpected_tool_behavior",
            "Praxis validator failed, but not at the predicted pre-history boundary.",
            "praxis-validator.json;action-praxis-validator.txt",
        )
    if context.get("praxis_clean") is False:
        add(
            "RF-A0-U03",
            "unexpected_dependency_state",
            "The observed Praxis working tree was not clean.",
            "praxis-identity.json;action-praxis-status.txt",
        )
    if context.get("protocol_digest_match") is False:
        add(
            "RF-A0-U04",
            "evidence_generation_failure",
            "The protocol commitment, archive, snapshot, or observation digest disagreed.",
            "commitment.json;protocol-snapshot.json;observation.json",
        )
    if context.get("historical_prefix_match") is False:
        add(
            "RF-A0-U05",
            "evidence_generation_failure",
            "The immutable three-run historical prefix changed.",
            "historical-integrity.json",
        )
    if context.get("collector_exit_status") not in {None, 0}:
        add(
            "RF-A0-U06",
            "partial_observation",
            "The runtime collector did not complete successfully.",
            "action-runtime-observation.txt",
        )
    if context.get("platform_is_fedora") is False:
        add(
            "RF-A0-U07",
            "unexpected_environment_property",
            "The decisive environment did not identify as Fedora.",
            "platform-baseline.json",
        )
    if context.get("gate_failure"):
        add(
            "RF-A0-U08",
            "possible_methodological_issue",
            f"The gate encountered a failure: {context['gate_failure']}",
            "gate-results.json;verification.txt",
        )
    return observations


def derive_candidate_learning(
    contracts: list[dict[str, Any]], comparisons: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Propose learning only when every declared prediction dependency is supported."""
    comparison_index = {item["prediction_id"]: item for item in comparisons}
    proposals: list[dict[str, Any]] = []
    for contract in contracts:
        dependencies = contract.get("depends_on", [])
        if not dependencies or any(
            comparison_index.get(identity, {}).get("comparison") != "SUPPORTED"
            for identity in dependencies
        ):
            continue
        evidence = sorted(
            {
                reference
                for identity in dependencies
                for reference in comparison_index[identity].get("evidence_references", [])
            }
        )
        proposals.append(
            {
                "id": contract["id"],
                "status": "CANDIDATE",
                "proposal": contract["proposal"],
                "supported_by_predictions": dependencies,
                "evidence_references": evidence,
                "interpretation_required": True,
                "governance_adoption": "NONE",
                "authority_boundary": "Machine generation proposes; it does not adopt a project or Praxis rule.",
            }
        )
    return proposals
