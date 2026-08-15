#!/usr/bin/env python3
"""Collect and correlate RF-A0 evidence from one live native child process."""

from __future__ import annotations

import datetime as dt
import json
import os
import selectors
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

from execution_authority import (
    AuthorityViolation,
    ExecutionContext,
    spawn_external,
)


class EvidenceFailure(RuntimeError):
    pass


def read_links(directory: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for entry in sorted(directory.iterdir(), key=lambda item: item.name):
        try:
            result[entry.name] = os.readlink(entry)
        except FileNotFoundError:
            continue
    return result


def render_links(values: dict[str, str]) -> str:
    return "".join(f"{key} -> {value}\n" for key, value in values.items())


def normalized_snapshot(text: str) -> str:
    """Remove procfs column padding that would fail a versioned whitespace check."""
    return "\n".join(line.rstrip(" \t") for line in text.splitlines()) + "\n"


def read_ready(process: subprocess.Popen[bytes]) -> tuple[dict[str, str], list[str]]:
    assert process.stdout is not None
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    values: dict[str, str] = {}
    lines: list[str] = []
    buffered = b""
    deadline = time.monotonic() + 5

    while time.monotonic() < deadline:
        if process.poll() is not None:
            stderr = process.stderr.read().decode("utf-8") if process.stderr else ""
            raise EvidenceFailure(
                f"probe exited before ready: returncode={process.returncode} stderr={stderr!r}"
            )
        if not selector.select(timeout=0.1):
            continue
        chunk = os.read(process.stdout.fileno(), 4096)
        if not chunk:
            continue
        buffered += chunk
        while b"\n" in buffered:
            raw_line, buffered = buffered.split(b"\n", 1)
            line = raw_line.decode("utf-8")
            lines.append(line)
            key, separator, value = line.partition("=")
            if separator:
                values[key] = value
            if values.get("ready") == "1":
                return values, lines

    raise EvidenceFailure("probe did not become ready within five seconds")


def status_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        key, separator, value = line.partition(":")
        if separator:
            fields[key] = value.strip()
    return fields


def find_tcp_listener(tcp_text: str, port: int, inode: str) -> str:
    expected_address = f"0100007F:{port:04X}"
    for line in tcp_text.splitlines()[1:]:
        columns = line.split()
        if len(columns) > 9 and columns[1] == expected_address and columns[3] == "0A":
            if columns[9] != inode:
                raise EvidenceFailure(
                    f"listener inode mismatch: fd={inode} tcp={columns[9]}"
                )
            return line.rstrip(" \t") + "\n"
    raise EvidenceFailure(
        f"no LISTEN row for 127.0.0.1:{port} and socket inode {inode}"
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise EvidenceFailure(message)


def run_signal_stress(
    executable: Path,
    environment: dict[str, str],
    authority: ExecutionContext,
    iterations: int,
) -> dict[str, object]:
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    completed = 0
    failure: str | None = None
    for iteration in range(iterations):
        regular_file = executable.parent / f"rf-a0-signal-stress-{iteration}.dat"
        process = spawn_external(
            authority,
            "probe.run",
            [str(executable), "--file", str(regular_file), "--port", "0"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environment,
        )
        forced_kill = False
        try:
            _, initial_lines = read_ready(process)
            process.send_signal(signal.SIGTERM)
            stdout_tail, stderr_bytes = process.communicate(timeout=5)
            lines = initial_lines + stdout_tail.decode("utf-8").splitlines()
            if process.returncode != 0:
                failure = (
                    f"iteration {iteration}: returncode={process.returncode} "
                    f"stderr={stderr_bytes.decode('utf-8')!r}"
                )
                break
            if "shutdown_signal=15" not in lines or "shutdown=controlled" not in lines:
                failure = f"iteration {iteration}: controlled shutdown record missing"
                break
            completed += 1
        except (EvidenceFailure, OSError, subprocess.SubprocessError) as error:
            failure = f"iteration {iteration}: {error}"
            break
        finally:
            if process.poll() is None:
                forced_kill = True
                process.kill()
                process.wait(timeout=5)
            if forced_kill and failure is None:
                failure = f"iteration {iteration}: forced cleanup required"

    return {
        "started_at_utc": started,
        "completed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "requested_iterations": iterations,
        "completed_iterations": completed,
        "all_controlled": failure is None and completed == iterations,
        "failure": failure,
        "claim_boundary": "Repeated stress increases sensitivity to the prior race but is not a mathematical proof of concurrency correctness.",
    }


def collect(executable: Path, evidence_directory: Path) -> dict[str, object]:
    evidence_directory.mkdir(parents=True, exist_ok=True)
    forced_kill_marker = evidence_directory / "forced-kill.txt"
    if forced_kill_marker.exists():
        forced_kill_marker.unlink()
    regular_file = executable.parent / "rf-a0-opened-by-probe.dat"
    environment = os.environ.copy()
    environment["SRF_PROBE_CONTEXT"] = "rf-a0-native-baseline"
    protocol_digest = environment.get("SRF_PROTOCOL_SHA256", "")
    run_id = environment.get("SRF_RUN_ID", "")
    require(len(protocol_digest) == 64, "protocol digest missing from run environment")
    require(bool(run_id), "run identity missing from run environment")
    observation_started = dt.datetime.now(dt.timezone.utc).isoformat()
    authority = ExecutionContext(Path(__file__).resolve().parents[1])

    process = spawn_external(
        authority,
        "probe.run",
        [str(executable), "--file", str(regular_file), "--port", "0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
    )

    initial_lines: list[str] = []
    forced_kill = False
    try:
        values, initial_lines = read_ready(process)
        pid = process.pid
        proc = Path("/proc") / str(pid)
        required_fields = {
            "pid",
            "cplusplus",
            "ppid",
            "uid",
            "gid",
            "cwd",
            "environment.SRF_PROBE_CONTEXT",
            "regular_file",
            "regular_fd",
            "listen_address",
            "listen_port",
            "socket_fd",
            "signal_wait",
            "signal_fd",
            "open_fds",
        }
        require(required_fields <= values.keys(), "probe omitted required fields")
        require(int(values["pid"]) == pid, "reported PID differs from launched child")
        require(int(values["ppid"]) == os.getpid(), "probe PPID differs from collector PID")
        require(int(values["uid"]) == os.getuid(), "probe UID differs from collector UID")
        require(int(values["gid"]) == os.getgid(), "probe GID differs from collector GID")
        require(values["listen_address"] == "127.0.0.1", "listener is not loopback")
        require(int(values["cplusplus"]) >= 202302, "reported language mode is not C++23")
        require(values["signal_wait"] == "signalfd", "signal wait is not signalfd")
        require(
            values["environment.SRF_PROBE_CONTEXT"] == "rf-a0-native-baseline",
            "controlled environment observation differs",
        )

        status_text = (proc / "status").read_text(encoding="utf-8")
        maps_text = (proc / "maps").read_text(encoding="utf-8")
        mountinfo_text = (proc / "mountinfo").read_text(encoding="utf-8")
        cgroup_text = (proc / "cgroup").read_text(encoding="utf-8")
        tcp_text = (proc / "net/tcp").read_text(encoding="utf-8")
        environ_bytes = (proc / "environ").read_bytes()
        fd_links = read_links(proc / "fd")
        probe_ns = read_links(proc / "ns")
        launcher_ns = read_links(Path("/proc/self/ns"))
        launcher_cgroup = Path("/proc/self/cgroup").read_text(encoding="utf-8")
        executable_link = os.readlink(proc / "exe")

        fields = status_fields(status_text)
        require(fields.get("Pid") == str(pid), "/proc status PID mismatch")
        require(fields.get("PPid") == str(os.getpid()), "/proc status PPID mismatch")
        require(fields.get("Uid", "").split()[0] == str(os.getuid()), "/proc UID mismatch")
        require(fields.get("Gid", "").split()[0] == str(os.getgid()), "/proc GID mismatch")
        require(Path(executable_link).resolve() == executable.resolve(), "/proc exe mismatch")
        require(bool(maps_text.strip()), "/proc maps is empty")
        require(bool(mountinfo_text.strip()), "/proc mountinfo is empty")
        require(
            b"SRF_PROBE_CONTEXT=rf-a0-native-baseline" in environ_bytes.split(b"\0"),
            "selected environment entry absent from /proc environ",
        )

        regular_fd = values["regular_fd"]
        socket_fd = values["socket_fd"]
        signal_fd = values["signal_fd"]
        require(regular_fd in fd_links, "reported regular fd absent from /proc fd")
        require(socket_fd in fd_links, "reported socket fd absent from /proc fd")
        require(signal_fd in fd_links, "reported signal fd absent from /proc fd")
        require(
            Path(fd_links[regular_fd]).resolve() == Path(values["regular_file"]).resolve(),
            "regular fd target differs from declared file",
        )
        socket_target = fd_links[socket_fd]
        require(
            socket_target.startswith("socket:[") and socket_target.endswith("]"),
            "socket fd target does not expose an inode",
        )
        socket_inode = socket_target.removeprefix("socket:[").removesuffix("]")
        require(fd_links[signal_fd] == "anon_inode:[signalfd]", "signal fd is not signalfd")
        port = int(values["listen_port"])
        listener_row = find_tcp_listener(tcp_text, port, socket_inode)

        common_namespace_types = sorted(probe_ns.keys() & launcher_ns.keys())
        require(bool(common_namespace_types), "no comparable namespace links")
        namespace_mismatches = {
            name: {"launcher": launcher_ns[name], "probe": probe_ns[name]}
            for name in common_namespace_types
            if launcher_ns[name] != probe_ns[name]
        }
        require(not namespace_mismatches, f"namespace mismatch: {namespace_mismatches}")
        require(cgroup_text == launcher_cgroup, "probe and launcher cgroup records differ")

        with socket.create_connection(("127.0.0.1", port), timeout=2):
            pass

        (evidence_directory / "proc-status.txt").write_text(
            normalized_snapshot(status_text), encoding="utf-8"
        )
        (evidence_directory / "proc-fd.txt").write_text(
            render_links(fd_links), encoding="utf-8"
        )
        (evidence_directory / "proc-maps.txt").write_text(
            normalized_snapshot(maps_text), encoding="utf-8"
        )
        (evidence_directory / "proc-mountinfo.txt").write_text(
            normalized_snapshot(mountinfo_text), encoding="utf-8"
        )
        (evidence_directory / "proc-ns.txt").write_text(
            render_links(probe_ns), encoding="utf-8"
        )
        (evidence_directory / "proc-cgroup.txt").write_text(
            normalized_snapshot(cgroup_text), encoding="utf-8"
        )
        (evidence_directory / "launcher-ns.txt").write_text(
            render_links(launcher_ns), encoding="utf-8"
        )
        (evidence_directory / "launcher-cgroup.txt").write_text(
            normalized_snapshot(launcher_cgroup), encoding="utf-8"
        )
        (evidence_directory / "proc-net-tcp-listener.txt").write_text(
            listener_row, encoding="utf-8"
        )

        process.send_signal(signal.SIGTERM)
        stdout_tail, stderr_bytes = process.communicate(timeout=5)
        stderr = stderr_bytes.decode("utf-8")
        all_lines = initial_lines + stdout_tail.decode("utf-8").splitlines()
        require(process.returncode == 0, f"probe returned {process.returncode}")
        require("shutdown_signal=15" in all_lines, "SIGTERM was not reported")
        require("shutdown=controlled" in all_lines, "controlled shutdown absent")

        signal_stress = run_signal_stress(executable, environment, authority, 128)
        (evidence_directory / "signal-stress.json").write_text(
            json.dumps(signal_stress, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        require(signal_stress["all_controlled"] is True, "signal stress failed")

        stdout_text = "\n".join(all_lines) + "\n"
        (evidence_directory / "probe-stdout.txt").write_text(
            stdout_text, encoding="utf-8"
        )
        (evidence_directory / "probe-stderr.txt").write_text(stderr, encoding="utf-8")

        observation: dict[str, object] = {
            "run_id": run_id,
            "protocol_sha256": protocol_digest,
            "observation_started_at_utc": observation_started,
            "captured_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "executable": executable_link,
            "cplusplus": int(values["cplusplus"]),
            "pid": pid,
            "ppid": int(values["ppid"]),
            "uid": int(values["uid"]),
            "gid": int(values["gid"]),
            "cwd": values["cwd"],
            "regular_file": values["regular_file"],
            "regular_fd": int(regular_fd),
            "socket_fd": int(socket_fd),
            "socket_inode": socket_inode,
            "signal_wait": values["signal_wait"],
            "signal_fd": int(signal_fd),
            "listen_address": "127.0.0.1",
            "listen_port": port,
            "tcp_state": "LISTEN",
            "namespace_types_compared": common_namespace_types,
            "namespace_links_match_launcher": True,
            "cgroup_record_matches_launcher": True,
            "maps_observed": True,
            "mountinfo_observed": True,
            "selected_environment_observed": True,
            "loopback_connection_succeeded": True,
            "shutdown_signal": signal.SIGTERM,
            "controlled_shutdown": True,
            "forced_kill": False,
            "signal_stress_iterations": signal_stress["completed_iterations"],
        }
        (evidence_directory / "observation.json").write_text(
            json.dumps(observation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        analysis = f"""# RF-A0 generated analysis

## OBSERVED

- The launched executable resolved through `/proc/{pid}/exe` to `{executable_link}`.
- Probe output and `/proc/{pid}/status` agreed on PID {pid}, PPID {values['ppid']}, UID {values['uid']}, and GID {values['gid']}.
- Descriptor {regular_fd} resolved to `{values['regular_file']}` while the process was alive.
- Descriptor {socket_fd} resolved to socket inode {socket_inode}; `/proc/{pid}/net/tcp` showed that inode listening at `127.0.0.1:{port}`; a loopback connection succeeded.
- Descriptor {signal_fd} resolved to `anon_inode:[signalfd]`; the probe reported C++ language macro {values['cplusplus']}.
- Launcher and probe namespace links matched for: {', '.join(common_namespace_types)}.
- Launcher and probe cgroup records were byte-for-byte equal.
- `/proc/{pid}/maps` and `/proc/{pid}/mountinfo` were readable and nonempty.
- SIGTERM produced the probe records `shutdown_signal=15` and `shutdown=controlled`; exit status was zero and no forced kill was used.
- {signal_stress['completed_iterations']} consecutive immediate-after-ready SIGTERM stress iterations also completed without forced termination.

## INFERRED

- The executable artifact and this process instance are related but distinct: the kernel exposed a live PID and per-process state for one execution of the artifact.
- The regular-file descriptor and socket were live process resources, not properties established merely by printed paths or port numbers.
- This project did not place the probe in a namespace or cgroup different from its launcher during this run.
- Explicit loopback binding explains the observed listener address without requiring a network-isolation explanation.

## LEARNED

- For this ordinary native-child baseline, identity and retained resources can be correlated independently through procfs and an active connection.
- Claims about inherited runtime context must be relative to the launcher and execution environment, not generalized to an unnamespaced or globally unique host view.
- Controlled SIGTERM shutdown is demonstrable only by combining signal action, emitted shutdown state, timely exit, exit code, and absence of forced termination.

## NOT_YET_KNOWN

- How filesystem semantics change when deliberately varied (RF-A1, unauthorized).
- How creating or entering namespaces changes identity and visibility (RF-A2, unauthorized).
- How cgroup v2 controllers or limits change resource behavior (RF-A3, unauthorized).
- How network isolation changes reachability (RF-A4, unauthorized).
- What runtime properties SisTer itself requires for deployment (primarily RF-A8, unauthorized).
"""
        (evidence_directory / "analysis.md").write_text(analysis, encoding="utf-8")
        return observation
    finally:
        if process.poll() is None:
            forced_kill = True
            process.kill()
            process.wait(timeout=5)
        if forced_kill:
            (evidence_directory / "forced-kill.txt").write_text(
                "The collector had to force termination; RF-A0 evidence is invalid.\n",
                encoding="utf-8",
            )


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: collect_rf_a0_evidence.py PROBE EVIDENCE_DIRECTORY", file=sys.stderr)
        return 2

    executable = Path(sys.argv[1]).resolve()
    evidence_directory = Path(sys.argv[2]).resolve()
    if not executable.is_file():
        print(f"FAIL executable missing: {executable}", file=sys.stderr)
        return 1

    try:
        observation = collect(executable, evidence_directory)
    except (AuthorityViolation, EvidenceFailure, OSError, subprocess.SubprocessError) as error:
        print(f"FAIL RF-A0 runtime observation: {error}", file=sys.stderr)
        return 1

    for statement in [
        "process identity correlated through /proc",
        "regular file descriptor externally observable",
        "loopback listener correlated by descriptor, inode, TCP row, and connection",
        "launcher/probe namespace links compared",
        "launcher/probe cgroup records compared",
        "required /proc observations collected",
        "SIGTERM caused controlled shutdown without forced kill",
    ]:
        print(f"PASS {statement}")
    print(f"evidence={evidence_directory}")
    print(f"pid_observed={observation['pid']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
