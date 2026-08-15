# EPISTEMIC LEARNING LOOP

This project is not only an implementation exercise.

Its purpose is to produce explicit, testable and reusable understanding about Linux runtime semantics.

Codex must therefore work through an explicit learning loop during RF-A0.

The objective is NOT merely:

```text
propose
→ implement
→ make tests pass
```

The required reasoning cycle is:

```text
QUESTION
    ↓
CURRENT UNDERSTANDING
    ↓
HYPOTHESIS
    ↓
PREDICTION
    ↓
MINIMAL EXPERIMENT
    ↓
OBSERVATION
    ↓
CONFRONTATION WITH PREDICTION
    ↓
INTERPRETATION
    ↓
LEARNING
    ↓
RULE OR INVARIANT CANDIDATE
    ↓
GATE / EVIDENCE CONSEQUENCE
    ↓
NEXT QUESTION
```

Each meaningful technical decision in RF-A0 should pass through this cycle where practical.

---

# DO NOT REASON BACKWARDS FROM THE IMPLEMENTATION

Do not first implement something and then invent a justification for it.

Before significant implementation changes, record:

```text
what is currently believed;
what is uncertain;
what is being predicted;
what observation would support the prediction;
what observation would contradict it.
```

Then perform the smallest experiment capable of discriminating between the alternatives.

Tests are evidence.

They are not substitutes for a hypothesis.

A passing test does not by itself establish understanding.

---

# OBSERVATION VS INTERPRETATION

Maintain a strict distinction among:

```text
OBSERVED
INFERRED
LEARNED
NOT YET KNOWN
```

Example:

```text
OBSERVED:
  /proc/<pid>/ns/pid resolves to the same namespace identifier
  as the shell that launched the process.

INFERRED:
  the runtime probe has not entered a distinct PID namespace.

LEARNED:
  an ordinary native process inherits the launching environment's
  PID namespace unless another mechanism changes that relationship.

NOT YET KNOWN:
  how creating a new PID namespace changes process visibility.
```

The final item must remain unresolved until the milestone that is authorized to investigate it.

Do not convert inference into observation.

Do not convert expectation into evidence.

---

# PREDICTIONS BEFORE EXPERIMENTS

Whenever RF-A0 investigates an observable Linux property, formulate a prediction before collecting the decisive evidence.

Examples include:

```text
If the probe is an ordinary native Linux process,
its namespace identifiers should initially match those
of the launching shell for the namespaces that have not
been deliberately changed.

If the probe opens a regular file,
the corresponding descriptor should become externally
observable under /proc/<pid>/fd.

If the probe binds a socket to loopback,
the listening endpoint should be externally observable
from the same host network namespace.

If SIGTERM is handled correctly,
the process should perform controlled shutdown
rather than requiring SIGKILL.
```

Predictions may prove wrong.

A disproved prediction is a valid and potentially valuable result.

Do not modify historical predictions after observing the result.

---

# SURPRISES ARE FIRST-CLASS RESULTS

Unexpected behavior must not be silently patched away.

When actual behavior differs from the prediction:

1. record the discrepancy;
2. determine whether it results from:
   - an incorrect hypothesis;
   - an implementation defect;
   - an environmental property;
   - an incomplete mental model;
   - a tooling limitation;
3. design the smallest discriminating experiment;
4. rerun;
5. update the understanding explicitly.

Do not immediately change the code merely to obtain PASS.

The first question after a surprising result must be:

> What have we learned about the system?

not:

> How do we make the gate green?

---

# LEARNING RECORD

Maintain a compact, structured learning record for RF-A0.

Use the current Praxis representation if one already exists.

If Praxis has no canonical artifact for this purpose, create the smallest project-local representation necessary without inventing a new Praxis-wide standard.

Each substantive learning entry should contain conceptually:

```text
question
prior_understanding
hypothesis
prediction
experiment
observation
result
interpretation
learning
confidence
limitations
candidate_rule
gate_consequence
open_questions
```

Do not create learning entries for trivial implementation events.

Record only knowledge that materially changes or sharpens the project's understanding.

---

# CONFIDENCE

Learning must state its evidential strength.

Use a small qualitative scale such as:

```text
TENTATIVE
SUPPORTED
STRONGLY_SUPPORTED
```

unless the current Praxis method already defines an equivalent vocabulary.

Confidence must derive from evidence, not from Codex certainty.

Example:

```text
TENTATIVE:
  suggested by one observation or environmental inspection.

SUPPORTED:
  reproduced by a focused experiment with an explicit prediction.

STRONGLY_SUPPORTED:
  reproduced, independently checked where practical,
  and protected by an executable gate or invariant.
```

Do not use absolute language where evidence does not justify it.

---

# FROM LEARNING TO GOVERNANCE

Not every observation deserves a rule.

Not every rule deserves a schema.

Not every schema deserves a gate.

Promote knowledge progressively:

```text
observation
    ↓
reproduced finding
    ↓
learning
    ↓
candidate invariant
    ↓
validated invariant
    ↓
project rule
    ↓
machine-checkable contract where appropriate
    ↓
gate
```

Codex must explicitly justify each promotion.

Avoid premature formalization.

The project must discover its runtime semantics before trying to encode all of them into governance.

