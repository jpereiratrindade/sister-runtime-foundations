# SisTer Runtime Foundations

**From Bare Metal to Governed Containers**

SisTer Runtime Foundations (SRF) is a C++23 research project using Fedora Linux
as its reference execution platform and asking what Linux
runtime environment is necessary and sufficient for SisTer-class software when
process, filesystem, resource, network, persistence, and security boundaries
must be explicit, reproducible, and governable.

The governing principle is: **begin with a Linux process and earn every
boundary**. RF-A0 is the only active and authorized milestone. It studies an
ordinary native child process; it does not create isolation or implement a
container.

## Build and test

```sh
cmake -S . -B .build/dev
cmake --build .build/dev
ctest --test-dir .build/dev --output-on-failure
```

The complete fail-closed RF-A0 gate commits the pre-observation protocol,
validates governance against the current sibling Praxis checkout, creates a
clean run-specific build, tests, captures the Fedora/toolchain baseline, runs
the native experiment, and appends a hash-chained evidence record:

```sh
python3 scripts/verify_rf_a0.py
```

See [Project foundation](docs/project-foundation.md), [RF-A0 experiment](docs/rf-a0-experiment.md),
[hardening synthesis](docs/rf-a0-hardening-synthesis.md), the fixed
[pre-observation protocol](.hoa/protocols/rf-a0-pre-observation.json), and the
separate project-local [post-observation learning](.hoa/learning/rf-a0.json).
