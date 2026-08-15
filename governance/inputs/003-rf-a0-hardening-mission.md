# Mission: Harden RF-A0 Before the First Governed Commit

Continue working on the existing **SisTer Runtime Foundations** repository.

This is NOT a new milestone.

This is NOT RF-A1.

This is a hardening pass over the existing RF-A0 bootstrap before the first commit is authorized.

Do not rewrite the project from scratch. Preserve valid existing work and modify only what is justified by the findings below.

The project remains:

```text
name: SisTer Runtime Foundations
repository: sister-runtime-foundations
short_name: SRF
language: C++23
reference operating system: Fedora Linux
reference system: SisTer
methodology: Praxis
current milestone: RF-A0
```

The guiding principle remains:

> We do not begin with containers. We begin with a Linux process and earn every boundary.

## 1. Preserve the RF-A0 boundary

RF-A0 remains the only authorized milestone.

Do not implement RF-A1 or any later milestone.

Do not create filesystem isolation, namespaces, cgroups, containers, virtual networks, privilege isolation or deployment abstractions.

Do not use Docker, Podman, containerd, Compose, Kubernetes, `unshare`, `nsenter`, `chroot`, OverlayFS, network namespace creation, cgroup manipulation, routing/NAT/firewall mutation, `sudo`, root privileges or persistent host mutation.

Do not inspect or copy SisTer implementation.

Do not modify Praxis.

Do not commit.

Do not push.

Do not create remotes.

Do not promote RF-A0 to verified.

The objective is to make the existing RF-A0 bootstrap technically, experimentally and semantically stronger before its first governed commit.

---

# 2. Establish Fedora Linux as the reference experimental platform

The project currently reasons about Linux generically, while the experiment is actually executed on Fedora.

Make that distinction explicit.

Fedora Linux shall be the **reference execution and experimental platform** for SRF.

Linux kernel concepts remain the broader research subject, but RF-A0 must not generalize observations from Fedora to all Linux distributions without evidence.

Do not hard-code a Fedora release number into project identity.

Instead, collect the actual execution-platform baseline for every decisive RF-A0 verification.

At minimum, record read-only information sufficient to identify:

```text
distribution and release
kernel release
machine architecture
glibc version
selected C++ compiler identity and version
CMake version
Python version used by the gate
```

Reading `/etc/os-release` is permitted.

Do not edit `/etc`.

Do not install packages or mutate the host.

Generated evidence must make it possible to say:

> This RF-A0 observation was obtained on this Fedora userspace, this kernel, this libc and this toolchain.

Distinguish carefully between:

```text
Fedora property
Linux kernel property
glibc property
compiler/toolchain property
C++ language property
project observation
```

Do not attribute a behavior to “Linux” merely because it was observed once on Fedora.

---

# 3. Make C++23 an explicit technological contract

C++23 must be more than an incidental compiler flag.

At the same time, do NOT add C++23 features merely to demonstrate novelty.

The rule is:

> SRF application code is written against a C++23 language baseline. Linux/POSIX interfaces are used directly when those interfaces are themselves part of the runtime phenomenon under study.

Preserve explicit C++23 compilation.

Record enough build evidence to establish:

```text
selected compiler
compiler version
actual compile command
C++23 mode requested
C++ standard mode accepted
```

Inspect the current implementation and distinguish:

```text
C++ language facilities
C++ standard-library facilities
POSIX interfaces
Linux-specific interfaces
```

Document this distinction concisely for RF-A0.

Do not hide kernel semantics behind an unnecessary portability framework.

Do not require a C++23 library facility that RF-A0 does not actually need.

If a C++23 facility materially improves correctness, ownership, error handling or clarity, it may be adopted, but its use must be justified rather than decorative.

Where standard-library capability matters, test the exact capability actually required instead of assuming that “C++23 mode” implies complete library support.

No external C++ dependency may be added during this hardening pass.

---

# 4. Fix the signal/wait race

Audit the current relationship between:

```text
shutdown_signal
signal handler
poll(...)
controlled shutdown
```

The current design may contain a race in which a termination signal is handled after the loop condition is tested but before the blocking `poll()` begins.

Do not merely add a timeout to make the test usually pass.

Resolve the synchronization issue correctly.

Evaluate an appropriate Linux/POSIX mechanism such as:

```text
signalfd
self-pipe
ppoll with an atomic signal-mask transition
```

Choose the smallest mechanism whose correctness can be explained and tested.

Because Fedora/Linux is the reference platform, use of a Linux-specific primitive is acceptable when justified.

If `signalfd` is chosen, explicitly record that this is a Linux-specific process-interface choice rather than a portable C++ or generic POSIX property.

Extend the integration test and RF-A0 gate so the corrected shutdown behavior is exercised repeatedly enough to make the previously identified race meaningful to test.

Do not claim mathematical proof from stress testing.

Record the previous design assumption, the discovered counterexample window, the correction and the resulting learning.

---

# 5. Make prediction-before-observation auditable

The current learning record contains hypothesis, prediction and observation in the same synthesized artifact.

That does not independently demonstrate that the prediction existed before the decisive observation.

Strengthen the RF-A0 epistemic cycle.

Separate the pre-observation experimental protocol from post-observation synthesis.

The pre-observation record must contain, as appropriate:

```text
question
prior understanding
hypothesis
prediction
alternative explanation
falsification or contradiction condition
```

