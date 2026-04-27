from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib import request

try:
    from PyQt6.QtCore import QTimer
    from PyQt6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QDialog,
        QDialogButtonBox,
        QFormLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QSpinBox,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "PyQt6 is required for the GUI. Install with: pip install PyQt6"
    ) from exc

# Project root: gui/ is one level below the repo root.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_GUI_SETTINGS_PATH = Path.home() / ".llmr" / "gui.json"
_SERVER_LOG_PATH = Path.home() / ".llmr" / "server.log"

_PROVIDERS = ["openai", "anthropic", "google", "ollama", "cohere", "mistral", "other"]

# How long to wait for the server to start (seconds).
_STARTUP_TIMEOUT = 20


# ── Local settings helpers ────────────────────────────────────────────────────

def _load_gui_settings() -> dict:
    if _GUI_SETTINGS_PATH.exists():
        try:
            return json.loads(_GUI_SETTINGS_PATH.read_text())
        except Exception:
            return {}
    return {}


def _save_gui_settings(data: dict) -> None:
    _GUI_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _GUI_SETTINGS_PATH.write_text(json.dumps(data, indent=2))


# ── Server management ─────────────────────────────────────────────────────────

class ServerManager:
    """Manages the lifecycle of the llm-r server subprocess."""

    def __init__(self) -> None:
        self._proc: subprocess.Popen | None = None
        self._log_file = None

    @property
    def owned(self) -> bool:
        """True when this manager launched the server (vs. it was already running)."""
        return self._proc is not None

    def start(self, base_url: str) -> bool:
        """Launch the server if it is not already running.

        Returns True if a subprocess was started, False if the server was
        already up (in which case we leave it alone).
        """
        if self._ping(base_url):
            return False  # already running — don't touch it

        cmd = self._find_command()
        env = {**os.environ, "LLMR_HOST": "127.0.0.1"}

        _SERVER_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._log_file = open(_SERVER_LOG_PATH, "w")  # noqa: SIM115

        self._proc = subprocess.Popen(
            cmd,
            cwd=str(_PROJECT_ROOT),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=self._log_file,
            stderr=self._log_file,
        )
        return True

    def stop(self) -> None:
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()
        if self._log_file:
            self._log_file.close()
            self._log_file = None

    def crashed(self) -> bool:
        """True if we launched the server but it has since exited unexpectedly."""
        return self._proc is not None and self._proc.poll() is not None

    @staticmethod
    def _ping(base_url: str) -> bool:
        try:
            request.urlopen(f"{base_url}/health", timeout=1)
            return True
        except Exception:
            return False

    @staticmethod
    def _find_command() -> list[str]:
        # PyInstaller bundle: companion binary sits next to the GUI executable.
        if getattr(sys, "frozen", False):
            for name in ("llm-r-server", "llm-r-server.exe"):
                candidate = Path(sys.executable).with_name(name)
                if candidate.exists():
                    return [str(candidate)]

        # Source layout: backend/main.py at the project root.
        backend = _PROJECT_ROOT / "backend" / "main.py"
        if backend.exists():
            return [sys.executable, str(backend)]

        # Fallback: invoke uvicorn directly.
        return [sys.executable, "-m", "uvicorn", "llmr.app:app",
                "--host", "127.0.0.1", "--port", "8787"]


# ── API client ────────────────────────────────────────────────────────────────

@dataclass
class ApiClient:
    base_url: str
    token: str = ""

    def _request(self, method: str, path: str, payload: dict | None = None) -> dict:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = request.Request(
            f"{self.base_url}{path}",
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")
        with request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}

    def plan(self, prompt: str) -> dict:
        return self._request("POST", "/api/plan", {"prompt": prompt})

    def execute(self, plan_id: str, dry_run: bool, approved: bool = False) -> dict:
        return self._request(
            "POST", "/api/execute",
            {"plan_id": plan_id, "dry_run": dry_run, "approved": approved},
        )

    def get_settings(self) -> dict:
        return self._request("GET", "/api/settings")

    def patch_settings(self, data: dict) -> dict:
        return self._request("PATCH", "/api/settings", data)


# ── Settings dialog ───────────────────────────────────────────────────────────

