"""Bound CLI jobs and publish their outputs only after successful completion."""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile


def now():
    return datetime.now(timezone.utc).isoformat()


def read_status(path):
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def write_status(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     delete=False) as handle:
        temp = Path(handle.name)
        json.dump(value, handle, ensure_ascii=False)
    try:
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


@contextmanager
def job_lock(path):
    """OS releases this lock even if the supervisor crashes (Linux and Windows)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        if os.name == "nt":
            import msvcrt
            handle.seek(0)
            if not handle.read(1):
                handle.write(b"0")
                handle.flush()
            handle.seek(0)
            try:
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise RuntimeError("Pipeline už běží v jiném procesu.") from exc
        else:
            import fcntl
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise RuntimeError("Pipeline už běží v jiném procesu.") from exc
        try:
            yield
        finally:
            if os.name == "nt":
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


def run_bounded(command, output_dir, status_name, timeout=300):
    """command(stage) runs in a killable child; status never stores stderr/secrets.

    The timeout covers the worker (downloads, computation and optional sync).
    Remote writes already accepted before a timeout cannot be rolled back.
    """
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("Časový limit musí být kladné konečné číslo.")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    status_path = output_dir / status_name
    # One lock for real and demo too: a single pipeline owns publication.
    with job_lock(output_dir / ".pipeline.lock"):
        status = read_status(status_path)
        status.update(state="running", started_at=now(), finished_at=None,
                      timeout_seconds=timeout, error=None)
        write_status(status_path, status)
        try:
            with tempfile.TemporaryDirectory(prefix=".run-", dir=output_dir) as temp:
                stage = Path(temp)
                subprocess.run(command(stage), check=True, timeout=timeout)
                files = sorted(stage.glob("*.csv"))
                if not files:
                    raise RuntimeError("Pipeline nevytvořila žádné výstupy.")
                for file in files:
                    os.replace(file, output_dir / file.name)
                status.update(state="success", finished_at=now(),
                              last_success_at=now(),
                              last_success_files=[file.name for file in files])
        except BaseException as exc:
            state = "timeout" if isinstance(exc, subprocess.TimeoutExpired) else "failed"
            status.update(state=state, finished_at=now(),
                          error="Překročen časový limit." if state == "timeout"
                          else "Běh selhal; podrobnosti jsou v terminálu.")
            write_status(status_path, status)
            raise
        write_status(status_path, status)
        return status
