# RF-A0 learning synthesis

This synthesis interprets the generated RF-A0 evidence within its declared
boundary. Exact runtime values remain in `docs/experiments/evidence/rf-a0/`;
the structured learning cycles and their historical predictions remain in
`.hoa/learning/rf-a0.json`.

## What we knew before RF-A0

The initial model expected an ordinary child to receive a live process identity,
inherit launcher credentials and runtime memberships unless something changed
them, hold files and sockets as descriptors, and be able to turn SIGTERM into a
controlled shutdown. It also treated the executable, process, pathname,
descriptor, application, and listening port as related but distinct concepts.

These were hypotheses and prior understanding, not RF-A0 evidence.

## What RF-A0 directly demonstrated

In the recorded environment:

- probe output, the child handle, `/proc/<pid>/status`, and `/proc/<pid>/exe`
  agreed on the child/launcher identity, credentials, and executable;
- a live descriptor resolved to the regular file retained by the probe;
- a second descriptor exposed a socket inode that matched a TCP LISTEN row at
  `127.0.0.1:<selected-port>`, and a loopback connection succeeded;
- launcher and child namespace links matched for every type compared;
- launcher and child cgroup records matched byte-for-byte;
- process maps and mount information were readable and nonempty;
- SIGTERM produced an explicit controlled-shutdown record, zero exit, and no
  forced kill.

## What changed in our understanding

The runtime hypotheses were supported, not corrected. Their claim boundaries
became sharper: namespace and cgroup evidence is relational to the launcher;
loopback reachability is supported by correlated binding evidence rather than
assumed isolation; a path or printed port is insufficient without live kernel
state; and controlled shutdown requires more evidence than disappearance.

One methodological assumption was corrected. The first observer assumed that a
kernel-level selector could safely be interleaved with `TextIOWrapper.readline()`.
A direct capture showed the probe had emitted output while unread lines remained
only in the wrapper's user-space buffer. The observer now uses byte-level reads.

## What became governed knowledge

The six candidate rules in the learning record were accepted as project-local
RF-A0 gate obligations because each corresponds to a focused, supported
prediction and a mechanically checkable correlation. The gate now protects:

- process/executable/launcher identity correlation;
- live regular-descriptor correlation;
- loopback socket descriptor/inode/TCP-row/connection correlation;
- launcher/child namespace comparison with a relative claim boundary;
- launcher/child cgroup comparison without a resource-governance claim;
- bounded SIGTERM shutdown without forced termination.

No new Praxis-wide schema or rule was proposed. The learning artifact remains
project-local because Praxis 0.1 has no canonical learning-record contract.

## Negative knowledge

RF-A0 rejects these misleading models within the demonstrated boundary:

- an executable is not itself a process;
- a pathname does not prove that a process holds an open file;
- a printed port does not prove a live listening socket;
- matching namespace membership does not mean namespaces are absent;
- cgroup membership does not mean this project configured resource governance;
- loopback binding does not constitute network isolation;
- containerization is not required for the native process properties observed.

It does not establish that PIDs are stable across namespace contexts; RF-A0 did
not vary that context.

## What remains uncertain

RF-A0 does not determine filesystem-isolation semantics, effects of namespace
creation, cgroup controllers or limits, network isolation, privilege/security
boundaries, persistence behavior, container behavior, operational readiness, or
verified SisTer deployment requirements.

## What RF-A0 does not establish

The evidence does not demonstrate filesystem, network, resource, privilege, or
security isolation. It does not demonstrate a container or an unnamespaced
global host view. It does not show that any cgroup was configured by SRF. It
does not generalize one environment's numeric IDs, paths, namespace identifiers,
cgroup path, mappings, mounts, or ephemeral port to other executions.

## Questions handed to RF-A1

If RF-A1 is later authorized, focused questions include:

- Which pathname properties persist after an already-open file is renamed or
  unlinked?
- Which working-directory and relative-path relationships are process state?
- Which mount-table observations describe filesystem view without introducing
  isolation?
- How should file ownership, modes, and persistence be varied one at a time?

These questions do not authorize RF-A1.

## Dispositions

- Assumptions confirmed: process identity correlation, live FD observability,
  explicit loopback listener observability, inherited launcher-relative
  memberships, and controlled SIGTERM shutdown.
- Assumptions corrected: the original Python selector/text-buffer observer was
  not a reliable line-framing strategy.
- Assumptions rejected: none of the six pre-recorded Linux runtime hypotheses.
- Unexpected observations: one warnings-as-errors conversion defect and one
  evidence-observer buffering defect; neither was silently patched around.
- Candidate invariants accepted: the six scoped gate obligations listed above.
- Candidate invariants rejected or deferred: all RF-A1+ semantic rules, any
  global PID/namespace claim, any isolation claim, and any verified SisTer
  deployment requirement.