class SettingsDialog(QDialog):
    def __init__(self, client: ApiClient, cached: dict, parent=None) -> None:
        super().__init__(parent)
        self.client = client
        self.setWindowTitle("LLM-r Settings")
        self.setMinimumWidth(440)

        outer = QVBoxLayout()

        conn_box = QGroupBox("Connection")
        conn_form = QFormLayout()
        self.url_edit = QLineEdit(client.base_url)
        self.token_edit = QLineEdit(client.token)
        self.token_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.token_edit.setPlaceholderText("leave empty to disable auth")
        conn_form.addRow("Server URL:", self.url_edit)
        conn_form.addRow("API Token:", self.token_edit)
        conn_box.setLayout(conn_form)

        llm_box = QGroupBox("LLM Provider")
        llm_form = QFormLayout()
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(_PROVIDERS)
        self.provider_combo.setEditable(True)
        self.model_edit = QLineEdit()
        self.model_edit.setPlaceholderText("e.g. gpt-4.1-mini, claude-3-sonnet, llama3")
        llm_form.addRow("Provider:", self.provider_combo)
        llm_form.addRow("Model:", self.model_edit)
        llm_box.setLayout(llm_form)

        abl_box = QGroupBox("Ableton Live (AbletonOSC)")
        abl_form = QFormLayout()
        self.ableton_host_edit = QLineEdit()
        self.ableton_port_spin = QSpinBox()
        self.ableton_port_spin.setRange(1, 65535)
        abl_form.addRow("OSC Host:", self.ableton_host_edit)
        abl_form.addRow("OSC Port:", self.ableton_port_spin)
        abl_box.setLayout(abl_form)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        outer.addWidget(conn_box)
        outer.addWidget(llm_box)
        outer.addWidget(abl_box)
        outer.addWidget(btns)
        self.setLayout(outer)

        self._populate(cached)

    def _populate(self, cached: dict) -> None:
        self.provider_combo.setCurrentText(cached.get("provider", "openai"))
        self.model_edit.setText(cached.get("model", "gpt-4.1-mini"))
        self.ableton_host_edit.setText(cached.get("ableton_host", "127.0.0.1"))
        self.ableton_port_spin.setValue(int(cached.get("ableton_port", 11000)))
        try:
            live = self.client.get_settings()
            self.provider_combo.setCurrentText(live.get("modelito_provider", "openai"))
            self.model_edit.setText(live.get("modelito_model", ""))
            self.ableton_host_edit.setText(live.get("ableton_host", "127.0.0.1"))
            self.ableton_port_spin.setValue(int(live.get("ableton_port", 11000)))
        except Exception:
            pass  # server not reachable yet — keep cached values

    def values(self) -> dict:
        return {
            "base_url": self.url_edit.text().strip().rstrip("/"),
            "token": self.token_edit.text().strip(),
            "provider": self.provider_combo.currentText().strip(),
            "model": self.model_edit.text().strip(),
            "ableton_host": self.ableton_host_edit.text().strip(),
            "ableton_port": self.ableton_port_spin.value(),
        }


