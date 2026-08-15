# Reflexive Bounded Autonomy

This section refines the operating model for the current RF-A0 hardening mission.

Its purpose is to grant Codex substantial engineering and experimental autonomy while preserving scientific control through observable state, evidence, invariants and reproducible validation.

## 1. Governing principle

Codex is not required to follow a predetermined implementation recipe.

Within the authorized milestone it may:

```text
inspect
hypothesize
design
implement
instrument
experiment
compare alternatives
reject an attempted solution
revert
refactor
strengthen tests
strengthen gates
discover unexpected behavior
revise a hypothesis
produce new candidate rules
```

without requesting step-by-step authorization.

Prefer:

> constrain properties and effects, not implementation creativity.

The project must therefore distinguish:

```text
freedom of method
from
authority over system boundaries
```

Codex has broad freedom of method.

Its authority over governed boundaries remains explicitly bounded.

---

# 2. Hard invariants

The following remain hard RF-A0 boundaries regardless of the implementation strategy selected:

```text
RF-A0 remains the only authorized milestone.

RF-A1+ behavior must not be implemented.

No privilege escalation.

No root requirement.

No sudo.

No persistent host mutation.

No manually-created isolation boundary belonging to later milestones.

No silent modification of Praxis.

No fabricated evidence.

No weakening of a gate merely to obtain PASS.

No claim stronger than the evidence.

No commit, push, remote creation or milestone promotion unless separately authorized.
```

These invariants govern effects, not individual AI behavior.

If an intended action would cross one of these boundaries, stop that action and report why.

Otherwise, continue autonomously.

---

# 3. Permission by class rather than command

Do not interpret this mission as requiring explicit permission for every command or implementation choice.

Read-only host observation, project-local reversible mutation, compilation, testing, instrumentation and unprivileged experimentation inside RF-A0 are generally authorized.

When multiple technically valid mechanisms exist, investigate and choose among them.

Examples in prior instructions such as:

```text
signalfd
self-pipe
ppoll
specific allowlist layouts
specific record layouts
```

are candidate approaches, not mandatory implementations unless a property explicitly requires them.

Choose the mechanism based on evidence, simplicity, correctness and explanatory value.

Record the reasoning for consequential choices.

---

# 4. Cybernetic experimental loop

Treat each material engineering problem as a feedback loop:

```text
INTENT
  ↓
CURRENT STATE
  ↓
HYPOTHESIS
  ↓
PREDICTION
  ↓
ACTION / EXPERIMENT
  ↓
OBSERVATION
  ↓
EXPECTED × OBSERVED COMPARISON
  ↓
INTERPRETATION
  ↓
LEARNING
  ↓
STATE / RULE / GATE UPDATE
  ↓
NEXT LOOP
```

The loop must be capable of producing:

```text
confirmation
correction
rejection
or
unresolved uncertainty
```

A failed hypothesis is a valid scientific result.

Do not optimize for PASS at the expense of learning.

---

# 5. Reflexive second-order loop

When an unexpected result occurs, do not assume that implementation is necessarily wrong.

Consider at least the following possible sources:

```text
implementation
hypothesis
experimental design
measurement instrument
environment assumption
test
gate
governance representation
conceptual model
```

The system must therefore support second-order questions such as:

```text
Did the experiment actually test the intended property?

Is the gate measuring what we think it measures?

Was an assumption incorrectly generalized?

Is the observed behavior Fedora-specific, kernel-specific,
toolchain-specific or project-specific?

Should an existing candidate rule be weakened, rejected or refined?

Did the method itself expose a limitation that belongs in Praxis learning?
```

Do not silently change a rule when evidence contradicts it.

Record the contradiction and resulting reasoning.

---

# 6. Automated Experimental Run Ledger

Create a minimal project-local mechanism that automatically records decisive experimental runs.

Do not manually fabricate generated run records.

The implementation and exact representation are yours to design.

Each decisive run should preserve enough information to reconstruct the causal chain between:

```text
starting state
epistemic commitment
action
observation
interpretation
validation
resulting state
```

At minimum, preserve machine-readable representations of:

```text
run identity

milestone / experiment identity

pre-run project state

relevant environment/toolchain identity

source or tree identity sufficient to identify what was executed

pre-observation question/hypothesis/prediction commitment

action or experiment performed

raw generated evidence

exit status and validation outcomes

unexpected observations

comparison of prediction and observation

post-run interpretation

candidate learning

post-run project state

evidence integrity digests
```

Avoid exhaustive shell-command surveillance.

Capture actions that are material to reproducing or interpreting the experiment.

Auditability is more important than volume.

---

# 7. Temporal epistemic commitment

The system should mechanically establish that the experimental prediction used by a decisive run was fixed before decisive observations from that run were collected.

