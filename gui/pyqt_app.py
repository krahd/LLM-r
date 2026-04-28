from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib import request

try:
    from PyQt6.QtCore import QThread, pyqtSignal
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

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_GUI_SETTINGS_PATH = Path.home() / ".llmr" / "gui.json"

_PROVIDERS = ["openai", "anthropic", "google", "ollama", "cohere", "mistral", "other"]

# Ensure llmr is importable when running from the source tree.
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


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


# ── Backend interface ─────────────────────────────────────────────────────────

class Backend:
    """Common interface implemented by both HttpBackend and EmbeddedBackend."""

    def plan(self, prompt: str) -> dict:
        raise NotImplementedError

    def execute(self, plan_id: str, dry_run: bool, approved: bool = False) -> dict:
        raise NotImplementedError

    def get_settings(self) -> dict:
        raise NotImplementedError

    def patch_settings(self, data: dict) -> dict:
        raise NotImplementedError


# ── HTTP backend ──────────────────────────────────────────────────────────────

class HttpBackend(Backend):
    """Delegates to a running LLM-r server over HTTP."""

    def __init__(self, base_url: str, token: str = "") -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token

    def _request(self, method: str, path: str, payload: dict | None = None) -> dict:
        data = json.dumps(payload).encode() if payload is not None else None
        req = request.Request(
            f"{self.base_url}{path}",
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")
        with request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
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


# ── Embedded backend ──────────────────────────────────────────────────────────

class EmbeddedBackend(Backend):
    """Runs LLM planning and OSC execution in-process — no server needed."""

    def __init__(self) -> None:
        from llmr.config import settings
        from llmr.macros import init_macro_store
        from llmr.planner import PlanStore

        self._settings = settings
        self._store = PlanStore(persist_path=settings.plan_store_path)
        init_macro_store(settings.macro_store_path)

    def _build_planner(self):
        from llmr.ableton_osc import AbletonOSCClient
        from llmr.modelito_adapter import ModelitoClient
        from llmr.planner import IntentPlanner

        return IntentPlanner(
            llm=ModelitoClient(
                provider=self._settings.modelito_provider,
                model=self._settings.modelito_model,
            ),
            ableton=AbletonOSCClient(
                self._settings.ableton_host,
                self._settings.ableton_port,
            ),
        )

    def plan(self, prompt: str) -> dict:
        planner = self._build_planner()
        plan = planner.plan(prompt.strip())
        self._store.put(plan)
        return {
            "plan_id": plan.id,
            "prompt": plan.prompt,
            "explanation": plan.explanation,
            "confidence": plan.confidence,
            "requires_approval": plan.requires_approval,
            "created_at": plan.created_at,
            "executed_at": plan.executed_at,
            "planned_actions": [
                {
                    "tool": a.tool.value,
                    "address": a.address,
                    "args": a.args,
                    "description": a.description,
                    "destructive": a.destructive,
                }
                for a in plan.actions
            ],
            "llm_raw": plan.llm_raw,
        }

    def execute(self, plan_id: str, dry_run: bool, approved: bool = False) -> dict:
        from llmr.executor import execute_actions

        plan = self._store.get(plan_id)
        if plan is None:
            raise ValueError("Plan not found or expired")
        if plan.executed_at:
            raise ValueError("Plan already executed")

        try:
            report, _ = execute_actions(
                plan.actions,
                ableton_host=self._settings.ableton_host,
                ableton_port=self._settings.ableton_port,
                approved=approved,
                dry_run=dry_run,
            )
        except PermissionError as exc:
            raise ValueError(str(exc)) from exc

        if not dry_run:
            plan = self._store.mark_executed(plan.id) or plan

        return {
            "plan_id": plan.id,
            "dry_run": dry_run,
            "executed_at": plan.executed_at,
            "requires_approval": plan.requires_approval,
            "executed_count": len(plan.actions),
            "execution_report": report,
        }

    def get_settings(self) -> dict:
        s = self._settings
        return {
            "modelito_provider": s.modelito_provider,
            "modelito_model": s.modelito_model,
            "ableton_host": s.ableton_host,
            "ableton_port": int(s.ableton_port),
        }

    def patch_settings(self, data: dict) -> dict:
        s = self._settings
        if data.get("modelito_provider"):
            s.modelito_provider = data["modelito_provider"]
        if data.get("modelito_model"):
            s.modelito_model = data["modelito_model"]
        if data.get("ableton_host"):
            s.ableton_host = data["ableton_host"]
        if data.get("ableton_port"):
            s.ableton_port = int(data["ableton_port"])
        if "api_token" in data:
            s.api_token = data.get("api_token") or ""
        s.save()
        return self.get_settings()


# ── Backend selection ─────────────────────────────────────────────────────────

def _ping(url: str) -> bool:
    try:
        request.urlopen(f"{url.rstrip('/')}/health", timeout=1)
        return True
    except Exception:
        return False


def _choose_backend(base_url: str, token: str) -> tuple[Backend, str]:
    """Return (backend, status_text). Prefers a live server; falls back to embedded."""
    if _ping(base_url):
        return HttpBackend(base_url=base_url, token=token), f"Server: {base_url}"
    return EmbeddedBackend(), "Embedded mode"


# ── Background workers ────────────────────────────────────────────────────────

class _PlanWorker(QThread):
    finished: pyqtSignal = pyqtSignal(dict)
    error: pyqtSignal = pyqtSignal(str)

    def __init__(self, backend: Backend, prompt: str) -> None:
        super().__init__()
        self._backend = backend
        self._prompt = prompt

    def run(self) -> None:
        try:
            self.finished.emit(self._backend.plan(self._prompt))
        except Exception as exc:
            self.error.emit(str(exc))


class _ExecuteWorker(QThread):
    finished: pyqtSignal = pyqtSignal(dict)
    error: pyqtSignal = pyqtSignal(str)

    def __init__(
        self, backend: Backend, plan_id: str, dry_run: bool, approved: bool,
    ) -> None:
        super().__init__()
        self._backend = backend
        self._plan_id = plan_id
        self._dry_run = dry_run
        self._approved = approved

    def run(self) -> None:
        try:
            self.finished.emit(
                self._backend.execute(self._plan_id, self._dry_run, self._approved)
            )
        except Exception as exc:
            self.error.emit(str(exc))


# ── Settings dialog ───────────────────────────────────────────────────────────

class SettingsDialog(QDialog):
    def __init__(self, backend: Backend, cached: dict, parent=None) -> None:
        super().__init__(parent)
        self._backend = backend
        self.setWindowTitle("LLM-r Settings")
        self.setMinimumWidth(440)

        outer = QVBoxLayout()

        conn_box = QGroupBox("Server Connection")
        conn_form = QFormLayout()
        self.url_edit = QLineEdit(cached.get("base_url", "http://127.0.0.1:8787"))
        self.token_edit = QLineEdit(cached.get("token", ""))
        self.token_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.token_edit.setPlaceholderText("leave empty to disable auth")
        note = QLabel(
            "When a server is reachable at this URL the GUI connects to it;"
            " otherwise it runs embedded."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: gray; font-size: 11px;")
        conn_form.addRow("Server URL:", self.url_edit)
        conn_form.addRow("API Token:", self.token_edit)
        conn_form.addRow(note)
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
            live = self._backend.get_settings()
            self.provider_combo.setCurrentText(live.get("modelito_provider", "openai"))
            self.model_edit.setText(live.get("modelito_model", ""))
            self.ableton_host_edit.setText(live.get("ableton_host", "127.0.0.1"))
            self.ableton_port_spin.setValue(int(live.get("ableton_port", 11000)))
        except Exception:
            pass  # keep cached values if backend is unreachable

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

        self._gui_cfg = _load_gui_settings()
        self.last_plan_id = ""
        self._worker: QThread | None = None

        base_url = self._gui_cfg.get(
            "base_url", os.getenv("LLMR_GUI_API_URL", "http://127.0.0.1:8787")
        )
        token = self._gui_cfg.get("token", os.getenv("LLMR_GUI_API_TOKEN", ""))
        self._backend, mode = _choose_backend(base_url, token)

        # ── Layout ─────────────────────────────────────────────────────────
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

        self._status_label = QLabel(mode)

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

        self.execute_btn.setEnabled(False)

    # ── UI helpers ────────────────────────────────────────────────────────────

    def _show_output(self, payload: dict) -> None:
        self.output.setPlainText(json.dumps(payload, indent=2))

    def _set_busy(self, busy: bool) -> None:
        self.plan_btn.setEnabled(not busy)
        self.execute_btn.setEnabled(not busy and bool(self.last_plan_id))

    # ── Plan ──────────────────────────────────────────────────────────────────

    def on_plan(self) -> None:
        prompt = self.prompt.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Missing prompt", "Please enter a prompt first.")
            return
        self._set_busy(True)
        self._status_label.setText("Planning…")
        self._worker = _PlanWorker(self._backend, prompt)
        self._worker.finished.connect(self._on_plan_done)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.start()

    def _on_plan_done(self, payload: dict) -> None:
        self.last_plan_id = payload.get("plan_id", "")
        self.plan_id.setText(self.last_plan_id)
        self._show_output(payload)
        self._set_busy(False)
        self._status_label.setText("Plan ready — review and execute")

    # ── Execute ───────────────────────────────────────────────────────────────

    def on_execute(self) -> None:
        if not self.last_plan_id:
            QMessageBox.warning(self, "Missing plan", "Create a plan first.")
            return
        self._set_busy(True)
        self._status_label.setText("Executing…")
        self._worker = _ExecuteWorker(
            self._backend,
            self.last_plan_id,
            dry_run=self.dry_run.isChecked(),
            approved=False,
        )
        self._worker.finished.connect(self._on_execute_done)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.start()

    def _on_execute_done(self, payload: dict) -> None:
        self._show_output(payload)
        self._set_busy(False)
        label = "Dry run complete" if payload.get("dry_run") else "Executed"
        self._status_label.setText(label)

    # ── Error ─────────────────────────────────────────────────────────────────

    def _on_error(self, message: str) -> None:
        self._set_busy(False)
        self._status_label.setText("Error")
        QMessageBox.critical(self, "Error", message)

    # ── Settings ──────────────────────────────────────────────────────────────

    def on_settings(self) -> None:
        dlg = SettingsDialog(self._backend, self._gui_cfg, parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        vals = dlg.values()
        self._gui_cfg = {**vals}
        _save_gui_settings(self._gui_cfg)

        # Re-detect backend: if the new URL has a live server, switch to HTTP.
        self._backend, mode = _choose_backend(vals["base_url"], vals["token"])
        self._status_label.setText(mode)

        try:
            self._backend.patch_settings({
                "modelito_provider": vals["provider"],
                "modelito_model": vals["model"],
                "ableton_host": vals["ableton_host"],
                "ableton_port": vals["ableton_port"],
                "api_token": vals["token"] or None,
            })
        except Exception as exc:
            QMessageBox.warning(
                self, "Settings",
                f"Connection settings saved.\n\nCould not push LLM/Ableton settings:\n{exc}",
            )


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    app = QApplication([])
    win = MainWindow()
    win.resize(840, 640)
    win.show()
    app.exec()


if __name__ == "__main__":
    main()