Before launching the decisive runtime observation, the experiment orchestrator must compute and record a SHA-256 digest of this pre-observation protocol.

Only after that point may decisive runtime observations be collected and the post-observation synthesis produced.

The generated evidence must preserve the protocol digest used for that run.

The post-observation record may then contain:

```text
observation
confrontation with prediction
interpretation
learning
confidence
candidate invariant or rule
governance consequence
open question
```

Do not claim that a checksum proves historical authorship.

It should prove only the narrower property that the exact pre-observation protocol used by the orchestrated run was fixed before that run collected its decisive observation.

Preserve this claim boundary explicitly.

---

# 6. Harden the forbidden-operation audit

The current gate performs useful forbidden-technology checks, but a negative keyword search alone is not a complete fail-closed execution policy.

Audit all project-owned executable scripts.

Establish an explicit allowlist for external commands that project-owned verification/evidence scripts are permitted to launch.

The allowlist should be minimal and derived from actual need.

Examples may include:

```text
cmake
ctest
git
the built srf-runtime-probe
```

Python itself is the executing interpreter and need not become an excuse for arbitrary subprocess execution.

If additional external programs are genuinely required, justify each one.

Where practical, statically inspect Python subprocess invocation sites and reject executable targets outside the allowlist.

Do not use `shell=True`.

Do not execute dynamically constructed shell command strings.

Account for the fact that CMake itself invokes the configured compiler as part of its legitimate build operation; distinguish project-script authority from child processes legitimately delegated to the build system.

The goal is not merely:

> forbidden words were not found.

The stronger goal is:

> project-controlled verification code has a bounded and inspectable external execution authority.

Document remaining limitations honestly.

---

# 7. Remove absolute external-input dependencies

The RF-A0 experiment currently refers to constitutive inputs through absolute user-directory paths.

That is insufficiently reproducible.

Make all inputs required to understand or reproduce RF-A0 self-contained or project-relative.

Do not copy implementation or governance artifacts from other repositories.

Project-specific constitutive texts supplied for SRF may be preserved as project inputs when necessary for reproducibility.

Use project-relative paths and checksums.

Do not make successful verification depend on files remaining in `~/Downloads` or another unrelated directory.

The project must be relocatable without changing the semantic identity of its governed inputs.

---

# 8. Characterize, but do not repair, the Praxis bootstrap gap

Do not modify Praxis.

Do not weaken its validator.

Do not invent a fake verified commit.

Do not fabricate successful validation.

Re-run the current applicable Praxis validators exactly as they exist.

Record the generic governed-project validator result as generated evidence, including the expected bootstrap failure if it remains:

```text
no previously verified milestone
no real verified commit
no valid ancestor commit
```

Review the current SRF state representation:

```text
last_verified_milestone: NONE
last_verified_commit: "0000000"
last_verified_gate: ...
last_verified_evidence: ...
```

Determine whether the latter two fields semantically imply a verified milestone even though the first two state that none exists.

Do not invent a new Praxis-wide representation.

Instead, document this precisely as a candidate:

```text
PRAXIS BOOTSTRAP REPRESENTATION GAP
```

Separate:

```text
schema validity
SRF internal consistency
Praxis governed-project validity
```

These are not synonyms.

A schema PASS must not be reported as a governed-project PASS.

---

# 9. Preserve and extend the learning loop

For every material correction in this hardening pass, use the same epistemic discipline already established by RF-A0:

```text
question
prior understanding
hypothesis
prediction
experiment or analysis
observation
confrontation
interpretation
learning
confidence
candidate rule
gate consequence
open question
```

In particular, synthesize the lessons from:

```text
signal/event waiting
Fedora-specific versus Linux-general claims
C++23 language mode versus library capability
prediction temporal ordering
bounded script execution authority
Praxis pre-history bootstrap
```

Do not convert every observation automatically into a universal invariant.

Rules must have an explicit evidence boundary.

---

# 10. Required final validation

Before stopping, run a clean RF-A0 validation cycle.

It must include:

```text
clean CMake configure
C++23 build
warnings-as-errors
CTest
RF-A0 gate
runtime evidence collection
evidence checksum verification
pre-observation protocol checksum verification
Fedora/toolchain baseline evidence
forbidden-operation audit
all applicable current Praxis validators
whitespace/integrity checks
Git state inspection
scope audit
```

Run from the actual existing SRF repository.

Do not hide failures.

A Praxis validator failure caused by the known bootstrap representation gap is not grounds for weakening the validator.

The final state must still have:

```text
RF-A0: active
RF-A1: unauthorized
no commits
no remotes
no push
no RF-A1 implementation
no Praxis modification
```

---

# 11. Final report

Report:

```text
1. What was changed and why
2. Fedora execution baseline actually observed
3. C++23/toolchain baseline actually observed
4. Signal-race analysis and resolution
5. Prediction-first evidence mechanism
6. External-execution authority audit
7. Input/provenance changes
8. Praxis bootstrap-gap characterization
9. New learning produced
10. Build and test results
11. RF-A0 gate result
12. Praxis validator results
13. Governance state
14. Git state
15. Remaining limitations
```

Clearly distinguish:

```text
PASS
EXPECTED FAIL-CLOSED
LIMITATION
NOT YET KNOWN
```

Do not begin RF-A1.

Do not commit.

Stop after RF-A0 hardening and validation.