---

# NEGATIVE KNOWLEDGE

Record important things that the experiment demonstrates are NOT true.

For example, if supported by evidence:

```text
an executable is not itself a process;

a PID is not a stable identity across all namespace contexts;

an open file descriptor is process state, not merely a path;

a listening port belongs to a network context,
not abstractly to an application;

containerization is not required for these Linux process properties.
```

Negative findings are particularly valuable when they eliminate misleading mental models.

---

# ALTERNATIVE EXPLANATIONS

For important conclusions, consider at least one plausible alternative explanation when one exists.

Example:

```text
Observation:
  a socket is reachable only from loopback.

Possible explanation A:
  the application explicitly bound 127.0.0.1.

Possible explanation B:
  some external isolation mechanism prevents access.

Discriminating evidence:
  inspect the actual socket binding and current namespace context.
```

Prefer experiments that distinguish explanations over assumptions based on expected behavior.

---

# MINIMAL EXPERIMENT PRINCIPLE

Every experiment should answer one primary question.

Avoid experiments that simultaneously change:

```text
filesystem
network
process namespace
cgroup
privilege
application behavior
```

because the causal explanation becomes ambiguous.

RF-A0 is the baseline.

Its value depends on minimizing introduced variables.

---

# LEARN BEFORE ABSTRACTING

Do not create reusable abstraction layers before the experiment has established why they are needed.

In particular, avoid premature:

```text
runtime frameworks
generic probe frameworks
container abstractions
deployment abstractions
namespace abstractions
resource-governance abstractions
large class hierarchies
generic configuration systems
```

A little duplication inside an early experiment is preferable to an abstraction whose semantics have not yet been understood.

---

# LEARN BEFORE GENERALIZING TO SISTER

SisTer is the reference system, not proof.

Do not infer:

```text
SisTer requires X
```

merely because the RF-A0 probe uses X.

At RF-A0, distinguish:

```text
Linux runtime fact
experimental probe design
possible SisTer relevance
verified SisTer requirement
```

Only the first two are expected to be established in this mission.

Verified SisTer deployment requirements belong primarily to RF-A8.

---

# REFLECTION CHECKPOINTS

At natural checkpoints during RF-A0, pause implementation internally and evaluate:

```text
What did we expect?

What actually happened?

What changed in our understanding?

Which previous assumption is now weaker or stronger?

Did the implementation reveal an environmental dependency?

Did the experiment answer the intended question?

Are we testing behavior or merely testing our own implementation?

Did a new question emerge?

Should anything become an invariant?

Should anything explicitly remain unresolved?
```

Use these reflections to choose the next smallest experiment.

Do not expand scope merely because an adjacent topic becomes interesting.

---

# MILESTONE SYNTHESIS

Before declaring RF-A0 technically complete, produce a synthesis that answers:

## What we knew before RF-A0

State the initial assumptions and mental model.

## What RF-A0 directly demonstrated

Only experimentally supported findings.

## What changed in our understanding

Identify corrected, refined or rejected assumptions.

## What became governed knowledge

List only findings promoted to rules, invariants or gates.

## What remains uncertain

Explicitly preserve unresolved questions.

## What RF-A0 does NOT establish

State the semantic boundary of the evidence.

## Questions handed to RF-A1

List questions that legitimately emerge from RF-A0 but require filesystem-semantics experimentation.

These questions do NOT authorize RF-A1.

---

# FAILURE IS AN ACCEPTABLE SCIENTIFIC RESULT

A failed hypothesis does not make RF-A0 unsuccessful.

A useful outcome may be:

```text
prediction disproved
→ mental model corrected
→ evidence preserved
→ new hypothesis formulated
```

What is unacceptable is:

```text
unexpected result
→ unexplained workaround
→ test changed
→ PASS
```

The purpose of the gate is to protect demonstrated knowledge, not to manufacture success.

---

# SOURCE CHANGES CAUSED BY LEARNING

When an experiment reveals that implementation or documentation must change, Codex must be able to trace conceptually:

```text
observation
    ↓
learning
    ↓
reason for change
    ↓
source/documentation change
    ↓
new test or gate if appropriate
```

Avoid unexplained corrective patches.

---

# FINAL RESPONSE — ADDITIONAL REQUIRED SECTION

Add a section named:

## Learning produced

Report the most important learning cycles in compact form:

```text
Question
Initial hypothesis
Prediction
Observation
Conclusion
Confidence
Governance consequence
Open question
```

Also report:

```text
assumptions confirmed
assumptions corrected
assumptions rejected
unexpected observations
candidate invariants accepted
candidate invariants rejected or deferred
```

Do not report generic statements such as:

```text
"we learned a lot about Linux processes"
```

Every claimed learning must be traceable to an experiment or direct observation.

---

# STOP CONDITION

RF-A0 is complete only when:

```text
implementation works
AND
evidence is reproducible
AND
the learning is explicit
AND
claims do not exceed evidence
AND
governance reflects the demonstrated state
```

A green build alone is insufficient.

A green gate alone is insufficient.

The intended output of RF-A0 is:

```text
working software
+
reproducible evidence
+
corrected mental model
+
explicit learning
+
governed knowledge
+
better questions
```
