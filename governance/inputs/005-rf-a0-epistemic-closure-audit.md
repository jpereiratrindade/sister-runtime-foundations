# Codex Mission — RF-A0 Epistemic Closure Audit

**Project:** Sister Runtime Foundations
**Phase:** RF-A0
**Mission type:** Epistemic closure audit
**Reference platform:** Fedora Linux
**Application language baseline:** C++23
**Current governed state:** `RF-A0 active`
**Promotion authority:** not granted
**RF-A1 authority:** not granted

---

## 1. Mission purpose

RF-A0 has already produced sufficient evidence for its **technical hardening**.

The current mission is **not** to expand the Linux experiment, add functionality, redesign the runtime probe, improve signal handling further, or begin RF-A1.

The purpose of this mission is narrower:

> **Audit and, where necessary, repair the causal fidelity of RF-A0's experimental evidence and reflexive recording mechanisms before RF-A0 is considered epistemically ready for later governance closure.**

The governing principle is:

> **Freedom to discover means; rigor in demonstrating properties, preserving causal boundaries, and recording evidence honestly.**

Do not optimize for producing another green gate.

Optimize for making the experimental record faithfully express:

1. what was predicted;
2. what was actually observed;
3. what evidence supports each observation;
4. what comparison can legitimately be made;
5. what remains inconclusive;
6. what was unexpected;
7. what may be learned from the observations;
8. what remains outside the authority of this project.

---

# 2. Current state that must be preserved

Treat the following as the starting scientific and governance state.

RF-A0 currently has:

- native Linux runtime experiment implemented;
- Fedora as explicit experimental reference platform;
- C++23 language baseline checked;
- signal handling implemented with Linux `signalfd`;
- direct project subprocess execution centralized under default-deny authority;
- prediction-first experimental commitment;
- machine-readable gate results;
- hash-chained run ledger;
- three existing experimental runs;
- Praxis validation intentionally failing closed for the current bootstrap representation;
- no prior verified milestone;
- no Git commit;
- no Git remote;
- RF-A0 active and authorized;
- RF-A1 through RF-A9 unauthorized and unimplemented.

The canonical governance state must remain semantically equivalent to:

```text
phase: RF-A0
status: active

last_verified_milestone: NONE
last_verified_commit: 0000000
last_verified_gate: NONE
last_verified_evidence: NONE

next_milestone: RF-A0
next_milestone_status: active
next_milestone_authorized: true
```

Do not convert successful checks into a verified milestone.

Do not promote RF-A0.

Do not authorize RF-A1.

---

# 3. Existing evidence is historical record

The three existing RF-A0 runs and their ledger are historical experimental evidence.

They must be treated as immutable observations.

In particular:

- do not edit existing run records;
- do not rewrite their commitments;
- do not regenerate them;
- do not recompute their ledger entries;
- do not silently migrate their schema;
- do not normalize or rewrite their JSON merely for formatting;
- do not alter historical hashes;
- do not reinterpret old observations by modifying their stored contents.

The existing ledger head must remain independently verifiable.

Current known historical ledger state:

```text
runs: 3
head:
fc6d758e6a04d07451b9d86af45be1ef33b23d61731c124ee0140b1e72894fcc
```

The current committed RF-A0 protocol digest associated with those runs is:

```text
cba33aabff5e45d499f097bac16bda6fb33cef5add32924d906be89bda074e40
```

The mission may extend the evidence system prospectively.

It must not rewrite its past.

---

# 4. Technical hardening is not the subject of this mission

Assume the current RF-A0 technical hardening to be sufficiently demonstrated unless this audit uncovers direct evidence to the contrary.

Do not proactively replace or redesign:

- `signalfd`;
- the listener/event loop;
- the existing C++23 runtime probe;
- the Fedora baseline;
- the compiler warning baseline;
- signal stress testing;
- existing build mechanics;
- the execution-authority architecture;
- the current Linux/POSIX boundary.

A technical change is permitted only if required to repair a defect directly affecting the epistemic integrity of the experimental record.

If such a defect is discovered, document why the technical change was necessary.

Do not perform unrelated cleanup.

---

# 5. Primary audit questions

Investigate the following issues as hypotheses about the evidence mechanism.

Do not assume in advance that every suspected defect is real.

For each one:

1. inspect the implementation;
2. determine whether the concern is confirmed, partially confirmed, or rejected;
3. record the basis for that conclusion;
4. repair it only if justified by evidence.

