"""Smoke and regression tests for the Windows/Linux/macOS single-command launcher."""
import importlib.util
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "start.py"


def load_launcher():
    assert SCRIPT.is_file()
    spec = importlib.util.spec_from_file_location("crimemap_launcher", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_launcher_uses_repo_relative_paths_and_fixed_ports(monkeypatch):
    launcher = load_launcher()
    assert launcher.ROOT == ROOT
    assert launcher.BACKEND == ROOT / "backend"
    assert launcher.FRONTEND == ROOT / "frontend"
    assert launcher.PYTHON == ROOT / "backend" / ".venv" / (
        "Scripts/python.exe" if launcher.IS_WINDOWS else "bin/python"
    )
    assert launcher.VITE_SCRIPT == ROOT / "frontend/node_modules/vite/bin/vite.js"

    started = []
    stopped = []

    class FakeProcess:
        def __init__(self, args, **kwargs):
            self.pid = 50000 + len(started)
            self.args = args
            self.kwargs = kwargs
            started.append(self)

        def poll(self):
            return None

    monkeypatch.setattr(launcher, "prerequisites", lambda: True)
    monkeypatch.setattr(launcher.subprocess, "Popen", FakeProcess)
    monkeypatch.setattr(launcher.shutil, "which", lambda name: "C:/node/node.exe" if launcher.IS_WINDOWS else "/usr/bin/node")
    monkeypatch.setattr(launcher.time, "sleep", lambda _seconds: (_ for _ in ()).throw(KeyboardInterrupt()))
    monkeypatch.setattr(launcher, "terminate", lambda children: stopped.extend(children))

    assert launcher.main() == 0
    assert len(started) == 2
    assert started[0].kwargs["cwd"] == ROOT / "backend"
    assert started[1].kwargs["cwd"] == ROOT / "frontend"
    assert [str(launcher.PYTHON), "-m", "uvicorn"] == started[0].args[:3]
    assert str(launcher.VITE_SCRIPT) == started[1].args[1]
    assert ["--port", "8000"] == started[0].args[-2:]
    assert "--strictPort" in started[1].args
    assert "5173" in started[1].args
    if launcher.IS_WINDOWS:
        assert "creationflags" in started[0].kwargs
        assert "creationflags" in started[1].kwargs
    else:
        assert started[0].kwargs["start_new_session"] is True
        assert started[1].kwargs["start_new_session"] is True
    assert stopped == started


def test_launcher_reports_missing_backend_environment(monkeypatch, tmp_path, capsys):
    launcher = load_launcher()
    monkeypatch.setattr(launcher, "PYTHON", tmp_path / "missing" / "python")
    assert launcher.prerequisites() is False
    output = capsys.readouterr()
    assert ("py -3 -m venv .venv" if launcher.IS_WINDOWS else "python3 -m venv .venv") in output.err


def test_platform_specific_process_groups(monkeypatch):
    launcher = load_launcher()
    monkeypatch.setattr(launcher, "IS_WINDOWS", True)
    assert launcher.process_options() == {
        "creationflags": getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x200)
    }
    assert "Scripts" in launcher.setup_commands()
    monkeypatch.setattr(launcher, "IS_WINDOWS", False)
    assert launcher.process_options() == {"start_new_session": True}
    assert "bin/python" in launcher.setup_commands()


def test_windows_cleanup_sends_break_then_kills_stuck_process_tree(monkeypatch):
    launcher = load_launcher()
    monkeypatch.setattr(launcher, "IS_WINDOWS", True)
    calls = []

    class FakeChild:
        pid = 1091

        def poll(self):
            return None

        def send_signal(self, sig):
            calls.append(("break", sig))

        def wait(self, timeout=None):
            calls.append(("wait", timeout))
            if timeout == 3:
                raise subprocess.TimeoutExpired("backend", timeout)
            return 0

        def kill(self):
            calls.append(("kill",))

    monkeypatch.setattr(launcher.subprocess, "run",
                        lambda cmd, **kwargs: calls.append(("taskkill", cmd)))
    launcher.terminate([FakeChild()])
    assert calls[0][0] == "break"
    assert calls[1] == ("wait", 3)
    assert calls[2] == ("taskkill", ["taskkill", "/PID", "1091", "/T", "/F"])
    assert calls[3] == ("wait", 2)
    assert not any(call[0] == "kill" for call in calls)
