#!/usr/bin/env python3
"""Run an isolated local Dagster and dashboard with synthetic DuckDB data."""

import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / "tmpdata" / "local-stack"


def main():
    LOCAL.mkdir(parents=True, exist_ok=True)
    # Keep dotenv discovery and Dagster history separate from the real project.
    (LOCAL / ".env").touch()
    metrics = LOCAL / "metrics"
    metrics.mkdir(exist_ok=True)
    for target, source in {
        metrics / "defaults": ROOT / "metrics/defaults",
        LOCAL / "dashboard": ROOT / "dashboard",
    }.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.symlink_to(source, target_is_directory=True)
    shutil.copytree(
        ROOT / "metrics/examples/python/python_ingest_simple",
        metrics / "examples/python/python_ingest_simple",
        dirs_exist_ok=True,
    )
    dagster_home = LOCAL / "dagster_home"
    dagster_home.mkdir(exist_ok=True)
    (dagster_home / "dagster.yaml").write_text("telemetry:\n  enabled: false\n")
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("ANOMSTACK_", "POSTHOG_", "DAGSTER_"))
    }
    env.update(
        PYTHONPATH=str(ROOT),
        PYTHON_DOTENV_DISABLED="1",
        DAGSTER_HOME=str(dagster_home),
        ANOMSTACK_ENV_FILE_PATH=str(LOCAL / ".env"),
        ANOMSTACK_DUCKDB_PATH=str(LOCAL / "metrics.db"),
        ANOMSTACK_IGNORE_EXAMPLES="no",
        ANOMSTACK__PYTHON_INGEST_SIMPLE__ALERT_METHODS="",
        ANOMSTACK__PYTHON_INGEST_SIMPLE__THOLDALERT_METHODS="",
    )
    if not (LOCAL / "metrics.db").exists():
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/development/seed_local_db.py"),
                "--db-path",
                env["ANOMSTACK_DUCKDB_PATH"],
            ],
            cwd=LOCAL,
            env=env,
            check=True,
        )
    children = []

    def stop(*_):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, stop)
    try:
        for command in (
            [
                sys.executable,
                "-m",
                "dagster",
                "dev",
                "-f",
                str(ROOT / "scripts/development/local_definitions.py"),
                "-h",
                "127.0.0.1",
                "-p",
                "3000",
            ],
            [
                sys.executable,
                "-m",
                "uvicorn",
                "dashboard.app:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8080",
            ],
        ):
            children.append(subprocess.Popen(command, cwd=LOCAL, env=env, start_new_session=True))
        print("Dashboard: http://localhost:8080 | Dagster: http://localhost:3000", flush=True)
        while all(child.poll() is None for child in children):
            time.sleep(1)
        raise RuntimeError("A local service exited; see its logs above.")
    except KeyboardInterrupt:
        pass
    finally:
        for child in children:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
        for child in children:
            try:
                child.wait(timeout=15)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()


if __name__ == "__main__":
    main()
