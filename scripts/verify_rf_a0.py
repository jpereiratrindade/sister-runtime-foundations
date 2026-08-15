#!/usr/bin/env python3
"""Fail-closed, prediction-committing RF-A0 experimental gate."""

from __future__ import annotations

import ast
import datetime as dt
import hashlib
import json
import os
import platform
import re
import sys
from pathlib import Path
from typing import Any

from execution_authority import (
    ALLOWED_ROLES,
    AuthorityViolation,
    ExecutionContext,
    run_external,
)
from epistemic_model import (
    EpistemicModelError,
    compare_predictions,
    derive_candidate_learning,
    detect_unexpected_observations,
)
from run_ledger import GENESIS_HASH, LedgerError, append_run, canonical_bytes, validate_ledger


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / "docs/experiments/evidence/rf-a0"
RUNS_ROOT = EVIDENCE_ROOT / "runs"
STATE = ROOT / ".hoa/project-state.yaml"
EXPERIMENT = ROOT / ".hoa/experiments/rf-a0.json"
PROTOCOL = ROOT / ".hoa/protocols/rf-a0-epistemic-closure.json"
PROTOCOL_INDEX = ROOT / ".hoa/protocols/index.json"
HISTORICAL_PREFIX = ROOT / "governance/historical-evidence-prefix.json"
HISTORICAL_PROTOCOL_DIGEST = "cba33aabff5e45d499f097bac16bda6fb33cef5add32924d906be89bda074e40"
AUTHORITY_POLICY = ROOT / "governance/execution-authority.json"


class GateFailure(RuntimeError):
    pass


checks: list[dict[str, Any]] = []
actions: list[dict[str, Any]] = []
human_log: list[str] = []


def emit(message: str = "") -> None:
    print(message)
    human_log.append(message)


def record_check(
    identity: str,
    property_text: str,
    condition: bool,
    evidence: str,
    failure_reason: str,
    *,
    success_result: str = "PASS",
) -> None:
    result = success_result if condition else "FAIL"
    item = {
        "id": identity,
        "property": property_text,
        "result": result,
        "evidence": evidence,
        "failure_reason": None if condition else failure_reason,
    }
    checks.append(item)
    emit(f"{result} {identity} — {property_text}")
    if not condition:
        raise GateFailure(f"{identity}: {failure_reason}")


