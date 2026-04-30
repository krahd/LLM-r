from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib import parse, request

try:
    from PyQt6.QtCore import QThread, QTimer, Qt, pyqtSignal
    from PyQt6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QDialog,
        QDialogButtonBox,
        QFileDialog,
        QFormLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QScrollArea,
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

    def get_modelito_models(self, provider: str = "", model: str = "") -> dict:
        raise NotImplementedError

    def ollama(self, action: str, model: str = "") -> dict:
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

    def get_modelito_models(self, provider: str = "", model: str = "") -> dict:
        query = parse.urlencode({k: v for k, v in {"provider": provider, "model": model}.items() if v})
        path = f"/api/modelito/models?{query}" if query else "/api/modelito/models"
        return self._request("GET", path)

    def ollama(self, action: str, model: str = "") -> dict:
        read_paths = {
            "status": "/api/ollama/status",
            "local_models": "/api/ollama/local_models",
            "remote_models": "/api/ollama/remote_models",
        }
        if action in read_paths:
            return self._request("GET", read_paths[action])
        if action in {"start", "stop", "install"}:
            return self._request("POST", f"/api/ollama/{action}", {})
        if action in {"download", "delete", "serve"}:
            return self._request("POST", f"/api/ollama/{action}", {"model": model})
        raise ValueError(f"Unknown Ollama action: {action}")


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
        from llmr.prompts import planner_extra_prompt

        return IntentPlanner(
            llm=ModelitoClient(
                provider=self._settings.modelito_provider,
                model=self._settings.modelito_model,
            ),
            ableton=AbletonOSCClient(
                self._settings.ableton_host,
                self._settings.ableton_port,
            ),
            extra_prompt=planner_extra_prompt(self._settings),
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
            "planner_extra_prompt_enabled": s.planner_extra_prompt_enabled,
            "planner_extra_prompt_path": s.planner_extra_prompt_path,
            "ableton_host": s.ableton_host,
            "ableton_port": int(s.ableton_port),
        }

    def patch_settings(self, data: dict) -> dict:
        s = self._settings
        if data.get("modelito_provider"):
            s.modelito_provider = data["modelito_provider"]
        if data.get("modelito_model"):
            s.modelito_model = data["modelito_model"]
        if "planner_extra_prompt_enabled" in data:
            s.planner_extra_prompt_enabled = bool(data["planner_extra_prompt_enabled"])
        if "planner_extra_prompt_path" in data:
            s.planner_extra_prompt_path = data.get("planner_extra_prompt_path") or ""
        if data.get("ableton_host"):
            s.ableton_host = data["ableton_host"]
        if data.get("ableton_port"):
            s.ableton_port = int(data["ableton_port"])
        if "api_token" in data:
            s.api_token = data.get("api_token") or ""
        s.save()
        return self.get_settings()

    def get_modelito_models(self, provider: str = "", model: str = "") -> dict:
        from llmr.modelito_adapter import modelito_models

        current_provider = provider or self._settings.modelito_provider
        current_model = model or self._settings.modelito_model
        return {
            "provider": current_provider,
            "default_model": current_model,
            "models": modelito_models(current_provider, current_model),
        }

    def ollama(self, action: str, model: str = "") -> dict:
        from llmr import modelito_adapter

        actions = {
            "status": lambda: modelito_adapter.ollama_status(),
            "local_models": lambda: modelito_adapter.ollama_local_models(),
            "remote_models": lambda: modelito_adapter.ollama_remote_models(),
            "start": lambda: modelito_adapter.ollama_start(),
            "stop": lambda: modelito_adapter.ollama_stop(),
            "install": lambda: modelito_adapter.ollama_install(),
            "download": lambda: modelito_adapter.ollama_download(model),
            "delete": lambda: modelito_adapter.ollama_delete(model),
            "serve": lambda: modelito_adapter.ollama_serve(model),
        }
        if action not in actions:
            raise ValueError(f"Unknown Ollama action: {action}")
        return actions[action]()


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


