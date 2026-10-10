"""Start CrimeMap FastAPI and Vite together on Windows, Linux or macOS.

Run from any directory: python start.py
Windows: double-click start_windows.bat after first-time setup.
Uses the existing backend/.venv and frontend/node_modules. Never seeds,
bootstraps, recreates accounts, or changes the configured database.
"""
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
IS_WINDOWS = os.name == "nt"
PYTHON = BACKEND / ".venv" / ("Scripts/python.exe" if IS_WINDOWS else "bin/python")
VITE_SCRIPT = FRONTEND / "node_modules" / "vite" / "bin" / "vite.js"


def setup_commands() -> str:
    if IS_WINDOWS:
        return (
            "  cd backend\n"
            "  py -3 -m venv .venv\n"
            "  .\\.venv\\Scripts\\python.exe -m pip install -r requirements-dev.txt\n"
            "  cd ..\\frontend\n"
            "  npm install"
        )
    return (
        "  cd backend\n"
        "  python3 -m venv .venv\n"
        "  .venv/bin/python -m pip install -r requirements-dev.txt\n"
        "  cd ../frontend\n"
        "  npm install"
    )


def prerequisites() -> bool:
    if not BACKEND.is_dir() or not FRONTEND.is_dir():
        print("Error: start.py must live in the CrimeMap repository root.", file=sys.stderr)
        return False
    if not PYTHON.is_file():
        print("Backend Python environment missing. First-time setup:\n"
              + setup_commands(), file=sys.stderr)
        return False
    if not shutil.which("node"):
        print("Error: Node.js was not found. Install a supported Node.js LTS "
              "release and reopen the terminal.", file=sys.stderr)
        return False
    if not VITE_SCRIPT.is_file():
        print("Frontend dependencies missing. Run: cd frontend && npm install",
              file=sys.stderr)
        return False
    result = subprocess.run(
        [str(PYTHON), "-c", "import app.main; import uvicorn"],
        cwd=BACKEND,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        command = (".\\.venv\\Scripts\\python.exe" if IS_WINDOWS else ".venv/bin/python")
        print(
            "Backend dependencies missing or invalid. From backend/ run:\n"
            f"  {command} -m pip install -r requirements.txt\n"
            "Details: " + (result.stderr.strip() or result.stdout.strip())[-1000:],
            file=sys.stderr,
        )
        return False
    return True


def process_options() -> dict:
    """Start separate child groups, so stopping the launcher also stops reloaders."""
    if IS_WINDOWS:
        return {"creationflags": getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x200)}
    return {"start_new_session": True}


def terminate(processes: list[subprocess.Popen]) -> None:
    """Stop both servers *including* Uvicorn/Vite child processes."""
    if IS_WINDOWS:
        for process in processes:
            if process.poll() is None:
                try:
                    process.send_signal(getattr(signal, "CTRL_BREAK_EVENT", 1))
                except (AttributeError, OSError, ValueError):
                    pass
        for process in processes:
            if process.poll() is not None:
                continue
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                # taskkill /T targets the process tree (Uvicorn reload child too).
                subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    check=False,
                )
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
        return

    for process in processes:
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
    for process in processes:
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()


def main() -> int:
    if not prerequisites():
        return 1

    processes: list[subprocess.Popen] = []
    previous_term = signal.getsignal(signal.SIGTERM)

    def handle_term(_signal: int, _frame: object) -> None:
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, handle_term)
    try:
        print("Starting CrimeMap (press Ctrl+C to stop both servers)...", flush=True)
        options = process_options()
        processes.append(subprocess.Popen(
            [str(PYTHON), "-m", "uvicorn", "app.main:app",
             "--reload", "--host", "127.0.0.1", "--port", "8000"],
            cwd=BACKEND, **options,
        ))
        # Calling Vite's Node entrypoint avoids Windows npm.cmd shell quirks,
        # while retaining the same Vite development server configuration.
        node = shutil.which("node")
        processes.append(subprocess.Popen(
            [node, str(VITE_SCRIPT), "--host", "127.0.0.1",
             "--port", "5173", "--strictPort"],
            cwd=FRONTEND, **options,
        ))
        print(
            "\n  Frontend: http://127.0.0.1:5173\n"
            "  API docs: http://127.0.0.1:8000/docs\n"
            "  Backend:  http://127.0.0.1:8000\n"
            "\nLogs from both servers appear below. Ctrl+C stops both.\n",
            flush=True,
        )
        while True:
            for name, process in zip(("Backend", "Frontend"), processes):
                code = process.poll()
                if code is not None:
                    print(
                        f"\n{name} exited with code {code}. Stopping the other server.",
                        file=sys.stderr, flush=True,
                    )
                    return code or 1
            time.sleep(0.25)
    except KeyboardInterrupt:
        print("\nStopping CrimeMap...", flush=True)
        return 0
    except OSError as exc:
        print(f"Failed to start CrimeMap: {exc}", file=sys.stderr)
        return 1
    finally:
        terminate(processes)
        signal.signal(signal.SIGTERM, previous_term)


if __name__ == "__main__":
    sys.exit(main())