---

## 5.1 External identities must be observed, not asserted

Audit all material external identities recorded by RF-A0.

In particular, investigate whether the Praxis identity used by the experiment is currently represented by a hardcoded value such as a commit SHA rather than being measured from the Praxis instance actually invoked.

The epistemic requirement is:

> A run must not claim that an external artifact had a particular identity merely because that identity was written into RF-A0 source code.

Where an external dependency materially affects an observation, record sufficient read-only evidence to identify the actual dependency used.

For Praxis, the evidence should be sufficient to distinguish at least:

- the Praxis repository state actually observed;
- the validator actually executed;
- the methodology contracts or schemas actually consulted.

Possible observations may include, where useful:

```text
Praxis Git HEAD
validator content digest
schema/content digests
repository cleanliness or relevant Git state
```

These are examples, not mandatory implementation recipes.

Choose the simplest representation that establishes the property.

Do not modify Praxis during this mission.

Do not use observations of Praxis as an excuse to create authority over Praxis.

---

# 6. Prediction comparison must be causal and hypothesis-specific

Audit the production of `prediction_comparisons`.

A global gate result must not automatically imply that every individual hypothesis was supported.

The desired causal structure is:

```text
protocol prediction
        ↓
relevant observation/check/evidence
        ↓
comparison
```

not:

```text
global gate PASS
        ↓
all predictions SUPPORTED
```

Each prediction or pre-observation commitment must be independently comparable against the evidence that is relevant to it.

The comparison vocabulary should preserve distinctions equivalent to:

```text
SUPPORTED
CONTRADICTED
INCONCLUSIVE
```

Additional states may be introduced only if they express a genuinely necessary semantic distinction.

A prediction must not become `SUPPORTED` merely because unrelated checks passed.

A prediction must be capable of being contradicted while other predictions remain supported.

A prediction must be capable of remaining inconclusive while the overall run continues successfully.

The machinery should preserve traceability from:

```text
prediction
→ observation(s)
→ check(s)
→ evidence artifact(s)
→ comparison
```

Avoid unnecessary complexity.

The objective is causal traceability, not a large framework.

---

# 7. Unexpected observations must be an operational channel

Audit `unexpected_observations`.

A field that is structurally present but always populated with a hardcoded empty list is not yet a fully operational observational channel.

RF-A0 should be capable of representing an unexpected observation when the run itself reveals one.

Examples of the semantic class include:

- anomaly;
- confounder;
- contradiction;
- unexpected environment property;
- unexpected tool behavior;
- partial observation;
- unexpected dependency state;
- evidence-generation failure that does not justify pretending the observation never occurred.

Do **not** invent unexpected observations to exercise the mechanism.

An empty list is correct when nothing unexpected was observed.

The requirement is merely that emptiness result from the observation process rather than from an implementation that is incapable of recording anything else.

---

# 8. Observation and learning must remain different layers

Audit `candidate_learning` and related learning artifacts.

Preserve a strict semantic distinction among:

```text
prediction
observation
comparison
interpretation
candidate learning
governance adoption
```

Machine observations may justify comparisons.

Comparisons may motivate candidate learning.

But a run must not mechanically claim that a scientific or methodological lesson has been learned merely because the gate passed.

Candidate learning must remain explicitly distinguishable from:

- raw observation;
- automatic check result;
- prediction comparison;
- established project rule;
- adopted Praxis rule.

Where learning requires interpretation rather than direct measurement, represent that fact honestly.

Do not fabricate autonomous epistemic authority for the machine.

The system may produce evidence-backed **candidate learning**.

It must not silently transform candidate learning into governance law.

---

# 9. Preserve protocol history by content

The existing RF-A0 runs refer to a protocol by SHA-256.

That is necessary but may not be sufficient for long-term reconstructibility if the repository has no Git history and the current protocol file is later replaced.

Establish a prospective mechanism ensuring:

> The exact bytes of every protocol used for an experimental commitment remain recoverable after future protocol revisions.

The mechanism may use, for example:

- content-addressed archival copies;
- immutable protocol versions;
- exact protocol snapshots stored with future runs;
- another simple auditable design.

The implementation method is intentionally not prescribed.

The required properties are:

1. the exact committed bytes can later be recovered;
2. their digest can be independently recomputed;
3. historical runs remain associated with the exact protocol they used;
4. revising the current protocol does not erase previous experimental commitments.

