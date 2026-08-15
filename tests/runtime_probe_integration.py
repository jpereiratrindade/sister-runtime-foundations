#!/usr/bin/env python3
"""Black-box CTest for the native Linux process probe."""

from __future__ import annotations

import os
import selectors
import signal
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from execution_authority import ExecutionContext, spawn_external


def fail(message: str) -> None:
    raise AssertionError(message)


def read_until_ready(process: subprocess.Popen[bytes]) -> tuple[dict[str, str], list[str]]:
    assert process.stdout is not None
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    values: dict[str, str] = {}
    lines: list[str] = []
    buffered = b""
    deadline = time.monotonic() + 5

    while time.monotonic() < deadline:
        if process.poll() is not None:
            fail(f"probe exited before ready with {process.returncode}")
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

    fail("probe did not become ready")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: runtime_probe_integration.py PROBE", file=sys.stderr)
        return 2

    executable = Path(sys.argv[1]).resolve()
    if not executable.is_file():
        fail(f"probe executable missing: {executable}")

    authority = ExecutionContext(ROOT)
    with tempfile.TemporaryDirectory(
        prefix="srf-rf-a0-test-", dir=executable.parent
    ) as directory:
        regular_file = Path(directory) / "opened-by-probe.dat"
        environment = os.environ.copy()
        environment["SRF_PROBE_CONTEXT"] = "ctest-native-process"
        process = spawn_external(
            authority,
            "probe.run",
            [str(executable), "--file", str(regular_file), "--port", "0"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environment,
        )

        try:
            values, initial_lines = read_until_ready(process)
            required = {
                "probe",
                "cplusplus",
                "pid",
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
                "ready",
            }
            missing = required - values.keys()
            if missing:
                fail(f"missing probe fields: {sorted(missing)}")

            if int(values["pid"]) != process.pid:
                fail("reported PID does not match child PID")
            if int(values["ppid"]) != os.getpid():
                fail("reported PPID does not match test process")
            if int(values["uid"]) != os.getuid() or int(values["gid"]) != os.getgid():
                fail("reported credentials do not match test process")
            if values["environment.SRF_PROBE_CONTEXT"] != "ctest-native-process":
                fail("selected environment value was not exposed")
            if values["listen_address"] != "127.0.0.1":
                fail("listener is not explicitly bound to loopback")
            if int(values["cplusplus"]) < 202302:
                fail("probe did not report the required C++23 language mode")
            if values["signal_wait"] != "signalfd":
                fail("probe did not report the Linux signalfd wait mechanism")

            pid = process.pid
            regular_fd = int(values["regular_fd"])
            socket_fd = int(values["socket_fd"])
            signal_fd = int(values["signal_fd"])
            reported_fds = {int(item) for item in values["open_fds"].split(",")}
            if not {regular_fd, socket_fd, signal_fd} <= reported_fds:
                fail("opened descriptors are absent from open_fds")
            if Path(f"/proc/{pid}/fd/{regular_fd}").resolve() != regular_file.resolve():
                fail("regular descriptor does not resolve to the declared file")
            if not os.readlink(f"/proc/{pid}/fd/{socket_fd}").startswith("socket:["):
                fail("socket descriptor is not observable through /proc")

            status = Path(f"/proc/{pid}/status").read_text(encoding="utf-8")
            if f"Pid:\t{pid}" not in status or f"PPid:\t{os.getpid()}" not in status:
                fail("/proc status does not identify the process relationship")

            with socket.create_connection(
                ("127.0.0.1", int(values["listen_port"])), timeout=2
            ):
                pass

            process.send_signal(signal.SIGTERM)
            stdout_tail, stderr = process.communicate(timeout=5)
            all_lines = initial_lines + stdout_tail.decode("utf-8").splitlines()
            if process.returncode != 0:
                fail(f"probe returned {process.returncode}: {stderr.decode('utf-8')}")
            if "shutdown_signal=15" not in all_lines:
                fail("SIGTERM was not reported")
            if "shutdown=controlled" not in all_lines:
                fail("controlled shutdown was not reported")
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)

        stress_iterations = 64
        for iteration in range(stress_iterations):
            stress_file = Path(directory) / f"signal-stress-{iteration}.dat"
            stress_process = spawn_external(
                authority,
                "probe.run",
                [str(executable), "--file", str(stress_file), "--port", "0"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=environment,
            )
            try:
                _, stress_initial = read_until_ready(stress_process)
                stress_process.send_signal(signal.SIGTERM)
                stress_tail, stress_stderr = stress_process.communicate(timeout=5)
                stress_lines = stress_initial + stress_tail.decode("utf-8").splitlines()
                if stress_process.returncode != 0:
                    fail(
                        f"stress iteration {iteration} returned {stress_process.returncode}: "
                        f"{stress_stderr.decode('utf-8')}"
                    )
                if "shutdown_signal=15" not in stress_lines or "shutdown=controlled" not in stress_lines:
                    fail(f"stress iteration {iteration} lacked controlled shutdown evidence")
            finally:
                if stress_process.poll() is None:
                    stress_process.kill()
                    stress_process.wait(timeout=5)

    print(f"runtime probe integration: PASS; signal stress iterations={stress_iterations}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