class _ActionWorker(QThread):
    finished: pyqtSignal = pyqtSignal(dict)
    error: pyqtSignal = pyqtSignal(str)

    def __init__(self, fn) -> None:
        super().__init__()
        self._fn = fn

    def run(self) -> None:
        try:
            self.finished.emit(self._fn())
        except Exception as exc:
            self.error.emit(str(exc))


# ── Server start watcher ──────────────────────────────────────────────────────

class _ServerStartWatcher(QThread):
    ready: pyqtSignal = pyqtSignal()
    failed: pyqtSignal = pyqtSignal(str)

    def __init__(self, url: str, timeout: int = 20) -> None:
        super().__init__()
        self._url = url
        self._timeout = timeout

    def run(self) -> None:
        deadline = time.monotonic() + self._timeout
        while time.monotonic() < deadline:
            if _ping(self._url):
                self.ready.emit()
                return
            time.sleep(0.4)
        self.failed.emit("Server did not respond within timeout")


# ── Settings dialog ───────────────────────────────────────────────────────────

class SettingsDialog(QDialog):
    def __init__(self, backend: Backend, cached: dict, parent=None) -> None:
        super().__init__(parent)
        self._backend = backend
        self._workers: list[_ActionWorker] = []
        self.setWindowTitle("LLM-r Settings")
        self.setMinimumSize(560, 520)
        self.resize(680, 720)

        outer = QVBoxLayout()
        scroller = QScrollArea()
        scroller.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout()

        conn_box = QGroupBox("Server Connection")
        conn_form = QFormLayout()
        self.url_edit = QLineEdit(cached.get("base_url", "http://127.0.0.1:8787"))
        self.token_edit = QLineEdit(cached.get("token", ""))
        self.token_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.token_edit.setPlaceholderText("leave empty to disable auth")
        self.url_edit.setClearButtonEnabled(True)
        self.token_edit.setClearButtonEnabled(True)
        self.check_connection_btn = QPushButton("Check")
        self.show_token_check = QCheckBox("Show")
        self.connection_status = QLabel("Not checked")
        self.connection_status.setWordWrap(True)
        url_row = QHBoxLayout()
        url_row.addWidget(self.url_edit, stretch=1)
        url_row.addWidget(self.check_connection_btn)
        token_row = QHBoxLayout()
        token_row.addWidget(self.token_edit, stretch=1)
        token_row.addWidget(self.show_token_check)
        note = QLabel(
            "When a server is reachable at this URL the GUI connects to it;"
            " otherwise it runs embedded."
        )
        note.setWordWrap(True)
        conn_form.addRow("Server URL:", url_row)
        conn_form.addRow("API Token:", token_row)
        conn_form.addRow("Status:", self.connection_status)
        conn_form.addRow(note)
        conn_box.setLayout(conn_form)

        llm_box = QGroupBox("LLM Provider")
        llm_form = QFormLayout()
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(_PROVIDERS)
        self.provider_combo.setEditable(True)
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.model_combo.lineEdit().setPlaceholderText("e.g. gpt-4.1-mini, claude-3-sonnet, llama3")
        self.model_combo.setMinimumContentsLength(24)
        model_row = QHBoxLayout()
        model_row.addWidget(self.model_combo, stretch=1)
        self.refresh_models_btn = QPushButton("Refresh Models")
        model_row.addWidget(self.refresh_models_btn)
        llm_form.addRow("Provider:", self.provider_combo)
        llm_form.addRow("Model:", model_row)
        self.model_status = QLabel("Model list not loaded")
        self.model_status.setWordWrap(True)
        llm_form.addRow("Model list:", self.model_status)
        llm_box.setLayout(llm_form)

        planner_box = QGroupBox("Planner Guidance")
        planner_form = QFormLayout()
        self.extra_prompt_enabled = QCheckBox("Send LLM-r assistant prompt to the LLM")
        self.extra_prompt_path_edit = QLineEdit()
        self.extra_prompt_path_edit.setPlaceholderText("Path to optional planner prompt")
        self.extra_prompt_path_edit.setClearButtonEnabled(True)
        self.prompt_browse_btn = QPushButton("Browse")
        prompt_row = QHBoxLayout()
        prompt_row.addWidget(self.extra_prompt_path_edit, stretch=1)
        prompt_row.addWidget(self.prompt_browse_btn)
        planner_note = QLabel(
            "Enabled by default. Disable this if you want the model to use only"
            " the generated tool catalog."
        )
        planner_note.setWordWrap(True)
        planner_form.addRow(self.extra_prompt_enabled)
        planner_form.addRow("Prompt file:", prompt_row)
        planner_form.addRow(planner_note)
        planner_box.setLayout(planner_form)

        safety_box = QGroupBox("Execution Defaults")
        safety_form = QFormLayout()
        self.dry_run_default = QCheckBox("Dry run new executions")
        self.allow_destructive = QCheckBox("Allow destructive execution after review")
        safety_form.addRow(self.dry_run_default)
        safety_form.addRow(self.allow_destructive)
        safety_box.setLayout(safety_form)

        abl_box = QGroupBox("Ableton Live (AbletonOSC)")
        abl_form = QFormLayout()
        self.ableton_host_edit = QLineEdit()
        self.ableton_port_spin = QSpinBox()
        self.ableton_port_spin.setRange(1, 65535)
        abl_form.addRow("OSC Host:", self.ableton_host_edit)
        abl_form.addRow("OSC Port:", self.ableton_port_spin)
        abl_box.setLayout(abl_form)

        ollama_box = QGroupBox("Ollama / Modelito")
        ollama_layout = QVBoxLayout()
        self.ollama_status = QLabel("Status has not been checked yet.")
        self.ollama_status.setWordWrap(True)
        ollama_controls = QHBoxLayout()
        self.ollama_install_btn = QPushButton("Install")
        self.ollama_start_btn = QPushButton("Start")
        self.ollama_stop_btn = QPushButton("Stop")
        self.ollama_refresh_btn = QPushButton("Check Status")
        for button in (
            self.ollama_install_btn,
            self.ollama_start_btn,
            self.ollama_stop_btn,
            self.ollama_refresh_btn,
        ):
            ollama_controls.addWidget(button)

        local_form = QFormLayout()
        self.local_models_combo = QComboBox()
        self.local_models_combo.setEditable(True)
        self.local_models_combo.setMinimumContentsLength(24)
        local_actions = QHBoxLayout()
        self.serve_model_btn = QPushButton("Use + Serve")
        self.delete_model_btn = QPushButton("Delete")
        local_actions.addWidget(self.serve_model_btn)
        local_actions.addWidget(self.delete_model_btn)
        local_form.addRow("Local models:", self.local_models_combo)
        local_form.addRow(local_actions)

        remote_form = QFormLayout()
        self.remote_models_combo = QComboBox()
        self.remote_models_combo.setEditable(True)
        self.remote_models_combo.setMinimumContentsLength(24)
        self.remote_models_combo.lineEdit().setPlaceholderText("llama3, mistral, codellama")
        remote_actions = QHBoxLayout()
        self.list_remote_btn = QPushButton("List Online")
        self.download_model_btn = QPushButton("Download")
        remote_actions.addWidget(self.list_remote_btn)
        remote_actions.addWidget(self.download_model_btn)
        remote_form.addRow("Online models:", self.remote_models_combo)
        remote_form.addRow(remote_actions)

        self.ollama_log = QTextEdit()
        self.ollama_log.setReadOnly(True)
        self.ollama_log.setMaximumHeight(120)
        self.ollama_log.setPlaceholderText("Ollama action details")
        ollama_layout.addWidget(self.ollama_status)
        ollama_layout.addLayout(ollama_controls)
        ollama_layout.addLayout(local_form)
        ollama_layout.addLayout(remote_form)
        ollama_layout.addWidget(self.ollama_log)
        ollama_box.setLayout(ollama_layout)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        content_layout.addWidget(conn_box)
        content_layout.addWidget(llm_box)
        content_layout.addWidget(planner_box)
        content_layout.addWidget(safety_box)
        content_layout.addWidget(abl_box)
        content_layout.addWidget(ollama_box)
        content_layout.addStretch()
        content.setLayout(content_layout)
        scroller.setWidget(content)
        outer.addWidget(scroller)
        outer.addWidget(btns)
        self.setLayout(outer)

        self.check_connection_btn.clicked.connect(self._check_connection)
        self.show_token_check.toggled.connect(self._toggle_token_visibility)
        self.refresh_models_btn.clicked.connect(self._populate_model_list)
        self.provider_combo.currentIndexChanged.connect(lambda *_: self._populate_model_list())
        self.prompt_browse_btn.clicked.connect(self._browse_prompt_file)
        self.ollama_refresh_btn.clicked.connect(self._refresh_ollama)
        self.list_remote_btn.clicked.connect(self._load_remote_models)
        self.ollama_start_btn.clicked.connect(lambda: self._run_ollama_action("start"))
        self.ollama_stop_btn.clicked.connect(lambda: self._run_ollama_action("stop"))
        self.ollama_install_btn.clicked.connect(lambda: self._run_ollama_action("install"))
        self.download_model_btn.clicked.connect(self._download_selected_model)
        self.delete_model_btn.clicked.connect(self._delete_selected_model)
        self.serve_model_btn.clicked.connect(self._serve_selected_model)

        self._configure_accessibility()
        self._populate(cached)
        self._toggle_token_visibility(self.show_token_check.isChecked())
        self._check_connection()
        self._populate_model_list()
        self._refresh_ollama()

    def _populate(self, cached: dict) -> None:
        signals_blocked = self.provider_combo.blockSignals(True)
        self.provider_combo.setCurrentText(cached.get("provider", "openai"))
        self.model_combo.setCurrentText(cached.get("model", "gpt-4.1-mini"))
        self.extra_prompt_enabled.setChecked(
            bool(cached.get("planner_extra_prompt_enabled", True))
        )
        self.extra_prompt_path_edit.setText(cached.get("planner_extra_prompt_path", ""))
        self.dry_run_default.setChecked(bool(cached.get("dry_run", True)))
        self.allow_destructive.setChecked(bool(cached.get("allow_destructive", False)))
        self.ableton_host_edit.setText(cached.get("ableton_host", "127.0.0.1"))
        self.ableton_port_spin.setValue(int(cached.get("ableton_port", 11000)))
        try:
            live = self._backend.get_settings()
            self.provider_combo.setCurrentText(live.get("modelito_provider", "openai"))
            self.model_combo.setCurrentText(live.get("modelito_model", ""))
            self.extra_prompt_enabled.setChecked(
                bool(live.get("planner_extra_prompt_enabled", True))
            )
            self.extra_prompt_path_edit.setText(live.get("planner_extra_prompt_path", ""))
            self.ableton_host_edit.setText(live.get("ableton_host", "127.0.0.1"))
            self.ableton_port_spin.setValue(int(live.get("ableton_port", 11000)))
        except Exception:
            pass  # keep cached values if backend is unreachable
        finally:
            self.provider_combo.blockSignals(signals_blocked)

    def _configure_accessibility(self) -> None:
        described_widgets = {
            self.url_edit: (
                "Server URL",
                "LLM-r HTTP server URL. If unreachable, the GUI uses embedded mode.",
            ),
            self.token_edit: (
                "API token",
                "Bearer token used for protected server actions.",
            ),
            self.provider_combo: (
                "LLM provider",
                "Provider name passed to Modelito.",
            ),
            self.model_combo: (
                "LLM model",
                "Model identifier used for planning.",
            ),
            self.extra_prompt_enabled: (
                "Assistant prompt guidance",
                "Toggle additional LLM-r planning guidance.",
            ),
            self.extra_prompt_path_edit: (
                "Planner prompt file",
                "Optional path to an additional planner prompt file.",
            ),
            self.dry_run_default: (
                "Dry run by default",
                "New executions preview OSC messages before sending them.",
            ),
            self.allow_destructive: (
                "Allow destructive execution",
                "Allows non-dry-run execution of destructive plans after review.",
            ),
            self.ableton_host_edit: (
                "Ableton OSC host",
                "Host for AbletonOSC.",
            ),
            self.ableton_port_spin: (
                "Ableton OSC port",
                "Port for AbletonOSC.",
            ),
            self.local_models_combo: (
                "Local Ollama models",
                "Installed Ollama model picker.",
            ),
            self.remote_models_combo: (
                "Online Ollama models",
                "Ollama model name to download.",
            ),
            self.ollama_log: (
                "Ollama action log",
                "Details from recent Ollama operations.",
            ),
        }
        for widget, (name, description) in described_widgets.items():
            widget.setAccessibleName(name)
            widget.setAccessibleDescription(description)
            widget.setToolTip(description)

        button_tips = {
            self.check_connection_btn: "Check whether the configured server is reachable.",
            self.show_token_check: "Show or hide the API token text.",
            self.refresh_models_btn: "Reload model IDs for the selected provider.",
            self.prompt_browse_btn: "Choose a planner prompt file.",
            self.ollama_install_btn: "Install Ollama through Modelito.",
            self.ollama_start_btn: "Start the local Ollama service.",
            self.ollama_stop_btn: "Stop the local Ollama service.",
            self.ollama_refresh_btn: "Check Ollama installation and service status.",
            self.list_remote_btn: "Load available online Ollama model names.",
            self.download_model_btn: "Download the selected online Ollama model.",
            self.delete_model_btn: "Delete the selected local Ollama model.",
            self.serve_model_btn: "Serve the selected local model and use it for planning.",
        }
        for button, tip in button_tips.items():
            button.setAccessibleDescription(tip)
            button.setToolTip(tip)

    def _toggle_token_visibility(self, visible: bool) -> None:
        mode = QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password
        self.token_edit.setEchoMode(mode)

    def _browse_prompt_file(self) -> None:
        current = self.extra_prompt_path_edit.text().strip()
        start = str(Path(current).expanduser().parent) if current else str(_PROJECT_ROOT)
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Planner Prompt",
            start,
            "Prompt files (*.md *.txt);;All files (*)",
        )
        if path:
            self.extra_prompt_path_edit.setText(path)

    def _check_connection(self) -> None:
        url = self.url_edit.text().strip().rstrip("/")
        if not url:
            self.connection_status.setText("Enter a server URL.")
            return
        self.connection_status.setText("Checking...")

        def success(payload: dict) -> None:
            if payload.get("ok"):
                self.connection_status.setText("Server reachable. HTTP mode will be used.")
            else:
                self.connection_status.setText("Server unreachable. Embedded mode will be used.")

        self._run_backend(
            lambda: {"ok": _ping(url)},
            success,
            on_error=lambda msg: self.connection_status.setText(f"Check failed: {msg}"),
            buttons=(self.check_connection_btn,),
        )

    def _append_ollama_log(self, message: str) -> None:
        self.ollama_log.append(message)

    def _ollama_buttons(self) -> tuple[QPushButton, ...]:
        return (
            self.ollama_install_btn,
            self.ollama_start_btn,
            self.ollama_stop_btn,
            self.ollama_refresh_btn,
            self.list_remote_btn,
            self.download_model_btn,
            self.delete_model_btn,
            self.serve_model_btn,
        )

    def _run_backend(self, fn, on_success, *, on_error=None, buttons=()) -> None:
        worker = _ActionWorker(fn)
        self._workers.append(worker)
        busy_buttons = tuple(buttons)
        for button in busy_buttons:
            button.setEnabled(False)

        def cleanup() -> None:
            if worker in self._workers:
                self._workers.remove(worker)
            for button in busy_buttons:
                button.setEnabled(True)
            worker.deleteLater()

        worker.finished.connect(on_success)
        worker.finished.connect(lambda *_: cleanup())
        worker.error.connect(on_error or self._on_ollama_error)
        worker.error.connect(lambda *_: cleanup())
        worker.start()

    def _populate_model_list(self) -> None:
        current = self.model_combo.currentText().strip()
        provider = self.provider_combo.currentText().strip()
        self.model_status.setText("Loading model list...")

        def success(payload: dict) -> None:
            models = [str(m) for m in payload.get("models", []) if str(m).strip()]
            self.model_combo.clear()
            self.model_combo.addItems(models)
            self.model_combo.setCurrentText(current or payload.get("default_model", ""))
            provider_name = payload.get("provider") or provider or "provider"
            self.model_status.setText(f"{len(models)} model(s) loaded for {provider_name}.")

        self._run_backend(
            lambda: self._backend.get_modelito_models(provider, current),
            success,
            on_error=lambda msg: self.model_status.setText(f"Model list unavailable: {msg}"),
            buttons=(self.refresh_models_btn,),
        )

    def _refresh_ollama(self) -> None:
        def success(payload: dict) -> None:
            self.ollama_status.setText(payload.get("message", "Ollama status refreshed."))
            self._append_ollama_log(json.dumps(payload, indent=2))
            QTimer.singleShot(0, self._load_local_models)

        self._run_backend(
            lambda: self._backend.ollama("status"),
            success,
            buttons=self._ollama_buttons(),
        )

    def _load_local_models(self) -> None:
        def success(payload: dict) -> None:
            models = [str(m) for m in payload.get("models", []) if str(m).strip()]
            current = self.local_models_combo.currentText().strip()
            self.local_models_combo.clear()
            self.local_models_combo.addItems(models)
            if current:
                self.local_models_combo.setCurrentText(current)
            elif models:
                self.local_models_combo.setCurrentText(models[0])
            self.ollama_status.setText(payload.get("message", "Local models refreshed."))

        self._run_backend(
            lambda: self._backend.ollama("local_models"),
            success,
            buttons=self._ollama_buttons(),
        )

    def _load_remote_models(self) -> None:
        def success(payload: dict) -> None:
            models = [str(m) for m in payload.get("models", []) if str(m).strip()]
            current = self.remote_models_combo.currentText().strip()
            self.remote_models_combo.clear()
            self.remote_models_combo.addItems(models)
            if current:
                self.remote_models_combo.setCurrentText(current)
            elif models:
                self.remote_models_combo.setCurrentText(models[0])
            self.ollama_status.setText(payload.get("message", "Online models refreshed."))

        self._run_backend(
            lambda: self._backend.ollama("remote_models"),
            success,
            buttons=self._ollama_buttons(),
        )

    def _run_ollama_action(self, action: str, model: str = "") -> None:
        self.ollama_status.setText(f"Running {action}...")

        def success(payload: dict) -> None:
            self.ollama_status.setText(payload.get("message", f"{action} complete."))
            self._append_ollama_log(json.dumps(payload, indent=2))
            if action in {"start", "stop", "install", "download", "delete", "serve"}:
                QTimer.singleShot(0, self._load_local_models)

        self._run_backend(
            lambda: self._backend.ollama(action, model),
            success,
            buttons=self._ollama_buttons(),
        )

    def _download_selected_model(self) -> None:
        model = self.remote_models_combo.currentText().strip()
        if not model:
            self.ollama_status.setText("Choose an online model to download.")
            return
        self._run_ollama_action("download", model)

    def _delete_selected_model(self) -> None:
        model = self.local_models_combo.currentText().strip()
        if not model:
            self.ollama_status.setText("Choose a local model to delete.")
            return
        confirm = QMessageBox.question(
            self,
            "Delete Ollama Model",
            f"Delete local Ollama model '{model}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self._run_ollama_action("delete", model)

    def _serve_selected_model(self) -> None:
        model = self.local_models_combo.currentText().strip()
        if not model:
            self.ollama_status.setText("Choose a local model to serve.")
            return
        self.model_combo.setCurrentText(model)
        self.provider_combo.setCurrentText("ollama")
        self._run_ollama_action("serve", model)

    def _on_ollama_error(self, message: str) -> None:
        self.ollama_status.setText("Ollama action failed.")
        self._append_ollama_log(message)

    def values(self) -> dict:
        return {
            "base_url": self.url_edit.text().strip().rstrip("/"),
            "token": self.token_edit.text().strip(),
            "provider": self.provider_combo.currentText().strip(),
            "model": self.model_combo.currentText().strip(),
            "planner_extra_prompt_enabled": self.extra_prompt_enabled.isChecked(),
            "planner_extra_prompt_path": self.extra_prompt_path_edit.text().strip(),
            "dry_run": self.dry_run_default.isChecked(),
            "allow_destructive": self.allow_destructive.isChecked(),
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
        self.last_requires_approval = False
        self._allow_destructive = bool(self._gui_cfg.get("allow_destructive", False))
        self._worker: QThread | None = None
        self._server_proc: subprocess.Popen | None = None
        self._server_watcher: _ServerStartWatcher | None = None

        base_url = self._gui_cfg.get(
            "base_url", os.getenv("LLMR_GUI_API_URL", "http://127.0.0.1:8787")
        )
        token = self._gui_cfg.get("token", os.getenv("LLMR_GUI_API_TOKEN", ""))
        self._server_url = base_url
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
        self.dry_run.setChecked(bool(self._gui_cfg.get("dry_run", True)))
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

        # ── Server control ─────────────────────────────────────────────────
        server_box = QGroupBox("Server")
        server_row = QHBoxLayout()
        self._server_status = QLabel()
        self._server_status.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._start_server_btn = QPushButton("Start Server")
        self._stop_server_btn = QPushButton("Stop Server")
        server_row.addWidget(self._server_status, stretch=1)
        server_row.addWidget(self._start_server_btn)
        server_row.addWidget(self._stop_server_btn)
        server_box.setLayout(server_row)

        layout.addWidget(QLabel("Prompt"))
        layout.addWidget(self.prompt)
        layout.addLayout(button_row)
        layout.addWidget(QLabel("Latest Plan ID"))
        layout.addWidget(self.plan_id)
        layout.addWidget(QLabel("Response"))
        layout.addWidget(self.output)
        layout.addWidget(server_box)
        layout.addWidget(self._status_label)

        root.setLayout(layout)
        self.setCentralWidget(root)

        self.plan_btn.clicked.connect(self.on_plan)
        self.execute_btn.clicked.connect(self.on_execute)
        settings_btn.clicked.connect(self.on_settings)
        self._start_server_btn.clicked.connect(self.on_start_server)
        self._stop_server_btn.clicked.connect(self.on_stop_server)
        self._update_server_buttons()

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
        self.last_requires_approval = False
        self._status_label.setText("Planning…")
        self._worker = _PlanWorker(self._backend, prompt)
        self._worker.finished.connect(self._on_plan_done)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.start()

    def _on_plan_done(self, payload: dict) -> None:
        self.last_plan_id = payload.get("plan_id", "")
        self.last_requires_approval = bool(payload.get("requires_approval", False))
        self.plan_id.setText(self.last_plan_id)
        self._show_output(payload)
        self._set_busy(False)
        self._status_label.setText("Plan ready — review and execute")

    # ── Execute ───────────────────────────────────────────────────────────────

    def on_execute(self) -> None:
        if not self.last_plan_id:
            QMessageBox.warning(self, "Missing plan", "Create a plan first.")
            return
        dry_run = self.dry_run.isChecked()
        if self.last_requires_approval and not dry_run and not self._allow_destructive:
            QMessageBox.warning(
                self,
                "Approval required",
                "This plan includes destructive actions. Enable destructive execution in Settings or keep Dry run on.",
            )
            return
        self._set_busy(True)
        self._status_label.setText("Executing…")
        self._worker = _ExecuteWorker(
            self._backend,
            self.last_plan_id,
            dry_run=dry_run,
            approved=self._allow_destructive or dry_run,
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

    # ── Server control ────────────────────────────────────────────────────────

    def _update_server_buttons(self) -> None:
        running = self._server_proc is not None and self._server_proc.poll() is None
        self._start_server_btn.setEnabled(not running)
        self._stop_server_btn.setEnabled(running)
        if running:
            self._server_status.setText(f"Running at {self._server_url}")
        elif _ping(self._server_url):
            self._server_status.setText(f"External server at {self._server_url}")
            self._start_server_btn.setEnabled(False)
            self._stop_server_btn.setEnabled(False)
        else:
            self._server_status.setText("Not running — GUI using embedded mode")

    def on_start_server(self) -> None:
        self._start_server_btn.setEnabled(False)
        self._server_status.setText("Starting…")
        backend_script = _PROJECT_ROOT / "backend" / "main.py"
        self._server_proc = subprocess.Popen(
            [sys.executable, str(backend_script)],
            cwd=str(_PROJECT_ROOT),
        )
        self._server_watcher = _ServerStartWatcher(self._server_url)
        self._server_watcher.ready.connect(self._on_server_ready)
        self._server_watcher.failed.connect(self._on_server_failed)
        self._server_watcher.finished.connect(self._server_watcher.deleteLater)
        self._server_watcher.start()

    def _on_server_ready(self) -> None:
        self._backend, mode = _choose_backend(self._server_url, self._gui_cfg.get("token", ""))
        self._status_label.setText(mode)
        self._update_server_buttons()

    def _on_server_failed(self, message: str) -> None:
        self._server_status.setText(f"Failed: {message}")
        if self._server_proc and self._server_proc.poll() is None:
            self._server_proc.terminate()
        self._server_proc = None
        self._update_server_buttons()

    def on_stop_server(self) -> None:
        if self._server_proc and self._server_proc.poll() is None:
            self._server_proc.terminate()
            try:
                self._server_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._server_proc.kill()
        self._server_proc = None
        self._backend, mode = _choose_backend(self._server_url, self._gui_cfg.get("token", ""))
        self._status_label.setText(mode)
        self._update_server_buttons()

    def closeEvent(self, event) -> None:
        if self._server_proc and self._server_proc.poll() is None:
            self._server_proc.terminate()
            try:
                self._server_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._server_proc.kill()
        super().closeEvent(event)

    # ── Settings ──────────────────────────────────────────────────────────────

    def on_settings(self) -> None:
        dlg = SettingsDialog(self._backend, self._gui_cfg, parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        vals = dlg.values()
        self._gui_cfg = {**vals}
        _save_gui_settings(self._gui_cfg)

        # Re-detect backend: if the new URL has a live server, switch to HTTP.
        self._server_url = vals["base_url"]
        self._backend, mode = _choose_backend(self._server_url, vals["token"])
        self._status_label.setText(mode)
        self._update_server_buttons()
        self._allow_destructive = bool(vals.get("allow_destructive", False))
        self.dry_run.setChecked(bool(vals.get("dry_run", True)))

        try:
            self._backend.patch_settings({
                "modelito_provider": vals["provider"],
                "modelito_model": vals["model"],
                "planner_extra_prompt_enabled": vals["planner_extra_prompt_enabled"],
                "planner_extra_prompt_path": vals["planner_extra_prompt_path"],
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