Do not retroactively alter the three historical runs.

If preservation of the existing historical protocol requires creating a separate archival copy of its current exact bytes, that is permitted only if:

- the bytes are preserved exactly;
- the existing runs themselves remain unchanged;
- the existing ledger is not recomputed;
- the new archival fact is clearly distinguishable from evidence that existed at the time of those runs.

---

# 10. Preserve H06 as historical experimental context

The current protocol includes an expectation concerning the unchanged Praxis validator.

For this mission, keep that expectation unchanged.

The expected result remains semantically:

```text
Praxis current validator
        ↓
current SRF bootstrap state
        ↓
EXPECTED_FAIL_CLOSED
```

Do not modify Praxis to make the validator accept RF-A0.

Do not weaken SRF evidence merely to make Praxis accept it.

Do not change H06 merely because the current outcome is inconvenient.

The fail-closed result is presently an observation of a methodology/bootstrap representation gap.

It is not a failure of this mission.

---

# 11. Praxis bootstrap gap remains outside SRF adoption authority

The existing candidate concerning the Praxis bootstrap representation gap may be preserved and improved as evidence-backed candidate learning.

However:

- SRF has no authority to change Praxis methodology;
- SRF must not patch Praxis;
- SRF must not vendor a modified Praxis validator;
- SRF must not create a local compatibility fork and present it as Praxis;
- SRF must not reinterpret `FAIL` as `PASS`;
- SRF must not fake a prior verified milestone.

The correct boundary is:

```text
SRF observes
      ↓
SRF records candidate methodological learning
      ↓
Praxis may later evaluate that learning
```

not:

```text
SRF observes
      ↓
SRF modifies Praxis
      ↓
SRF validates itself
```

---

# 12. Second-order experimental consequence

Preserve explicitly the fact that H06 belongs to the currently observed Praxis state.

If Praxis is modified in a future, separately governed mission, the old H06 observation must remain historical evidence.

A future return to SRF must use a new pre-observation commitment appropriate to the new Praxis state.

Conceptually:

```text
Praxis state P1
      ↓
H06-v1
      ↓
EXPECTED_FAIL_CLOSED
      ↓
candidate methodological learning
      ↓
Praxis separately evolves to P2
      ↓
new SRF protocol commitment
      ↓
H06-v2
      ↓
new observation
```

Do not reinterpret an observation under Praxis state `P1` as though it had occurred under state `P2`.

This distinction is part of RF-A0's experimental history.

---

# 13. Autonomy model

You have broad autonomy over implementation details.

You may:

- inspect all project files;
- simplify evidence machinery where simplification improves truthfulness;
- refactor RF-A0-specific evidence code;
- introduce small machine-readable structures;
- add focused tests;
- add focused verification checks;
- derive evidence mappings dynamically;
- improve naming where current names imply stronger claims than the evidence supports;
- design the protocol-preservation mechanism;
- design the hypothesis-to-evidence mapping;
- discover additional epistemic defects directly related to this mission.

Do not ask for permission for ordinary local implementation choices.

Prefer discovering the smallest sufficient mechanism experimentally.

However, autonomy is bounded by effects.

You may **not**:

- modify Praxis;
- create or alter Git remotes;
- commit;
- push;
- promote RF-A0;
- authorize RF-A1;
- implement RF-A1 behavior;
- introduce containers, VMs, sandbox frameworks, or unrelated isolation technology;
- copy implementation from SisTer, Praxis, or another project;
- manufacture historical evidence;
- change historical run contents;
- weaken a failing check to obtain a green result;
- turn an observation into an adopted methodological rule without authority.

---

# 14. Reflexive development loop

Use the following loop during this mission:

```text
question
   ↓
preliminary hypothesis
   ↓
inspect current mechanism
   ↓
predict consequence
   ↓
make minimal change if justified
   ↓
observe
   ↓
compare prediction with evidence
   ↓
record unexpected observations
   ↓
extract candidate learning
   ↓
strengthen or revise mechanism
```

The loop may repeat.

Do not preserve a design simply because it was previously written.

Do preserve evidence of what actually happened.

When a proposed improvement fails, treat that as information.

Do not hide failed attempts that materially change the interpretation of the final result.

---

# 15. Evidence must remain stronger than narrative

Prefer machine-readable evidence over prose assertions where practical.

Narrative documentation may explain evidence.

It must not substitute for evidence that can reasonably be measured automatically.

