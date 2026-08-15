# Mission: Bootstrap SisTer Runtime Foundations from First Principles

We are starting a new governed engineering project from zero.

## Project identity

Create the project at:

```text
/run/media/jpereiratrindade/labeco10T/dev/cpp/sister-runtime-foundations
```

Canonical identity:

```text
name: SisTer Runtime Foundations
repository: sister-runtime-foundations
short_name: SRF
subtitle: From Bare Metal to Governed Containers
language: C++23
reference_system: SisTer
methodology: Praxis
```

The central research question is:

> What constitutes, in Linux, the necessary and sufficient runtime environment for executing SisTer-class software with explicit, reproducible and governable process, filesystem, resource, network, persistence and security boundaries?

The guiding principle is:

> We do not begin with containers. We begin with a Linux process and earn every boundary.

---

# NON-NEGOTIABLE CONSTRAINTS

This project must be built from first principles.

Do NOT copy implementation, directory structure, manifests, CMake files, tests, documentation, scripts or governance artifacts from SisTer, SisTer Atmos, SisTer Infra, Praxis reference projects, or any other repository.

Reading existing repositories to understand requirements and the current Praxis method is permitted.

Copying their implementation is not.

## Reference repositories

Praxis:

```text
/run/media/jpereiratrindade/labeco10T/dev/cpp/Praxis
```

SisTer:

```text
/run/media/jpereiratrindade/labeco10T/dev/cpp/SisTer
```

Use Praxis as the authoritative source for the CURRENT governed engineering method.

Use SisTer only as a reference system whose runtime requirements may later be studied.

Do not assume the current Praxis schemas, commands, manifest names, statuses or directory structure from prior knowledge.

Inspect the current Praxis repository and discover the actual contracts and validators before designing governance artifacts.

Do not copy another governed project's `.hoa` or equivalent governance tree.

Construct only the minimum artifacts required by the current Praxis method.

---

# ARCHITECTURAL PRINCIPLE

Containerization is a deployment/runtime mechanism.

It is NOT a domain identity.

Do not model a container as a system, subsystem, module or service.

The project must maintain explicit conceptual separation among at least:

```text
application
process
service
filesystem
namespace
cgroup
network
persistent state
runtime
container
deployment
```

No architecture decision may depend on the assumption that software will eventually be containerized.

---

# PROJECT ROADMAP

Record the following long-term roadmap, but DO NOT implement future milestones.

```text
RF-A0 — Native Linux Process
RF-A1 — Filesystem Semantics
RF-A2 — Linux Namespaces
RF-A3 — Resource Governance / cgroup v2
RF-A4 — Network Isolation
RF-A5 — Privilege & Security Boundaries
RF-A6 — Raw Linux Container
RF-A7 — Runtime Reconstruction with Podman
RF-A8 — SisTer Deployment Model
RF-A9 — Praxis Runtime Governance
```

Only RF-A0 is authorized in this mission.

All later milestones must remain explicitly unimplemented and unauthorized.

---

# FORBIDDEN IN THIS MISSION

Do NOT:

- use Docker;
- use Podman;
- use containerd;
- create a Containerfile or Dockerfile;
- use Compose;
- use Kubernetes;
- create network namespaces;
- create PID namespaces;
- invoke `unshare`;
- invoke `nsenter`;
- configure cgroups;
- create veth interfaces;
- alter routing;
- alter NAT;
- alter firewall configuration;
- mount OverlayFS;
- use `chroot`;
- edit `/etc`;
- modify persistent host configuration;
- require root privileges;
- execute `sudo`;
- copy code from SisTer;
- copy governance artifacts from another project;
- implement RF-A1 or later milestones;
- commit;
- push;
- create remote repositories;
- promote RF-A0 to verified merely because the implementation builds.

If any current Praxis requirement conflicts with this mission, report the conflict rather than silently weakening either Praxis or these constraints.

---

# RF-A0 — NATIVE LINUX PROCESS

## Research question

Answer experimentally:

> What is a SisTer-class application process from the Linux kernel's point of view before any containerization or manually-created isolation boundary exists?

## Experimental object

Create a new, minimal C++23 executable designed specifically for this project.

A suitable conceptual name is:

```text
srf-runtime-probe
```

This is NOT a reduced copy of `sisterd`.

Design it from scratch.

It should provide enough observable behavior to investigate a native Linux process.

At minimum, it should be able to expose or allow observation of:

```text
PID
PPID
UID
GID
current working directory
selected process environment information
open file descriptors
a regular file opened by the process
a TCP listening socket bound explicitly to loopback
signal handling
controlled shutdown
```

Prefer Linux/POSIX primitives directly where they are relevant to the experiment.

Keep dependencies minimal.

Do not introduce a framework unless experimentally justified.

---

# REQUIRED RF-A0 OBSERVATIONS

The RF-A0 experiment must inspect the native process from the host using Linux interfaces such as:

```text
/proc/<pid>/status
/proc/<pid>/fd
/proc/<pid>/maps
/proc/<pid>/mountinfo
/proc/<pid>/ns
/proc/<pid>/cgroup
```