# ── Main window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("LLM-r")

        gui_cfg = _load_gui_settings()
        self.client = ApiClient(
            base_url=gui_cfg.get("base_url", os.getenv("LLMR_GUI_API_URL", "http://127.0.0.1:8787")),
            token=gui_cfg.get("token", os.getenv("LLMR_GUI_API_TOKEN", "")),
        )
        self._gui_cfg = gui_cfg
        self.last_plan_id = ""

        # ── Layout ────────────────────────────────────────────────────────
        root = QWidget()
        layout = QVBoxLayout()

        self.prompt = QTextEdit()
        self.prompt.setPlaceholderText("Describe what you want Ableton to do...")

        button_row = QHBoxLayout()
        self.plan_btn = QPushButton("Plan")
        self.execute_btn = QPushButton("Execute")
        self.dry_run = QCheckBox("Dry run")
        self.dry_run.setChecked(True)
        settings_btn = QPushButton("Settings…")
        button_row.addWidget(self.plan_btn)
        button_row.addWidget(self.execute_btn)
        button_row.addWidget(self.dry_run)
        button_row.addStretch()
        button_row.addWidget(settings_btn)

        self.plan_id = QLineEdit()
        self.plan_id.setReadOnly(True)
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        self._status_label = QLabel()

        layout.addWidget(QLabel("Prompt"))
        layout.addWidget(self.prompt)
        layout.addLayout(button_row)
        layout.addWidget(QLabel("Latest Plan ID"))
        layout.addWidget(self.plan_id)
        layout.addWidget(QLabel("Response"))
        layout.addWidget(self.output)
        layout.addWidget(self._status_label)

        root.setLayout(layout)
        self.setCentralWidget(root)

        self.plan_btn.clicked.connect(self.on_plan)
        self.execute_btn.clicked.connect(self.on_execute)
        settings_btn.clicked.connect(self.on_settings)

        # ── Server startup ────────────────────────────────────────────────
        self._server = ServerManager()
        self._startup_elapsed = 0
        self._startup_timer = QTimer(self)
        self._startup_timer.setInterval(500)
        self._startup_timer.timeout.connect(self._poll_server)

        self._set_ready(False)
        already_up = not self._server.start(self.client.base_url)
        if already_up:
            self._set_ready(True)
        else:
            self._status_label.setText("Starting server…")
            self._startup_timer.start()

    # ── Server state ──────────────────────────────────────────────────────────

    def _poll_server(self) -> None:
        self._startup_elapsed += self._startup_timer.interval()

        if self._server.crashed():
            self._startup_timer.stop()
            self._status_label.setText("Server failed to start — check ~/.llmr/server.log")
            QMessageBox.critical(
                self, "Server error",
                f"The server process exited unexpectedly.\n\nSee {_SERVER_LOG_PATH} for details.",
            )
            return

        if ServerManager._ping(self.client.base_url):
            self._startup_timer.stop()
            self._set_ready(True)
            return

        if self._startup_elapsed >= _STARTUP_TIMEOUT * 1000:
            self._startup_timer.stop()
            self._status_label.setText("Server not responding — check ~/.llmr/server.log")
            QMessageBox.critical(
                self, "Server error",
                f"Server did not respond within {_STARTUP_TIMEOUT}s.\n\nSee {_SERVER_LOG_PATH} for details.",
            )

    def _set_ready(self, ready: bool) -> None:
        self.plan_btn.setEnabled(ready)
        self.execute_btn.setEnabled(ready and bool(self.last_plan_id))
        if ready:
            self._status_label.setText("Server ready")

    # ── UI handlers ───────────────────────────────────────────────────────────

    def _show_output(self, payload: dict) -> None:
        self.output.setPlainText(json.dumps(payload, indent=2))

    def on_plan(self) -> None:
        prompt = self.prompt.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Missing prompt", "Please enter a prompt first.")
            return
        try:
            payload = self.client.plan(prompt)
            self.last_plan_id = payload.get("plan_id", "")
            self.plan_id.setText(self.last_plan_id)
            self.execute_btn.setEnabled(bool(self.last_plan_id))
            self._show_output(payload)
        except Exception as exc:
            QMessageBox.critical(self, "Plan failed", str(exc))

    def on_execute(self) -> None:
        if not self.last_plan_id:
            QMessageBox.warning(self, "Missing plan", "Create a plan first.")
            return
        try:
            payload = self.client.execute(self.last_plan_id, dry_run=self.dry_run.isChecked())
            self._show_output(payload)
        except Exception as exc:
            QMessageBox.critical(self, "Execute failed", str(exc))

    def on_settings(self) -> None:
        dlg = SettingsDialog(self.client, self._gui_cfg, parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        vals = dlg.values()

        self.client.base_url = vals["base_url"]
        self.client.token = vals["token"]
        self._gui_cfg = {**vals}
        _save_gui_settings(self._gui_cfg)

        try:
            self.client.patch_settings({
                "modelito_provider": vals["provider"],
                "modelito_model": vals["model"],
                "ableton_host": vals["ableton_host"],
                "ableton_port": vals["ableton_port"],
                "api_token": vals["token"] or None,
            })
        except Exception as exc:
            QMessageBox.warning(
                self, "Settings",
                f"Connection settings saved.\n\n"
                f"Could not push LLM/Ableton settings to the server:\n{exc}",
            )

    def closeEvent(self, event) -> None:
        self._startup_timer.stop()
        if self._server.owned:
            self._server.stop()
        event.accept()


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    app = QApplication([])
    win = MainWindow()
    win.resize(840, 640)
    win.show()
    app.exec()


if __name__ == "__main__":
    main()
