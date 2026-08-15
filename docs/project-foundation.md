# Project foundation

## Identity and purpose

- Name: SisTer Runtime Foundations
- Repository: `sister-runtime-foundations`
- Short name: SRF
- Subtitle: From Bare Metal to Governed Containers
- Language: C++23
- Reference execution and experimental platform: Fedora Linux
- Reference system: SisTer
- Methodology: Praxis Governed Engineering 0.1

Central research question:

> What constitutes, in Linux, the necessary and sufficient runtime environment
> for executing SisTer-class software with explicit, reproducible, and
> governable process, filesystem, resource, network, persistence, and security
> boundaries?

This project is built from first principles. Requirements may be learned from
Praxis and, later, from SisTer, but implementation and governance are authored
for SRF rather than copied from another repository.

## Architecture is not containerization

An application is implemented software. An executable is a filesystem artifact.
A process is a running kernel-managed instance. A service is an operational role
with lifecycle expectations. Filesystems, namespaces, cgroups, networks, and
persistent state are distinct runtime concerns. A runtime establishes and
manages some of those concerns. A container is one possible mechanism and a
deployment is a placement/configuration decision.

None of these concepts is modeled as a synonym for another, and no architecture
decision in RF-A0 assumes future containerization. In particular, a container
is not a domain system, subsystem, module, or service.

## Roadmap and authority

| Milestone | Subject | State | Authorized |
|---|---|---|---|
| RF-A0 | Native Linux Process | active | yes |
| RF-A1 | Filesystem Semantics | unimplemented | no |
| RF-A2 | Linux Namespaces | unimplemented | no |
| RF-A3 | Resource Governance / cgroup v2 | unimplemented | no |
| RF-A4 | Network Isolation | unimplemented | no |
| RF-A5 | Privilege & Security Boundaries | unimplemented | no |
| RF-A6 | Raw Linux Container | unimplemented | no |
| RF-A7 | Runtime Reconstruction with Podman | unimplemented | no |
| RF-A8 | SisTer Deployment Model | unimplemented | no |
| RF-A9 | Praxis Runtime Governance | unimplemented | no |

The table records questions, not implementation promises. Only an explicit
future authorization can activate a later milestone.

## Governance bootstrap boundary

Praxis 0.1 requires the canonical state to name last-verified milestone, commit,
gate, and evidence provenance, but this repository begins without a commit and
the mission forbids creating one. The canonical state therefore uses `NONE` for
milestone, gate, and evidence plus `0000000` for commit as honest bootstrap
sentinels while RF-A0 remains active. They conform structurally to the current
schema but are not claimed as canonical Praxis vocabulary or as verification.
The generic Praxis validator rejects this pre-history state; SRF preserves that
expected fail-closed result and does not fabricate ancestry.

Schema validity, SRF internal consistency, and Praxis governed-project validity
are reported separately.

## Safety and reversibility

RF-A0 runs without elevated privilege and confines generated data to ignored
build directories plus the declared evidence directory. It changes no host
configuration. Future privileged experiments must be separately authorized,
state their predicted host effects, use the narrowest reversible operation,
capture before/after evidence, define cleanup before execution, and stop if
cleanup or scope cannot be established. No such future experiment is authorized
here.