You may design the mechanism.

A digest-based protocol commitment is one acceptable approach but not the only possible one.

The mechanism must not overclaim.

For example, a digest may demonstrate:

> these exact hypothesis/prediction bytes were fixed before this orchestrated observation.

It does not by itself prove:

```text
human authorship
historical originality
truth of the prediction
or absence of knowledge from prior unrelated observations
```

Preserve that epistemic boundary.

---

# 8. Evidence integrity chain

Investigate a simple mechanism for making sequential decisive run records tamper-evident.

A suitable model is a local hash chain in which each run incorporates an integrity reference to the previous accepted run.

Conceptually:

```text
H0 = genesis

H1 = HASH(H0 + canonical_run_1)

H2 = HASH(H1 + canonical_run_2)

H3 = HASH(H2 + canonical_run_3)
```

This is not a distributed ledger and requires no external service.

Its purpose is narrower:

> make retrospective alteration of recorded experimental history detectable by normal validation.

If a simpler mechanism provides the same required property, use it instead.

Do not introduce unnecessary dependencies.

---

# 9. Machine-readable gate results

Gates should produce machine-readable validation results in addition to concise human-readable output where practical.

For each material check, preserve:

```text
check identity
property being checked
input identity where relevant
result
evidence reference
failure reason when applicable
```

Prefer stable semantic identifiers such as:

```text
RF-A0.PROCESS.IDENTITY
RF-A0.FILE.OPEN_FD
RF-A0.NET.LOOPBACK_LISTENER
RF-A0.SIGNAL.CONTROLLED_SHUTDOWN
```

over validation logic that can only be understood by parsing prose.

A final PASS is meaningful only as the aggregation of individually inspectable claims.

---

# 10. Observation, inference and governance must remain distinct

Automated tooling must not collapse:

```text
raw observation
interpretation
conclusion
candidate rule
accepted governed invariant
```

into one category.

An observation may automatically be recorded.

An inference may automatically be proposed.

A candidate rule may automatically be generated.

Promotion into a stronger governed claim requires the evidence conditions defined by the project and Praxis.

The system should preserve provenance between these levels.

---

# 11. Unexpected-observation channel

Every decisive experiment must be able to record findings that were not part of its initial prediction.

Unexpected observations must not be discarded merely because the primary test passed.

Classify them as appropriate:

```text
anomaly
new question
possible confounder
possible implementation issue
possible methodological issue
candidate new experiment
```

Do not automatically expand milestone scope because an anomaly is interesting.

Record it for later investigation when it belongs outside RF-A0.

---

# 12. Reversibility

Project-local experimentation should favor reversible operations.

Before a consequential mutation, the system should know enough about the current state to determine what changed afterward.

Use project state and source identity rather than relying on agent memory.

A failed experiment may be reverted without being erased from the experimental learning record.

Failure history is part of the evidence when it materially changed understanding.

---

# 13. AI-independent control

Do not rely on Codex remembering constraints or voluntarily describing every relevant event.

Where a property materially affects governance, prefer enforcement or observation by independent project tooling.

The architecture should tend toward:

```text
agent proposes or acts

system observes

gate evaluates

evidence persists

governance interprets
```

rather than:

```text
agent acts

agent states that everything was correct
```

The same control model should work regardless of whether the implementation is produced by:

```text
Codex
ChatGPT
a human developer
another automated agent
```

This project governs engineering state and evidence, not trust in a particular intelligence.

---

# 14. Relationship to Praxis

Praxis remains the external governed-engineering method.

SRF may develop project-local experimental instrumentation needed to study runtime foundations.

Do not silently promote project-local mechanisms into Praxis standards.

However, when SRF discovers a methodological limitation or useful generalization, record it as a candidate methodological learning with:

```text
triggering observation
evidence
scope
proposed generalization
known counterexamples or limitations
```

Only a separate governed Praxis evolution may later adopt it.

Thus the intended virtuous cycle is:

```text
SRF experiment
      ↓
observation
      ↓
learning
      ↓
project-local consequence
      ↓
candidate methodological lesson
      ↓
Praxis evaluation
      ↓
possible generalized rule
      ↓
future governed projects
```

---

# 15. Stopping rule for this mission

Continue autonomously inside RF-A0 until one of these conditions holds:

```text
the RF-A0 hardening objectives are demonstrably satisfied;

a hard invariant would need to be crossed;

the next meaningful experiment belongs to RF-A1 or later;

a discovered Praxis issue requires modifying Praxis;

a result cannot be honestly resolved with the available evidence.
```

Do not stop merely because the first implementation passes.

Do not continue merely to produce more activity after the experimental question is sufficiently answered.

At completion, report the knowledge gained, not only the files changed.