For material claims, seek a structure equivalent to:

```text
claim
 ↓
observation
 ↓
machine-readable artifact
 ↓
independent verification
```

Examples:

```text
external validator identity
→ observed repository/artifact identity
→ machine-readable evidence
```

```text
prediction Hxx supported
→ relevant check results
→ explicit evidence references
```

```text
historical protocol reconstructible
→ exact bytes archived
→ digest verification
```

The exact schemas and filenames are implementation choices unless constrained by existing project contracts.

---

# 16. Do not confuse checks, evidence, verification, and promotion

Maintain these distinctions:

```text
check PASS
≠ experiment verified

experiment evidence valid
≠ milestone promoted

Praxis schema valid
≠ governed project valid

SRF internally consistent
≠ Praxis accepts bootstrap representation

technical hardening complete
≠ RF-A0 complete
```

The phrase:

> **RF-A0 technical hardening complete**

is acceptable if still supported by the evidence after this audit.

Do **not** claim:

> **RF-A0 complete**

during this mission.

---

# 17. Testing strategy

Add only the tests necessary to demonstrate the properties changed by this mission.

The test strategy should be capable of detecting regressions such as:

- hardcoded external identity masquerading as observation;
- global gate PASS causing all hypotheses to become automatically supported;
- inability to represent an unexpected observation;
- learning emitted independently of supporting evidence;
- loss of reconstructibility after protocol revision;
- mutation of historical run records;
- mutation or recomputation of the existing ledger;
- accidental RF-A0 promotion;
- accidental RF-A1 authorization;
- accidental modification of Praxis.

Do not create artificial complexity merely to increase check counts.

The number of PASS checks is not a success metric.

Truthfulness of the experimental record is.

---

# 18. Historical integrity check

Before making changes, establish the observable integrity of the existing three-run chain.

After implementation, demonstrate that the historical chain still verifies unchanged.

Where practical, preserve an audit record sufficient to show that:

```text
historical run contents before
==
historical run contents after
```

for the immutable evidence set.

At minimum, independently verify:

- number of historical runs;
- existing ledger head;
- historical run hashes;
- existing protocol digest associations.

Do not rely exclusively on Git for this check because the repository currently has no commit history.

---

# 19. New decisive observation

Execute a new decisive RF-A0 observation only if necessary to demonstrate the repaired epistemic mechanism.

If a new run is generated, it must:

- use a prediction-first commitment;
- preserve the current H06 expectation;
- observe the actual external Praxis identity;
- compare predictions individually;
- support operational unexpected observations;
- preserve the observation/interpretation/learning distinction;
- use the new protocol-preservation mechanism;
- append to history without rewriting existing history.

A new run should extend the evidence chain prospectively.

It must not replace the previous runs.

---

# 20. Expected Praxis result

During this mission, the unchanged Praxis governed-project validator is still expected to fail closed against the current uncommitted bootstrap state.

The desired classification remains:

```text
EXPECTED_FAIL_CLOSED
```

provided that this classification is justified by the actual observed validator result.

Do not convert an unexpected Praxis result into the expected classification.

If Praxis unexpectedly passes, crashes, changes identity, produces a different error, or otherwise behaves differently from the prediction:

1. record the actual observation;
2. classify the relevant prediction accordingly;
3. record the unexpected observation;
4. stop any interpretation that would require modifying Praxis.

Unexpected evidence outranks expected narrative.

---

# 21. Stop conditions

Stop the mission when one of the following occurs.

## 21.1 Successful epistemic closure audit

Stop when all confirmed defects relevant to this mission have been repaired and demonstrated.

## 21.2 Praxis change required

Stop if further closure requires modifying Praxis.

Record the issue as candidate methodological learning.

Do not modify Praxis.

## 21.3 Governance change required

Stop if further work requires:

- promotion;
- commit;
- RF-A1 authorization;
- changing constitutive project authority.

Report the boundary instead.

## 21.4 Fundamental RF-A0 technical contradiction

If the audit reveals evidence that materially contradicts the claim that RF-A0 technical hardening is sufficient:

- record the contradiction;
- do not hide it;
- repair it only if it remains clearly within RF-A0;
- otherwise stop and report the new boundary.

---

# 22. Required final report

At the end of this mission, provide a concise but evidence-grounded report containing the following sections.

## 22.1 Audit findings

For each investigated concern:

