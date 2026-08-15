# RF-A0 bootstrap hardening synthesis

RF-A0 remains active and unverified. This hardening pass strengthens its
technical and experimental baseline without beginning RF-A1.

## Fedora reference boundary

The first hardening run directly observed Fedora Linux 44 Workstation on kernel
`7.1.6-201.fc44.x86_64`, architecture `x86_64`, and glibc 2.43. Fedora is SRF's
reference execution platform; the broader research subject remains Linux
runtime semantics. A result observed through a Linux kernel interface on this
machine is still an observation made in this Fedora userspace and kernel. The
project does not infer cross-distribution invariance from one run.

## C++23 and interface classification

SRF application source has a C++23 language contract. The run recorded GCC
16.1.1, the actual `-std=c++23` compile command, successful warnings-as-errors
compilation, and `__cplusplus=202302` from the probe.

- C++ language: ownership/lifetime structure, types, control flow, and the
  enforced C++23 compilation mode.
- C++ standard library: strings, views, vectors, filesystem paths, streams,
  `std::from_chars`, and error categories. RF-A0 needs no uniquely C++23 library
  facility and makes no complete-library-support claim.
- POSIX interfaces: process IDs and credentials, descriptors, signal masks,
  sockets, polling, and filesystem calls where their semantics are under study.
- Linux-specific interfaces: procfs, `signalfd`, `accept4`, and the exact
  namespace/cgroup observation surfaces.

Direct Linux/POSIX use is intentional experimental visibility, not hidden behind
a portability framework.

## Signal/event learning

The former handler/flag loop could test zero, receive SIGTERM, and then enter an
indefinite `poll()` with no event left to wake it. A timeout would reduce symptom
duration without fixing the synchronization error.

The probe now blocks SIGINT/SIGTERM before creating `signalfd` and polls the
signal descriptor together with its listener. The blocked signal remains pending
until read as a descriptor event, removing that specific lost-wakeup window. One
full observation, 64 CTest iterations, and 128 collector iterations completed
cleanly. Repetition supports the implementation; correctness of the selected
ordering comes from the mechanism, not a claim of proof by stress.

## Prediction-first evidence

`.hoa/protocols/rf-a0-pre-observation.json` contains questions, hypotheses,
predictions, alternatives, and contradiction conditions but no observations or
interpretations. Before decisive collection, the orchestrator writes its digest
and pre-run source identity to `commitment.json`. Observation records carry the
same digest, and the gate compares timestamps and rehashes the protocol.

This proves only that those exact bytes were committed before that orchestrated
observation. It does not prove authorship, originality, prediction truth, or lack
of earlier unrelated knowledge.

## Bounded execution authority

All project-owned Python subprocess creation is centralized in
`scripts/execution_authority.py`. The default-deny policy constrains executable
identity and arguments for CMake, CTest, read-only Git inspection, exact Python
scripts, and the built probe. Static AST inspection rejects direct subprocess
calls elsewhere and any `shell=True` path. CMake's compiler/linker children are
an explicit delegated build boundary rather than falsely enumerated commands.

## Run ledger and evidence categories

Each decisive run records pre-state, protocol commitment, material actions,
raw evidence, machine-readable checks, prediction comparisons, post-state, and
file digests. Each `run-record.json` incorporates the previous chain hash. This
is a local tamper-evidence mechanism, not a distributed ledger or external
timestamp authority.

Raw observations, generated comparisons, authored interpretation, candidate
rules, and accepted project-local gate obligations remain separate fields and
artifacts. Unexpected observations have an explicit run-record channel even when
the list is empty.

## Praxis bootstrap representation gap

Three outcomes must not be collapsed:

1. Schema validity: **PASS** for the sentinel-bearing flat state.
2. SRF internal pre-history consistency: **PASS** when milestone, gate, evidence,
   and commit all honestly state that no verification exists.
3. Praxis governed-project validity: **EXPECTED FAIL-CLOSED** because the generic
   validator requires real verified provenance.

The previous real gate/evidence paths semantically implied a verification that
`last_verified_milestone: NONE` denied. They are now `NONE`; this is internally
clear but not invented as Praxis-wide vocabulary. The gap is recorded only as a
candidate for separate Praxis evaluation.

## Not yet known

The hardening does not establish behavior on other Fedora/Linux environments,
complete C++23 library support, mathematical concurrency proof, production
SisTer lifecycle requirements, or any RF-A1+ property.