def record_observed_result(
    identity: str,
    property_text: str,
    result: str,
    evidence: str,
    failure_reason: str | None,
) -> None:
    checks.append(
        {
            "id": identity,
            "property": property_text,
            "result": result,
            "evidence": evidence,
            "failure_reason": failure_reason,
        }
    )
    emit(f"{result} {identity} — {property_text}")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_identity() -> dict[str, Any]:
    manifest: dict[str, str] = {}
    for path in sorted(ROOT.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if relative.parts[0] in {".git", ".build"}:
            continue
        if "__pycache__" in relative.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        if relative.parts[:4] == ("docs", "experiments", "evidence", "rf-a0"):
            continue
        manifest[relative.as_posix()] = sha256_file(path)
    return {
        "algorithm": "sha256",
        "tree_sha256": hashlib.sha256(canonical_bytes(manifest)).hexdigest(),
        "files": manifest,
    }


def create_run() -> tuple[str, Path, str, str, dict[str, Any], str]:
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    RUNS_ROOT.mkdir(parents=True, exist_ok=True)
    ledger_state = validate_ledger(EVIDENCE_ROOT)
    previous_hash = ledger_state["head_chain_hash"]
    protocol_digest = sha256_file(PROTOCOL)
    source = source_identity()
    timestamp = dt.datetime.now(dt.timezone.utc)
    run_id = timestamp.strftime("%Y%m%dT%H%M%S.%fZ") + "-" + protocol_digest[:12]
    run_directory = RUNS_ROOT / run_id
    run_directory.mkdir(parents=False, exist_ok=False)
    archive = ROOT / ".hoa/protocols/archive" / f"sha256-{protocol_digest}.json"
    if not archive.is_file() or sha256_file(archive) != protocol_digest:
        raise GateFailure("content-addressed protocol archive missing or invalid")
    protocol_snapshot = run_directory / "protocol-snapshot.json"
    protocol_snapshot.write_bytes(archive.read_bytes())
    committed_at = timestamp.isoformat()
    commitment = {
        "artifact": "srf-pre-observation-commitment/0.1",
        "run_id": run_id,
        "milestone": "RF-A0",
        "experiment": "RF-A0-HARDENING",
        "committed_at_utc": committed_at,
        "protocol": PROTOCOL.relative_to(ROOT).as_posix(),
        "protocol_sha256": protocol_digest,
        "protocol_archive": archive.relative_to(ROOT).as_posix(),
        "protocol_snapshot": protocol_snapshot.name,
        "previous_chain_hash": previous_hash,
        "pre_run_project_state_sha256": sha256_file(STATE),
        "pre_run_source_identity": source,
        "claim_boundary": "This commitment establishes only that these protocol bytes were hashed and recorded before this orchestrator collected the run's decisive observations.",
    }
    (run_directory / "commitment.json").write_text(
        json.dumps(commitment, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return run_id, run_directory, protocol_digest, previous_hash, source, committed_at


def find_praxis() -> Path:
    configured = os.environ.get("PRAXIS_ROOT")
    candidates = [
        Path(configured) if configured else None,
        ROOT.parent / "Praxis",
    ]
    for candidate in candidates:
        if candidate and (candidate / "scripts/governed_method_schema.py").is_file():
            return candidate.resolve()
    raise GateFailure("current Praxis checkout not found; set PRAXIS_ROOT")


def execute(
    authority: ExecutionContext,
    run_directory: Path,
    name: str,
    role: str,
    command: list[str],
    *,
    environment: dict[str, str] | None = None,
) -> Any:
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    result = run_external(
        authority,
        role,
        command,
        cwd=ROOT,
        text=True,
        stdout=-1,
        stderr=-2,
        check=False,
        env=environment,
    )
    completed = dt.datetime.now(dt.timezone.utc).isoformat()
    output_name = f"action-{name}.txt"
    (run_directory / output_name).write_text(result.stdout, encoding="utf-8")
    actions.append(
        {
            "id": name,
            "authority_role": role,
            "argv": command,
            "started_at_utc": started,
            "completed_at_utc": completed,
            "exit_status": result.returncode,
            "output": output_name,
        }
    )
    return result


def observe_praxis_identity(
    authority: ExecutionContext,
    run_directory: Path,
    praxis: Path,
    suffix: str,
) -> dict[str, Any]:
    head_action = execute(
        authority,
        run_directory,
        f"praxis-head-{suffix}",
        "git.praxis_head",
        ["git", "-C", str(praxis), "rev-parse", "HEAD"],
    )
    status_action = execute(
        authority,
        run_directory,
        f"praxis-status-{suffix}",
        "git.praxis_status",
        [
            "git",
            "-C",
            str(praxis),
            "status",
            "--porcelain",
            "--untracked-files=all",
        ],
    )
    observed_files = {
        "validator": praxis / "scripts/validate_governed_project.py",
        "schema_helper": praxis / "scripts/governed_method_schema.py",
        "project_state_schema": praxis
        / "contracts/methodology/project-state.schema.json",
        "experiment_record_schema": praxis
        / "contracts/methodology/experiment-record.schema.json",
    }
    identity = {
        "observed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "repository": str(praxis),
        "git_head": head_action.stdout.strip() if head_action.returncode == 0 else None,
        "git_head_exit_status": head_action.returncode,
        "git_status_porcelain": status_action.stdout,
        "git_status_exit_status": status_action.returncode,
        "working_tree_clean": status_action.returncode == 0
        and not status_action.stdout.strip(),
        "files": {
            role: {
                "path": path.relative_to(praxis).as_posix(),
                "sha256": sha256_file(path),
            }
            for role, path in observed_files.items()
        },
        "observation_method": "read-only Git commands plus SHA-256 over the exact validator/helper/schema bytes used by this run",
    }
    (run_directory / f"praxis-identity-{suffix}.json").write_text(
        json.dumps(identity, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return identity


def validate_protocol(protocol_digest: str) -> dict[str, Any]:
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    record_check(
        "RF-A0.EPISTEMIC.PROTOCOL",
        "pre-observation protocol is separate and observation-free",
        protocol.get("status") == "fixed_before_decisive_observation"
        and isinstance(protocol.get("commitments"), list)
        and len(protocol["commitments"]) == 6,
        PROTOCOL.relative_to(ROOT).as_posix(),
        "protocol identity/status/commitment count",
    )
    forbidden_post_fields = {
        "observation",
        "result",
        "interpretation",
        "learning",
        "confidence",
        "gate_consequence",
    }
    for commitment in protocol["commitments"]:
        missing = {
            "id",
            "question",
            "prior_understanding",
            "hypothesis",
            "prediction",
            "alternative_explanation",
            "contradiction_condition",
            "comparison_contract",
        } - commitment.keys()
        if missing or forbidden_post_fields & commitment.keys():
            raise GateFailure(f"protocol commitment fields: {commitment.get('id')}")
    record_check(
        "RF-A0.EPISTEMIC.DIGEST",
        "protocol digest is SHA-256 over the committed bytes",
        re.fullmatch(r"[0-9a-f]{64}", protocol_digest) is not None,
        "commitment.json",
        "invalid protocol digest",
    )
    return protocol


def validate_historical_post_observation_learning() -> None:
    learning_path = ROOT / ".hoa/learning/rf-a0.json"
    learning = json.loads(learning_path.read_text(encoding="utf-8"))
    entries = learning.get("entries")
    expected_ids = {
        "RF-A0-H01",
        "RF-A0-H02",
        "RF-A0-H03",
        "RF-A0-H04",
        "RF-A0-H05",
        "RF-A0-H06",
        "RF-A0-P01",
        "RF-A0-P02",
        "RF-A0-P03",
        "RF-A0-P04",
        "RF-A0-P05",
        "RF-A0-P06",
    }
    record_check(
        "RF-A0.EPISTEMIC.SYNTHESIS",
        "post-observation learning is separate, complete, and linked to the protocol",
        learning.get("artifact") == "srf-post-observation-learning/0.2"
        and learning.get("status") == "synthesized"
        and learning.get("protocol", {}).get("sha256") == HISTORICAL_PROTOCOL_DIGEST
        and isinstance(entries, list)
        and {item.get("protocol_id") for item in entries} == expected_ids,
        ".hoa/learning/rf-a0.json",
        "post-observation synthesis identity, protocol link, or entry set",
    )
    required = {
        "observation",
        "confrontation_with_prediction",
        "interpretation",
        "learning",
        "confidence",
        "candidate_rule",
        "candidate_rule_disposition",
        "governance_consequence",
        "open_question",
    }
    forbidden = {
        "prior_understanding",
        "hypothesis",
        "prediction",
        "alternative_explanation",
        "contradiction_condition",
    }
    for entry in entries:
        if required - entry.keys() or forbidden & entry.keys():
            raise GateFailure(f"post-observation learning fields: {entry.get('protocol_id')}")
        if entry.get("confidence") not in {"TENTATIVE", "SUPPORTED", "STRONGLY_SUPPORTED"}:
            raise GateFailure(f"post-observation confidence: {entry.get('protocol_id')}")
    candidate = ROOT / ".hoa/learning/candidates/praxis-bootstrap-representation-gap.json"
    record_check(
        "RF-A0.LEARNING.PRAXIS_CANDIDATE",
        "Praxis bootstrap gap remains a project-local candidate without adoption authority",
        candidate.is_file()
        and json.loads(candidate.read_text(encoding="utf-8")).get("praxis_adoption_authority")
        == "none",
        candidate.relative_to(ROOT).as_posix(),
        "candidate missing or implies Praxis authority",
    )


def validate_protocol_archives(run_directory: Path, protocol_digest: str) -> bool:
    index = json.loads(PROTOCOL_INDEX.read_text(encoding="utf-8"))
    entries = index.get("entries", [])
    observed: dict[str, str] = {}
    valid = True
    for entry in entries:
        digest = entry.get("sha256")
        archive = ROOT / entry.get("archive", "")
        if not isinstance(digest, str) or not archive.is_file():
            valid = False
            continue
        observed[digest] = sha256_file(archive)
        if observed[digest] != digest:
            valid = False
    snapshot = run_directory / "protocol-snapshot.json"
    valid = (
        valid
        and observed.get(HISTORICAL_PROTOCOL_DIGEST) == HISTORICAL_PROTOCOL_DIGEST
        and observed.get(protocol_digest) == protocol_digest
        and snapshot.is_file()
        and sha256_file(snapshot) == protocol_digest
    )
    (run_directory / "protocol-archive-validation.json").write_text(
        json.dumps(
            {
                "index": PROTOCOL_INDEX.relative_to(ROOT).as_posix(),
                "observed_archive_digests": observed,
                "run_snapshot_sha256": sha256_file(snapshot) if snapshot.is_file() else None,
                "valid": valid,
                "claim_boundary": "Historical protocol archives were created prospectively; exact bytes are recoverable but archival creation is not backdated.",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    record_check(
        "RF-A0.EPISTEMIC.PROTOCOL_ARCHIVE",
        "historical and current protocol bytes are content-addressed and the run snapshot agrees",
        valid,
        "protocol-archive-validation.json;.hoa/protocols/index.json;protocol-snapshot.json",
        "protocol archive, index, or snapshot mismatch",
    )
    return valid


def validate_historical_prefix(run_directory: Path) -> bool:
    expected = json.loads(HISTORICAL_PREFIX.read_text(encoding="utf-8"))
    ledger = json.loads((EVIDENCE_ROOT / "ledger.json").read_text(encoding="utf-8"))
    expected_runs = expected["runs"]
    observed_entries = ledger.get("entries", [])[: len(expected_runs)]
    valid = len(observed_entries) == expected["historical_run_count"]
    manifest: dict[str, str] = {}
    observed_runs: list[dict[str, str]] = []
    for wanted, entry in zip(expected_runs, observed_entries, strict=True):
        record_path = EVIDENCE_ROOT / entry["record"]
        observed = {
            "run_id": entry.get("run_id", ""),
            "chain_hash": entry.get("chain_hash", ""),
            "record_sha256": sha256_file(record_path) if record_path.is_file() else "",
        }
        observed_runs.append(observed)
        if observed != wanted:
            valid = False
        if record_path.is_file():
            record = json.loads(record_path.read_text(encoding="utf-8"))
            if record.get("protocol_sha256") != expected["protocol_sha256"]:
                valid = False
            for path in sorted(record_path.parent.iterdir(), key=lambda item: item.name):
                if path.is_file():
                    manifest[path.relative_to(EVIDENCE_ROOT).as_posix()] = sha256_file(path)
    aggregate = hashlib.sha256(canonical_bytes(manifest)).hexdigest()
    valid = (
        valid
        and observed_entries[-1]["chain_hash"] == expected["historical_head"]
        and len(manifest) == expected["historical_file_count"]
        and aggregate == expected["historical_content_aggregate_sha256"]
    )
    (run_directory / "historical-integrity.json").write_text(
        json.dumps(
            {
                "expected_manifest": HISTORICAL_PREFIX.relative_to(ROOT).as_posix(),
                "observed_runs": observed_runs,
                "observed_historical_head": observed_entries[-1]["chain_hash"]
                if observed_entries
                else None,
                "observed_file_count": len(manifest),
                "observed_content_aggregate_sha256": aggregate,
                "valid": valid,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    record_check(
        "RF-A0.HISTORY.PREFIX_IMMUTABLE",
        "the original three-run chain and all 93 historical files are byte-identical",
        valid,
        "historical-integrity.json;governance/historical-evidence-prefix.json",
        "historical run, record, protocol association, or aggregate digest changed",
    )
    return valid


def validate_governance(praxis: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    sys.path.insert(0, str(praxis / "scripts"))
    from governed_method_schema import (  # type: ignore[import-not-found]
        load_flat_yaml,
        load_schema,
        validate_instance,
    )

    state = load_flat_yaml(STATE)
    state_errors = validate_instance(
        state, load_schema(praxis / "contracts/methodology/project-state.schema.json")
    )
    record_check(
        "RF-A0.GOVERNANCE.SCHEMA",
        "canonical state conforms to the current Praxis schema",
        not state_errors,
        ".hoa/project-state.yaml",
        "; ".join(state_errors),
    )
    experiment = json.loads(EXPERIMENT.read_text(encoding="utf-8"))
    experiment_errors = validate_instance(
        experiment,
        load_schema(praxis / "contracts/methodology/experiment-record.schema.json"),
    )
    record_check(
        "RF-A0.EXPERIMENT.SCHEMA",
        "RF-A0 record conforms to the current Praxis experiment schema",
        not experiment_errors,
        ".hoa/experiments/rf-a0.json",
        "; ".join(experiment_errors),
    )
    record_check(
        "RF-A0.GOVERNANCE.STATE",
        "RF-A0 remains active and is not promoted",
        state.get("phase") == "RF-A0"
        and state.get("status") == "active"
        and state.get("next_milestone") == "RF-A0"
        and state.get("next_milestone_status") == "active"
        and state.get("next_milestone_authorized") is True
        and experiment["experiment"].get("status") == "active",
        ".hoa/project-state.yaml;.hoa/experiments/rf-a0.json",
        "RF-A0 state or authorization mismatch",
    )
    record_check(
        "RF-A0.GOVERNANCE.NO_PRIOR_VERIFICATION",
        "all last-verified fields use honest pre-history sentinels",
        state.get("last_verified_milestone") == "NONE"
        and state.get("last_verified_commit") == "0000000"
        and state.get("last_verified_gate") == "NONE"
        and state.get("last_verified_evidence") == "NONE",
        ".hoa/project-state.yaml",
        "last-verified fields imply a verification that does not exist",
    )
    record_check(
        "RF-A0.GOVERNANCE.AUTHORITY",
        "only RF-A0 is authorized and RF-A1 through RF-A9 are unauthorized",
        experiment.get("authority", {}).get("authorized_milestones") == ["RF-A0"]
        and experiment.get("authority", {}).get("unauthorized_milestones")
        == [f"RF-A{number}" for number in range(1, 10)],
        ".hoa/experiments/rf-a0.json",
        "milestone authority mismatch",
    )
    for item in experiment.get("inputs", []):
        relative = Path(item["path"])
        path = (ROOT / relative).resolve()
        record_check(
            f"RF-A0.INPUT.{item['role'].upper()}",
            "constitutive input is project-relative and digest-valid",
            not relative.is_absolute()
            and path.is_relative_to(ROOT)
            and path.is_file()
            and sha256_file(path) == item["sha256"],
            item["path"],
            "input path or digest mismatch",
        )
    return state, experiment


def validate_execution_authority() -> None:
    policy = json.loads(AUTHORITY_POLICY.read_text(encoding="utf-8"))
    record_check(
        "RF-A0.AUTHORITY.ALLOWLIST",
        "declared external-execution roles equal the implemented allowlist",
        policy.get("default") == "deny"
        and policy.get("shell_execution") == "forbidden"
        and set(policy.get("roles", {})) == set(ALLOWED_ROLES),
        "governance/execution-authority.json;scripts/execution_authority.py",
        "policy and implementation roles differ",
    )
    violations: list[str] = []
    authority_path = ROOT / "scripts/execution_authority.py"
    for path in sorted([*ROOT.glob("scripts/*.py"), *ROOT.glob("tests/*.py")]):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            function = node.func
            if (
                isinstance(function, ast.Attribute)
                and isinstance(function.value, ast.Name)
                and function.value.id == "subprocess"
                and function.attr in {"run", "Popen", "call", "check_call", "check_output"}
                and path != authority_path
            ):
                violations.append(f"{path.relative_to(ROOT)}:{node.lineno}:subprocess.{function.attr}")
            if (
                isinstance(function, ast.Attribute)
                and isinstance(function.value, ast.Name)
                and function.value.id == "os"
                and function.attr in {"system", "popen"}
            ):
                violations.append(f"{path.relative_to(ROOT)}:{node.lineno}:os.{function.attr}")
            for keyword in node.keywords:
                if (
                    keyword.arg == "shell"
                    and isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is True
                ):
                    violations.append(f"{path.relative_to(ROOT)}:{node.lineno}:shell=True")
    record_check(
        "RF-A0.AUTHORITY.CALL_SITES",
        "all project subprocess creation is centralized and shell-free",
        not violations,
        "scripts/*.py;tests/*.py",
        ", ".join(violations),
    )


def scope_audit(authority: ExecutionContext, run_directory: Path) -> None:
    forbidden_names = {
        "dockerfile",
        "containerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        "compose.yml",
        "compose.yaml",
    }
    introduced = [
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and ".build" not in path.parts
        and path.name.lower() in forbidden_names
    ]
    record_check(
        "RF-A0.SCOPE.ARTIFACTS",
        "no forbidden deployment manifest exists",
        not introduced,
        "project tree",
        ", ".join(introduced),
    )
    implementation = (ROOT / "CMakeLists.txt").read_text(encoding="utf-8") + (
        ROOT / "src/runtime_probe.cpp"
    ).read_text(encoding="utf-8")
    forbidden_tokens = [
        "docker",
        "podman",
        "containerd",
        "kubernetes",
        "unshare",
        "nsenter",
        "chroot",
        "overlayfs",
        "cgroup.procs",
        "setns(",
        "clone3(",
        "iptables",
        "nftables",
        "sudo",
    ]
    findings = [token for token in forbidden_tokens if token in implementation.lower()]
    record_check(
        "RF-A0.SCOPE.IMPLEMENTATION",
        "native probe and build contain no later-milestone mechanism",
        not findings,
        "CMakeLists.txt;src/runtime_probe.cpp",
        ", ".join(findings),
    )
    record_check(
        "RF-A0.SCOPE.UNPRIVILEGED",
        "gate executes without root privileges",
        os.geteuid() != 0,
        "os.geteuid",
        "effective UID is root",
    )

    remote = execute(authority, run_directory, "git-remote", "git.remote", ["git", "remote"])
    record_check(
        "RF-A0.GIT.NO_REMOTE",
        "Git has no configured remote",
        remote.returncode == 0 and not remote.stdout.strip(),
        "action-git-remote.txt",
        "remote exists or git remote failed",
    )
    head = execute(
        authority,
        run_directory,
        "git-head",
        "git.head",
        ["git", "rev-parse", "--verify", "HEAD"],
    )
    record_check(
        "RF-A0.GIT.NO_COMMIT",
        "repository still has no commit",
        head.returncode != 0,
        "action-git-head.txt",
        "HEAD unexpectedly resolves",
    )
    execute(
        authority,
        run_directory,
        "git-status",
        "git.status",
        ["git", "status", "--porcelain", "--untracked-files=all"],
    )


def parse_os_release() -> dict[str, str]:
    values: dict[str, str] = {}
    for line in Path("/etc/os-release").read_text(encoding="utf-8").splitlines():
        key, separator, raw = line.partition("=")
        if separator:
            values[key] = raw.strip().strip('"')
    return values


def compiler_metadata(build: Path) -> dict[str, str]:
    candidates = list(build.glob("CMakeFiles/*/CMakeCXXCompiler.cmake"))
    if len(candidates) != 1:
        raise GateFailure("CMake compiler metadata file count")
    text = candidates[0].read_text(encoding="utf-8")

    def setting(name: str) -> str:
        match = re.search(rf'^set\({re.escape(name)} "([^"]*)"\)', text, re.MULTILINE)
        if match is None:
            raise GateFailure(f"CMake compiler setting missing: {name}")
        return match.group(1)

    return {
        "compiler": setting("CMAKE_CXX_COMPILER"),
        "compiler_id": setting("CMAKE_CXX_COMPILER_ID"),
        "compiler_version": setting("CMAKE_CXX_COMPILER_VERSION"),
    }


def collect_platform_and_toolchain(
    run_directory: Path,
    build: Path,
    cmake_version_output: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    os_release = parse_os_release()
    compiler = compiler_metadata(build)
    cmake_first_line = cmake_version_output.splitlines()[0]
    glibc = os.confstr("CS_GNU_LIBC_VERSION")
    platform_record = {
        "captured_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "distribution": {
            "id": os_release.get("ID"),
            "name": os_release.get("NAME"),
            "version_id": os_release.get("VERSION_ID"),
            "pretty_name": os_release.get("PRETTY_NAME"),
            "source": "/etc/os-release",
        },
        "kernel_release": platform.release(),
        "machine_architecture": platform.machine(),
        "glibc": glibc,
        "python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
            "executable": sys.executable,
        },
        "cmake": cmake_first_line,
        "compiler": compiler,
        "claim_boundary": "This identifies the userspace, kernel, libc, and toolchain of this run; it does not generalize observed behavior to every Fedora release or Linux environment.",
    }
    compile_commands = json.loads((build / "compile_commands.json").read_text(encoding="utf-8"))
    probe_entries = [
        item
        for item in compile_commands
        if item.get("file", "").endswith("src/runtime_probe.cpp")
    ]
    if len(probe_entries) != 1:
        raise GateFailure("probe compile command count")
    command = probe_entries[0].get("command") or " ".join(probe_entries[0].get("arguments", []))
    toolchain_record = {
        **compiler,
        "cmake": cmake_first_line,
        "actual_compile_command": command,
        "cxx_standard_requested": "23",
        "cxx_extensions": False,
        "language_contract": "C++23",
        "standard_library_capability_contract": "Only facilities actually used by RF-A0; no claim of complete C++23 library support.",
    }
    (run_directory / "platform-baseline.json").write_text(
        json.dumps(platform_record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (run_directory / "toolchain-baseline.json").write_text(
        json.dumps(toolchain_record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return platform_record, toolchain_record


def whitespace_check() -> list[str]:
    errors: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or ".build" in path.parts:
            continue
        data = path.read_bytes()
        if b"\0" in data:
            continue
        text = data.decode("utf-8")
        for number, line in enumerate(text.splitlines(), start=1):
            if line.rstrip(" \t") != line:
                errors.append(f"{path.relative_to(ROOT)}:{number}:trailing whitespace")
        if data and not data.endswith(b"\n"):
            errors.append(f"{path.relative_to(ROOT)}:missing final newline")
    return errors


def write_gate_results(run_directory: Path, run_id: str, result: str) -> None:
    value = {
        "artifact": "srf-machine-readable-gate-results/0.1",
        "run_id": run_id,
        "milestone": "RF-A0",
        "result": result,
        "checks": checks,
    }
    (run_directory / "gate-results.json").write_text(
        json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_verification(run_directory: Path, result: str, failure: str | None) -> None:
    lines = [
        "SisTer Runtime Foundations RF-A0 epistemic closure evidence\n",
        f"run_id={run_directory.name}\n",
        f"result={result}\n",
        "\n",
        *(f"{line}\n" for line in human_log),
    ]
    if failure:
        lines.append(f"FAILURE {failure}\n")
    lines.extend(
        [
            "\n",
            "LIMITATION stress testing increases race sensitivity but is not mathematical proof.\n",
            "LIMITATION the protocol digest proves only orchestrated ordering of exact bytes.\n",
            "LIMITATION command allowlisting bounds direct project-script authority, not the semantics of allowed tools or CMake children.\n",
            f"RF-A0: {result}\n",
        ]
    )
    text = "".join(lines)
    (run_directory / "verification.txt").write_text(text, encoding="utf-8")
    (EVIDENCE_ROOT / "verification.txt").write_text(text, encoding="utf-8")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    (EVIDENCE_ROOT / "verification.sha256").write_text(
        f"{digest}  verification.txt\n", encoding="utf-8"
    )


def main() -> int:
    global checks, actions, human_log
    checks = []
    actions = []
    human_log = []
    emit("SisTer Runtime Foundations — RF-A0 epistemic closure gate")
    emit(f"root={ROOT}")

    try:
        run_id, run_directory, protocol_digest, previous_hash, pre_source, committed_at = create_run()
    except (GateFailure, LedgerError, OSError, ValueError, json.JSONDecodeError) as error:
        emit(f"FAIL unable to establish pre-observation commitment: {error}")
        return 1

    emit(f"run_id={run_id}")
    emit(f"protocol_sha256={protocol_digest}")
    failure: str | None = None
    result = "FAIL"
    praxis = find_praxis()
    authority = ExecutionContext(ROOT, praxis)
    build = ROOT / ".build/runs" / run_id
    protocol: dict[str, Any] = {}
    unexpected_context: dict[str, Any] = {
        "praxis_exit_status": None,
        "praxis_output": "",
        "expected_praxis_marker": "gate missing — NONE",
        "praxis_clean": None,
        "protocol_digest_match": None,
        "historical_prefix_match": None,
        "collector_exit_status": None,
        "platform_is_fedora": None,
        "gate_failure": None,
    }

    try:
        protocol = validate_protocol(protocol_digest)
        validate_historical_post_observation_learning()
        archive_valid = validate_protocol_archives(run_directory, protocol_digest)
        historical_valid = validate_historical_prefix(run_directory)
        unexpected_context["protocol_digest_match"] = archive_valid
        unexpected_context["historical_prefix_match"] = historical_valid
        praxis_before = observe_praxis_identity(
            authority, run_directory, praxis, "before-validator"
        )
        unexpected_context["praxis_clean"] = praxis_before["working_tree_clean"]
        state, _ = validate_governance(praxis)
        validate_execution_authority()
        scope_audit(authority, run_directory)

        cmake_version = execute(
            authority,
            run_directory,
            "cmake-version",
            "cmake.version",
            ["cmake", "--version"],
        )
        record_check(
            "RF-A0.BUILD.CMAKE_VERSION",
            "CMake version query succeeds",
            cmake_version.returncode == 0,
            "action-cmake-version.txt",
            "cmake --version failed",
        )
        record_check(
            "RF-A0.BUILD.CLEAN_DIRECTORY",
            "decisive run starts with a new build directory",
            not build.exists(),
            str(build.relative_to(ROOT)),
            "run build directory already exists",
        )
        configure = execute(
            authority,
            run_directory,
            "configure",
            "cmake.configure",
            [
                "cmake",
                "-S",
                str(ROOT),
                "-B",
                str(build),
                "-DCMAKE_BUILD_TYPE=Debug",
                "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON",
            ],
        )
        record_check(
            "RF-A0.BUILD.CONFIGURE",
            "clean CMake configure succeeds",
            configure.returncode == 0,
            "action-configure.txt",
            "CMake configure failed",
        )
        build_result = execute(
            authority,
            run_directory,
            "build",
            "cmake.build",
            ["cmake", "--build", str(build), "--parallel"],
        )
        record_check(
            "RF-A0.BUILD.CXX23",
            "C++23 warnings-as-errors build succeeds",
            build_result.returncode == 0,
            "action-build.txt",
            "C++ build failed",
        )

        platform_record, toolchain = collect_platform_and_toolchain(
            run_directory, build, cmake_version.stdout
        )
        record_check(
            "RF-A0.PLATFORM.FEDORA",
            "decisive platform identifies a Fedora userspace",
            platform_record["distribution"]["id"] == "fedora",
            "platform-baseline.json",
            f"distribution ID is {platform_record['distribution']['id']!r}",
        )
        unexpected_context["platform_is_fedora"] = (
            platform_record["distribution"]["id"] == "fedora"
        )
        required_platform = [
            platform_record["distribution"].get("version_id"),
            platform_record.get("kernel_release"),
            platform_record.get("machine_architecture"),
            platform_record.get("glibc"),
            platform_record.get("python", {}).get("version"),
            platform_record.get("cmake"),
            platform_record.get("compiler", {}).get("compiler_version"),
        ]
        record_check(
            "RF-A0.PLATFORM.COMPLETE",
            "distribution, kernel, architecture, libc, compiler, CMake, and Python are recorded",
            all(required_platform),
            "platform-baseline.json",
            "one or more baseline fields are missing",
        )
        compile_command = toolchain["actual_compile_command"]
        record_check(
            "RF-A0.TOOLCHAIN.CXX23_COMMAND",
            "actual probe compile command requests C++23 and warnings as errors",
            re.search(r"-std=(?:gnu\+\+|c\+\+)23(?:\s|$)", compile_command) is not None
            and all(option in compile_command for option in ["-Wall", "-Wextra", "-Wpedantic", "-Werror"]),
            "toolchain-baseline.json",
            "compile command lacks required standard or warning option",
        )

        ctest = execute(
            authority,
            run_directory,
            "ctest",
            "ctest.run",
            ["ctest", "--test-dir", str(build), "--output-on-failure"],
        )
        record_check(
            "RF-A0.TEST.CTEST",
            "CTest integration and repeated signal exercise pass",
            ctest.returncode == 0,
            "action-ctest.txt",
            "CTest failed",
        )
        epistemic_test_passed = (
            ctest.returncode == 0 and "epistemic-model" in ctest.stdout
        )
        record_check(
            "RF-A0.EPISTEMIC.COMPARISON_MODEL",
            "focused tests demonstrate independent supported, contradicted, and inconclusive comparisons",
            epistemic_test_passed,
            "action-ctest.txt;tests/epistemic_model_test.py",
            "causal comparison regression test did not pass",
        )
        record_check(
            "RF-A0.EPISTEMIC.UNEXPECTED_CHANNEL",
            "focused tests demonstrate empty normal and populated anomalous observation channels",
            epistemic_test_passed,
            "action-ctest.txt;tests/epistemic_model_test.py",
            "unexpected-observation channel regression test did not pass",
        )
        record_check(
            "RF-A0.EPISTEMIC.LEARNING_BOUNDARY",
            "focused tests suppress unsupported learning and preserve non-adoption authority",
            epistemic_test_passed,
            "action-ctest.txt;tests/epistemic_model_test.py",
            "candidate-learning boundary regression test did not pass",
        )

        collector_environment = os.environ.copy()
        collector_environment["SRF_PROTOCOL_SHA256"] = protocol_digest
        collector_environment["SRF_RUN_ID"] = run_id
        collector = execute(
            authority,
            run_directory,
            "runtime-observation",
            "python.collector",
            [
                sys.executable,
                str(ROOT / "scripts/collect_rf_a0_evidence.py"),
                str(build / "srf-runtime-probe"),
                str(run_directory),
            ],
            environment=collector_environment,
        )
        unexpected_context["collector_exit_status"] = collector.returncode
        record_check(
            "RF-A0.RUNTIME.COLLECTOR",
            "decisive runtime collector succeeds",
            collector.returncode == 0,
            "action-runtime-observation.txt",
            "runtime collector failed",
        )
        observation = json.loads((run_directory / "observation.json").read_text(encoding="utf-8"))
        stress = json.loads((run_directory / "signal-stress.json").read_text(encoding="utf-8"))
        commitment = json.loads((run_directory / "commitment.json").read_text(encoding="utf-8"))
        record_check(
            "RF-A0.EPISTEMIC.ORDER",
            "committed protocol predates decisive runtime observation and digest agrees",
            observation.get("protocol_sha256") == protocol_digest
            and commitment.get("protocol_sha256") == protocol_digest
            and committed_at < observation.get("observation_started_at_utc", "")
            and sha256_file(PROTOCOL) == protocol_digest,
            "commitment.json;protocol-snapshot.json;observation.json",
            "protocol digest or temporal order mismatch",
        )
        record_check(
            "RF-A0.PROCESS.IDENTITY",
            "process identity and executable are correlated through procfs",
            all(key in observation for key in ["pid", "ppid", "uid", "gid", "executable"]),
            "observation.json;proc-status.txt;probe-stdout.txt",
            "identity evidence incomplete",
        )
        record_check(
            "RF-A0.FILE.OPEN_FD",
            "retained regular file descriptor is externally correlated",
            isinstance(observation.get("regular_fd"), int),
            "observation.json;proc-fd.txt",
            "regular descriptor evidence incomplete",
        )
        record_check(
            "RF-A0.NET.LOOPBACK_LISTENER",
            "loopback listener address, inode, state, and connection are correlated",
            observation.get("listen_address") == "127.0.0.1"
            and observation.get("tcp_state") == "LISTEN"
            and observation.get("loopback_connection_succeeded") is True,
            "observation.json;proc-net-tcp-listener.txt",
            "loopback listener evidence incomplete",
        )
        record_check(
            "RF-A0.CONTEXT.NAMESPACE",
            "probe namespace links match the launcher for compared types",
            observation.get("namespace_links_match_launcher") is True,
            "observation.json;proc-ns.txt;launcher-ns.txt",
            "namespace membership differs",
        )
        record_check(
            "RF-A0.CONTEXT.CGROUP",
            "probe cgroup record matches the launcher without a governance claim",
            observation.get("cgroup_record_matches_launcher") is True,
            "observation.json;proc-cgroup.txt;launcher-cgroup.txt",
            "cgroup membership differs",
        )
        record_check(
            "RF-A0.SIGNAL.CONTROLLED_SHUTDOWN",
            "Linux signalfd drives controlled SIGTERM shutdown without forced kill",
            observation.get("signal_wait") == "signalfd"
            and observation.get("shutdown_signal") == 15
            and observation.get("controlled_shutdown") is True
            and observation.get("forced_kill") is False,
            "observation.json;probe-stdout.txt;proc-fd.txt",
            "controlled signalfd shutdown evidence incomplete",
        )
        record_check(
            "RF-A0.SIGNAL.STRESS",
            "128 repeated shutdown iterations complete without forced termination",
            stress.get("requested_iterations") == 128
            and stress.get("completed_iterations") == 128
            and stress.get("all_controlled") is True,
            "signal-stress.json",
            str(stress.get("failure")),
        )
        record_check(
            "RF-A0.TOOLCHAIN.CXX23_ACCEPTED",
            "compiled probe reports the accepted C++23 language macro",
            observation.get("cplusplus", 0) >= 202302,
            "observation.json;toolchain-baseline.json",
            "__cplusplus is below 202302L",
        )

        praxis_result = execute(
            authority,
            run_directory,
            "praxis-validator",
            "python.praxis_validator",
            [
                sys.executable,
                str(praxis / "scripts/validate_governed_project.py"),
                str(ROOT),
            ],
        )
        praxis_after = observe_praxis_identity(
            authority, run_directory, praxis, "after-validator"
        )
        stable_identity_fields = [
            "repository",
            "git_head",
            "git_status_porcelain",
            "working_tree_clean",
            "files",
        ]
        praxis_identity_stable = all(
            praxis_before.get(field) == praxis_after.get(field)
            for field in stable_identity_fields
        )
        record_check(
            "RF-A0.PRAXIS.IDENTITY_OBSERVED",
            "Praxis HEAD, cleanliness, validator, helper, and schema identities are directly observed and stable",
            praxis_identity_stable
            and re.fullmatch(r"[0-9a-f]{40}", str(praxis_before.get("git_head")))
            is not None
            and all(
                re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is not None
                for item in praxis_before["files"].values()
            ),
            "praxis-identity-before-validator.json;praxis-identity-after-validator.json",
            "Praxis identity observation failed or changed during validation",
        )
        expected_praxis_marker = "gate missing — NONE"
        if praxis_result.returncode != 0 and expected_praxis_marker in praxis_result.stdout:
            praxis_classification = "EXPECTED_FAIL_CLOSED"
            praxis_failure_reason = None
        elif praxis_result.returncode == 0:
            praxis_classification = "UNEXPECTED_PASS"
            praxis_failure_reason = "validator unexpectedly accepted the pre-history state"
        else:
            praxis_classification = "FAIL"
            praxis_failure_reason = "validator failed outside the predicted pre-history boundary"
        unexpected_context["praxis_exit_status"] = praxis_result.returncode
        unexpected_context["praxis_output"] = praxis_result.stdout
        praxis_machine = {
            "observed_identity_before": "praxis-identity-before-validator.json",
            "observed_identity_after": "praxis-identity-after-validator.json",
            "observed_praxis_head": praxis_before["git_head"],
            "validator": praxis_before["files"]["validator"],
            "consulted_contracts": {
                "project_state_schema": praxis_before["files"]["project_state_schema"],
                "experiment_record_schema": praxis_before["files"]["experiment_record_schema"],
                "schema_helper": praxis_before["files"]["schema_helper"],
            },
            "exit_status": praxis_result.returncode,
            "classification": praxis_classification,
            "observed_failure": praxis_result.stdout,
            "candidate_gap": "PRAXIS BOOTSTRAP REPRESENTATION GAP",
            "facts": {
                "last_verified_milestone": state["last_verified_milestone"],
                "last_verified_commit": state["last_verified_commit"],
                "head_exists": False,
            },
        }
        (run_directory / "praxis-validator.json").write_text(
            json.dumps(praxis_machine, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        record_observed_result(
            "RF-A0.PRAXIS.BOOTSTRAP_GAP",
            "the observed Praxis validator outcome is classified against the unchanged H06 prediction",
            praxis_classification,
            "action-praxis-validator.txt;praxis-validator.json;praxis-identity-before-validator.json",
            praxis_failure_reason,
        )

        diff_check = execute(
            authority,
            run_directory,
            "git-diff-check",
            "git.diff_check",
            ["git", "diff", "--check"],
        )
        record_check(
            "RF-A0.INTEGRITY.GIT_DIFF",
            "Git whitespace check passes",
            diff_check.returncode == 0,
            "action-git-diff-check.txt",
            "git diff --check failed",
        )
        whitespace_errors = whitespace_check()
        record_check(
            "RF-A0.INTEGRITY.UNTRACKED_TEXT",
            "all authored and generated text passes the untracked-tree whitespace equivalent",
            not whitespace_errors,
            "project text tree",
            "; ".join(whitespace_errors),
        )
        post_source = source_identity()
        record_check(
            "RF-A0.REVERSIBILITY.SOURCE_STATE",
            "decisive gate changed evidence/build state but not project source identity",
            post_source["tree_sha256"] == pre_source["tree_sha256"],
            "commitment.json;run-record.json",
            "project source changed during experiment",
        )
        result = "PASS"
    except (
        AuthorityViolation,
        GateFailure,
        LedgerError,
        EpistemicModelError,
        OSError,
        ValueError,
        KeyError,
        json.JSONDecodeError,
    ) as error:
        failure = str(error)
        unexpected_context["gate_failure"] = failure
        emit(f"FAIL {failure}")

    try:
        unexpected_observations = detect_unexpected_observations(unexpected_context)
        comparisons = compare_predictions(protocol.get("commitments", []), checks)
        candidate_learning = derive_candidate_learning(
            protocol.get("candidate_learning_contracts", []), comparisons
        )
    except (EpistemicModelError, KeyError, TypeError, ValueError) as error:
        failure = failure or f"epistemic outcome modeling: {error}"
        result = "FAIL"
        unexpected_context["gate_failure"] = failure
        unexpected_observations = detect_unexpected_observations(unexpected_context)
        comparisons = []
        candidate_learning = []

    causal_traceability = bool(comparisons) and all(
        item.get("relevant_checks")
        and item.get("comparison") in {"SUPPORTED", "CONTRADICTED", "INCONCLUSIVE"}
        for item in comparisons
    )
    record_observed_result(
        "RF-A0.EPISTEMIC.CAUSAL_TRACEABILITY",
        "every protocol prediction is compared only through declared checks and evidence",
        "PASS" if causal_traceability else "FAIL",
        "epistemic-outcomes.json;.hoa/protocols/rf-a0-epistemic-closure.json",
        None if causal_traceability else "one or more comparisons lack causal traceability",
    )
    if not causal_traceability:
        result = "FAIL"
        failure = failure or "prediction comparison traceability"
    comparison_states = {item["comparison"] for item in comparisons}
    if comparison_states == {"SUPPORTED"} and not unexpected_observations:
        epistemic_conclusion = "ALL_PROTOCOL_PREDICTIONS_SUPPORTED_NO_UNEXPECTED_OBSERVATIONS"
    elif "CONTRADICTED" in comparison_states:
        epistemic_conclusion = "MIXED_WITH_CONTRADICTION"
    else:
        epistemic_conclusion = "MIXED_OR_INCONCLUSIVE"
    (run_directory / "unexpected-observations.json").write_text(
        json.dumps(
            {
                "derived_from_run_outcomes": True,
                "observations": unexpected_observations,
                "empty_meaning": "No configured anomaly condition was observed"
                if not unexpected_observations
                else None,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (run_directory / "epistemic-outcomes.json").write_text(
        json.dumps(
            {
                "observation_layer": "gate-results.json and raw evidence artifacts",
                "prediction_comparisons": comparisons,
                "unexpected_observations": "unexpected-observations.json",
                "machine_interpretation_status": "PROPOSALS_ONLY",
                "candidate_learning_proposals": candidate_learning,
                "governance_adoption": [],
                "epistemic_conclusion": epistemic_conclusion,
            },
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    write_gate_results(run_directory, run_id, result)
    write_verification(run_directory, result, failure)
    post_source = source_identity()
    record = {
        "artifact": "srf-decisive-experimental-run/0.2",
        "run_id": run_id,
        "milestone": "RF-A0",
        "experiment": "RF-A0-EPISTEMIC-CLOSURE",
        "previous_chain_hash": previous_hash,
        "protocol_sha256": protocol_digest,
        "protocol_snapshot": "protocol-snapshot.json",
        "pre_run": {
            "source_tree_sha256": pre_source["tree_sha256"],
            "project_state_sha256": sha256_file(STATE),
            "commitment": "commitment.json",
        },
        "actions": actions,
        "raw_evidence": [
            path.name
            for path in sorted(run_directory.iterdir(), key=lambda item: item.name)
            if path.is_file() and path.name not in {"run-record.json"}
        ],
        "validation": "gate-results.json",
        "result": result,
        "failure": failure,
        "observation_layer": {
            "machine_checks": "gate-results.json",
            "raw_artifacts": "raw_evidence",
        },
        "unexpected_observations": unexpected_observations,
        "prediction_comparisons": comparisons,
        "interpretation_layer": {
            "status": "PROPOSALS_ONLY",
            "artifact": "epistemic-outcomes.json",
        },
        "candidate_learning": candidate_learning,
        "governance_adoption": [],
        "epistemic_conclusion": epistemic_conclusion,
        "post_run": {
            "source_tree_sha256": post_source["tree_sha256"],
            "project_state_sha256": sha256_file(STATE),
        },
    }
    try:
        chain_hash = append_run(EVIDENCE_ROOT, run_directory, record)
        emit(f"ledger_chain_hash={chain_hash}")
        ledger_validation = validate_ledger(EVIDENCE_ROOT)
        emit(
            "PASS RF-A0.LEDGER.INTEGRITY — "
            f"runs={ledger_validation['runs']} head={ledger_validation['head_chain_hash']}"
        )
    except (LedgerError, OSError, ValueError, json.JSONDecodeError) as error:
        emit(f"FAIL ledger finalization: {error}")
        return 1

    emit(f"RF-A0: {result}")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