```text
CONFIRMED
PARTIALLY CONFIRMED
REJECTED
```

and why.

## 22.2 Observed instead of declared

Identify every material property that previously depended on assertion or hardcoding and now comes from direct observation.

Especially report the actual Praxis identity used.

## 22.3 Prediction comparison

Explain how each protocol prediction is now causally linked to relevant observations and evidence.

Report at least:

```text
prediction id
comparison
supporting observation/check IDs
evidence reference
```

## 22.4 Unexpected-observation channel

Explain how the mechanism can now represent unexpected evidence.

State honestly whether the decisive run produced any unexpected observations.

## 22.5 Learning boundary

Explain how the implementation distinguishes:

```text
observation
comparison
interpretation
candidate learning
governance adoption
```

## 22.6 Protocol preservation

Explain how exact historical protocol bytes remain reconstructible after future revisions.

Provide the relevant digest verification.

## 22.7 Historical ledger integrity

Report whether the original three-run evidence chain remained unchanged.

Include:

```text
historical run count
historical ledger head
integrity result
```

The expected historical head, unless evidence proves otherwise, is:

```text
fc6d758e6a04d07451b9d86af45be1ef33b23d61731c124ee0140b1e72894fcc
```

## 22.8 New run, if any

If a new decisive run was necessary, report:

```text
run ID
protocol digest
Praxis identity
PASS count
EXPECTED_FAIL_CLOSED count
FAIL count
new ledger head
```

Do not use check count as a substitute for semantic interpretation.

## 22.9 Praxis result

Report the actual unchanged-validator result.

Do not merely state the expected outcome.

## 22.10 Governance state

Confirm explicitly:

```text
RF-A0 status
last verified milestone
last verified commit
RF-A0 authorization
RF-A1 authorization
promotion status
```

## 22.11 Git state

Confirm explicitly:

```text
branch
HEAD presence/absence
commit count
remote presence/absence
working tree state
```

## 22.12 Remaining limitations

State what RF-A0 still cannot prove.

Do not generalize beyond the evidence.

---

# 23. Acceptance criteria

This mission is successful only if all of the following are true:

- historical RF-A0 runs remain unchanged;
- the original ledger remains independently valid;
- exact committed protocol bytes are prospectively preservable;
- material external identities are observed rather than hardcoded;
- prediction comparisons are hypothesis-specific;
- hypotheses can independently be supported, contradicted, or remain inconclusive;
- unexpected observations are representable by the run machinery;
- an empty unexpected-observation list means none were observed, not that none can be represented;
- candidate learning is evidence-dependent and remains distinct from observation;
- candidate learning does not acquire governance authority automatically;
- unchanged Praxis behavior is observed honestly;
- Praxis remains unmodified;
- RF-A0 remains `active`;
- no verified milestone is fabricated;
- no Git commit is created;
- no remote is created;
- no push occurs;
- RF-A1 remains unauthorized and unimplemented;
- no unrelated functionality is added.

---

# 24. Scientific interpretation of the mission

This audit is not bookkeeping.

It establishes whether RF-A0 can distinguish:

```text
what we expected
from
what happened
from
what we infer
from
what we learned
from
what we are authorized to change
```

A reflexive engineering system is not one that always reaches the predicted result.

It is one that remains capable of recording when reality disagrees with prediction.

The desired feedback structure is:

```text
prediction
    ↓
experiment
    ↓
observation
    ↓
comparison
    ↓
unexpected evidence
    ↓
candidate learning
    ↓
possible methodological consequence
```

and, across independently governed systems:

```text
SRF observes Praxis P1
        ↓
methodological limitation discovered
        ↓
candidate learning exported
        ↓
Praxis may later evolve independently
        ↓
SRF observes Praxis P2 under a new commitment
```

The history of `P1` must remain true after `P2` exists.

---

# 25. Final instruction

Work autonomously within the boundaries above.

Do not optimize for pleasing the expected result.

Do not optimize for producing more artifacts.

Do not optimize for producing more PASS lines.

Prefer the smallest mechanism that makes the evidence more truthful, reconstructible, falsifiable, and causally traceable.

If the evidence contradicts an assumption in this mission, preserve the evidence and revise the conclusion.

**Evidence outranks instruction-level expectation.**

At completion:

> **Stop.**

Do not modify Praxis.

Do not commit.

Do not promote RF-A0.

Do not begin RF-A1.

Return the audit report and the evidence needed for independent review.