Also record enough information to establish the relationship between:

```text
executable
process
PID
file descriptors
socket
filesystem view
namespace membership
cgroup membership
```

Do NOT artificially isolate any of those properties yet.

RF-A0 is specifically the baseline before isolation.

---

# SCIENTIFIC DISCIPLINE

RF-A0 must distinguish:

```text
observation
inference
conclusion
```

Do not claim more than the evidence demonstrates.

In particular, RF-A0 must NOT claim that:

- namespaces have been understood experimentally;
- containers have been implemented;
- filesystem isolation exists;
- network isolation exists;
- resource isolation exists;
- cgroups have been configured by this project;
- security isolation has been achieved.

Those belong to later milestones.

---

# GOVERNANCE

Before creating project governance artifacts:

1. inspect the current Praxis repository;
2. identify the current canonical project-state contract;
3. identify the current experiment/milestone contract;
4. identify the relevant validation commands;
5. determine the minimum valid governed-project structure.

Then create a clean governance structure for this project.

Do not cargo-cult another repository.

The governance state must make clear that:

```text
RF-A0 is the only authorized active milestone
RF-A1 and later are not authorized
```

Use the actual current Praxis vocabulary and schema if it differs from the terminology in this prompt.

The schema and validators in the current Praxis repository are authoritative for representation.

The semantic constraints in this mission are authoritative for project intent.

---

# REQUIRED DOCUMENTATION

Create only documentation that has a clear function.

At minimum, capture:

1. project identity and purpose;
2. central research question;
3. first-principles policy;
4. distinction between architecture and containerization;
5. roadmap RF-A0 through RF-A9;
6. RF-A0 experiment specification;
7. initial architecture of the runtime probe;
8. evidence policy;
9. safety/reversibility policy for future privileged experiments.

Do not produce large speculative architecture documents for milestones that have not been executed.

---

# BUILD QUALITY

The project must use C++23 explicitly.

Establish a minimal native build and test path.

Prefer:

```text
CMake
CTest
warnings as errors
```

where supported by the current environment.

Do not add external dependencies unless necessary.

Do not pretend unsupported standard-library facilities are available.

Detect capabilities where appropriate.

The build should remain small enough that its purpose is obvious.

---

# RF-A0 GATE

Create an RF-A0 verification gate that proves at least:

```text
project governance is internally consistent;
C++23 build succeeds;
tests pass;
runtime probe starts correctly;
probe exposes the required native-process behavior;
the process can be identified externally;
required /proc observations can be collected;
the loopback listening socket is observable;
signal-driven shutdown behaves correctly;
no forbidden container/runtime technology was introduced;
no manually-created namespace isolation was introduced;
no privileged host mutation is required;
no code was copied from SisTer.
```

Where a property cannot be mechanically proven, document the limitation rather than fabricating a check.

The gate must fail closed.

Do not implement a gate that merely prints PASS without verifying the corresponding property.

---

# EVIDENCE

Runtime-generated evidence must be clearly distinguished from source-controlled specifications.

Evidence should be reproducible.

If the current Praxis method prescribes a canonical evidence structure, follow it.

Do not fabricate evidence.

Do not hand-write output that is supposed to have been produced by execution.

---

# GIT DISCIPLINE

If the target directory does not exist, create it and initialize a Git repository if appropriate.

Do not create remotes.

Do not push anything.

Do not commit anything during this mission.

Leave all created files inspectable in the working tree so they can be reviewed before the first commit.

Do not create future feature branches.

---

# REQUIRED VALIDATION

Before stopping:

1. run the project's own configure/build/test flow;
2. run the RF-A0 gate;
3. run every applicable current Praxis governed-project validator against the new repository;
4. run `git diff --check` or the appropriate equivalent;
5. inspect the final Git working tree;
6. verify that no forbidden technologies or premature RF-A1+ implementation entered the repository.

If Praxis validation cannot pass because the current method requires something incompatible with this deliberately minimal bootstrap, stop and explain the exact incompatibility.

Do not weaken Praxis validation merely to obtain PASS.

---

# FINAL RESPONSE

When finished, report concisely:

## 1. Praxis discovery

What current Praxis contracts and validators were actually found and used.

## 2. Files created

Group by purpose rather than dumping an unstructured file list.

## 3. RF-A0 implementation

Explain exactly what the runtime probe does.

## 4. Evidence

State what was actually observed from Linux and where the evidence resides.

## 5. Validation results

Report actual build, CTest, RF-A0 gate and Praxis validator results.

## 6. Governance state

State the actual current milestone, status and authorization of the next milestone.

## 7. Scope audit

Explicitly confirm whether any Docker, Podman, containerd, Compose, Kubernetes, `unshare`, `chroot`, OverlayFS, cgroup manipulation, network namespace or privileged host mutation entered the project.

## 8. Git state

Show branch, status and confirm that no commit or push was performed.

## 9. Deviations

List every deviation from this mission, if any.

Do not begin RF-A1.

STOP after RF-A0 bootstrap and validation.
