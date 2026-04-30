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
    from PyQt6.QtGui import QAction, QColor, QKeySequence, QPalette
    from PyQt6.QtWidgets import (
        QAbstractItemView,
        QApplication,
        QCheckBox,
        QComboBox,
        QDialog,
        QFileDialog,
        QFormLayout,
        QFrame,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QProgressBar,
        QSpinBox,
        QSplitter,
        QStatusBar,
        QTabWidget,
        QTableWidget,
        QTableWidgetItem,
        QTextEdit,
        QVBoxLayout,
        QWidget,
        QHeaderView,
    )
except Exception as exc:
    raise SystemExit(
        "PyQt6 is required for the GUI. Install with: pip install PyQt6"
    ) from exc

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_GUI_SETTINGS_PATH = Path.home() / ".llmr" / "gui.json"
_PROVIDERS = ["openai", "anthropic", "google", "ollama", "cohere", "mistral", "mock", "other"]
_MODEL_FALLBACKS = {
    "openai": ["gpt-4.1-mini", "gpt-4.1", "gpt-4o-mini"],
    "anthropic": ["claude-3-5-sonnet-latest", "claude-3-5-haiku-latest"],
    "google": ["gemini-1.5-pro", "gemini-1.5-flash"],
    "ollama": ["llama3:latest", "mistral:latest", "codellama:latest"],
    "cohere": ["command-r", "command-r-plus"],
    "mistral": ["mistral-large-latest", "mistral-small-latest"],
    "mock": ["mock-model"],
    "other": [],
}
_COMMON_OLLAMA_MODELS = [
    "llama3:latest",
    "llama3.1:latest",
    "mistral:latest",
    "codellama:latest",
    "qwen2.5:latest",
    "gemma2:latest",
    "phi3:latest",
    "nomic-embed-text:latest",
]

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


# ── Theme ─────────────────────────────────────────────────────────────────────

_STYLESHEET = """
QWidget {
    background-color: #f3f5f8;
    color: #1c1c1e;
    font-size: 13px;
}
QMainWindow, QDialog {
    background-color: #f3f5f8;
}
QPushButton {
    padding: 5px 14px;
    border-radius: 5px;
    border: 1px solid #b0b8c8;
    background-color: #e8edf5;
    color: #1c1c1e;
    font-weight: 500;
    min-height: 22px;
}
QPushButton:hover  { background-color: #d0d8ea; border-color: #8090b0; }
QPushButton:pressed { background-color: #b8c8de; }
QPushButton:disabled { background-color: #f0f0f0; color: #9a9a9a; border-color: #d0d0d0; }

QPushButton[role="primary"] {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
}
QPushButton[role="primary"]:hover  { background-color: #1d4ed8; }
QPushButton[role="primary"]:pressed { background-color: #1e40af; }
QPushButton[role="primary"]:disabled {
    background-color: #f0f0f0;
    color: #9a9a9a;
    border: 1px solid #d0d0d0;
}

QPushButton[role="danger"] {
    background-color: #dc2626;
    color: #ffffff;
    border: none;
}
QPushButton[role="danger"]:hover  { background-color: #b91c1c; }
QPushButton[role="danger"]:disabled {
    background-color: #f0f0f0;
    color: #9a9a9a;
    border: 1px solid #d0d0d0;
}

QLineEdit, QSpinBox {
    background-color: #ffffff;
    color: #1c1c1e;
    border: 1px solid #c8d0dc;
    border-radius: 5px;
    padding: 4px 8px;
    min-height: 22px;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}
QLineEdit:focus, QSpinBox:focus { border-color: #2563eb; }
QLineEdit:read-only { background-color: #f4f5f7; color: #555; }

QTextEdit {
    background-color: #ffffff;
    color: #1c1c1e;
    border: 1px solid #c8d0dc;
    border-radius: 5px;
    padding: 4px;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}
QTextEdit:focus { border-color: #2563eb; }
QTextEdit[readOnly="true"] { background-color: #f4f5f7; color: #1c1c1e; }

QTextBrowser {
    background-color: #f8f9fc;
    color: #1c1c1e;
    border: 1px solid #c8d0dc;
    border-radius: 5px;
    padding: 8px;
}

QTableWidget {
    background-color: #ffffff;
    color: #1c1c1e;
    border: 1px solid #c8d0dc;
    border-radius: 5px;
    gridline-color: #e5e7eb;
    selection-background-color: #dbeafe;
    selection-color: #111827;
}
QHeaderView::section {
    background-color: #e8edf5;
    color: #374151;
    border: none;
    border-right: 1px solid #c8d0dc;
    border-bottom: 1px solid #c8d0dc;
    padding: 5px 7px;
    font-weight: 600;
}

QComboBox {
    background-color: #ffffff;
    color: #1c1c1e;
    border: 1px solid #c8d0dc;
    border-radius: 5px;
    padding: 4px 8px;
    min-height: 22px;
    min-width: 60px;
}
QComboBox:focus { border-color: #2563eb; }
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #d5dde8;
}
QComboBox::down-arrow {
    image: url(:/qt-project.org/styles/commonstyle/images/downarrow-16.png);
    width: 10px;
    height: 10px;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #1c1c1e;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
    border: 1px solid #c8d0dc;
}

QCheckBox { color: #1c1c1e; spacing: 8px; }
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 3px;
    border: 1px solid #94a3b8;
    background-color: #ffffff;
}
QCheckBox::indicator:hover { border-color: #2563eb; }
QCheckBox::indicator:checked {
    background-color: #2563eb;
    border-color: #2563eb;
}

QLabel { color: #1c1c1e; }

QMenu {
    background-color: #ffffff;
    color: #1c1c1e;
    border: 1px solid #c8d0dc;
}
QMenu::item:selected {
    background-color: #dbeafe;
    color: #111827;
}

QProgressBar {
    background-color: #e5e7eb;
    color: #111827;
    border: 1px solid #c8d0dc;
    border-radius: 4px;
    height: 10px;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #2563eb;
    border-radius: 3px;
}

QGroupBox {
    border: 1px solid #c8d0dc;
    border-radius: 8px;
    margin-top: 10px;
    padding: 10px 8px 8px 8px;
    font-weight: bold;
    color: #1c1c1e;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
    color: #374151;
}

QTabWidget::pane {
    border: 1px solid #c8d0dc;
    border-radius: 0 6px 6px 6px;
    background-color: #f8f9fc;
}
QTabWidget::tab-bar { left: 4px; }
QTabBar::tab {
    background-color: #e8edf5;
    color: #374151;
    border: 1px solid #c8d0dc;
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    padding: 6px 16px;
    margin-right: 2px;
}
QTabBar::tab:selected { background-color: #f8f9fc; color: #1c1c1e; font-weight: bold; }
QTabBar::tab:hover:!selected { background-color: #d8e2f0; }

QScrollArea { border: none; background-color: transparent; }
QScrollArea > QWidget > QWidget { background-color: transparent; }

QSplitter::handle { background-color: #c8d0dc; }
QSplitter::handle:horizontal { width: 1px; }
QSplitter::handle:vertical { height: 1px; }

QStatusBar { background-color: #e8edf5; color: #374151; border-top: 1px solid #c8d0dc; }
"""


def _apply_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    pal = QPalette()
    W = QColor
    pal.setColor(QPalette.ColorRole.Window,           W("#f0f2f5"))
    pal.setColor(QPalette.ColorRole.WindowText,       W("#1c1c1e"))
    pal.setColor(QPalette.ColorRole.Base,             W("#ffffff"))
    pal.setColor(QPalette.ColorRole.AlternateBase,    W("#f0f2f5"))
    pal.setColor(QPalette.ColorRole.Text,             W("#1c1c1e"))
    pal.setColor(QPalette.ColorRole.BrightText,       W("#ffffff"))
    pal.setColor(QPalette.ColorRole.Button,           W("#e8edf5"))
    pal.setColor(QPalette.ColorRole.ButtonText,       W("#1c1c1e"))
    pal.setColor(QPalette.ColorRole.Highlight,        W("#2563eb"))
    pal.setColor(QPalette.ColorRole.HighlightedText,  W("#ffffff"))
    pal.setColor(QPalette.ColorRole.Link,             W("#2563eb"))
    pal.setColor(QPalette.ColorRole.PlaceholderText,  W("#9ca3af"))
    pal.setColor(QPalette.ColorRole.ToolTipBase,      W("#ffffff"))
    pal.setColor(QPalette.ColorRole.ToolTipText,      W("#1c1c1e"))
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text,       W("#9a9a9a"))
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, W("#9a9a9a"))
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, W("#9a9a9a"))
    app.setPalette(pal)
    app.setStyleSheet(_STYLESHEET)


# ── Helpers ───────────────────────────────────────────────────────────────────

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


def _ping(url: str) -> bool:
    try:
        request.urlopen(f"{url.rstrip('/')}/health", timeout=1)
        return True
    except Exception:
        return False


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        item = str(value).strip()
        if item and item not in seen:
            out.append(item)
            seen.add(item)
    return out


def _combo_text(combo: QComboBox) -> str:
    return combo.currentText().strip()


def _set_combo_items(combo: QComboBox, values: list[str], current: str = "") -> None:
    selected = current or combo.currentText().strip()
    signals = combo.blockSignals(True)
    combo.clear()
    combo.addItems(_unique(values))
    if selected:
        combo.setCurrentText(selected)
    elif combo.count():
        combo.setCurrentIndex(0)
    combo.blockSignals(signals)


def _json_text(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _short_id(value: str) -> str:
    return f"{value[:8]}..." if value else ""


def _configure_tabs(tabs: QTabWidget) -> None:
    tabs.tabBar().setUsesScrollButtons(False)
    tabs.tabBar().setElideMode(Qt.TextElideMode.ElideNone)


# ── Backend interface ─────────────────────────────────────────────────────────

class Backend:
    def plan(self, prompt: str) -> dict: raise NotImplementedError
    def execute(self, plan_id: str, dry_run: bool, approved: bool = False) -> dict: raise NotImplementedError
    def get_settings(self) -> dict: raise NotImplementedError
    def patch_settings(self, data: dict) -> dict: raise NotImplementedError
    def get_modelito_models(self, provider: str = "", model: str = "") -> dict: raise NotImplementedError
    def ollama(self, action: str, model: str = "") -> dict: raise NotImplementedError


class HttpBackend(Backend):
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
        return self._request("POST", "/api/execute",
                             {"plan_id": plan_id, "dry_run": dry_run, "approved": approved})

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
            "status":        "/api/ollama/status",
            "local_models":  "/api/ollama/local_models",
            "remote_models": "/api/ollama/remote_models",
            "running_models": "/api/ollama/running_models",
        }
        if action in read_paths:
            return self._request("GET", read_paths[action])
        if action in {"start", "stop", "install"}:
            return self._request("POST", f"/api/ollama/{action}", {})
        if action in {"download", "delete", "serve", "stop_serving"}:
            return self._request("POST", f"/api/ollama/{action}", {"model": model})
        raise ValueError(f"Unknown Ollama action: {action}")


class EmbeddedBackend(Backend):
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
            ableton=AbletonOSCClient(self._settings.ableton_host, self._settings.ableton_port),
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
                {"tool": a.tool.value, "address": a.address, "args": a.args,
                 "description": a.description, "destructive": a.destructive}
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
        current_model    = model    or self._settings.modelito_model
        return {
            "provider":      current_provider,
            "default_model": current_model,
            "models":        modelito_models(current_provider, current_model),
        }

    def ollama(self, action: str, model: str = "") -> dict:
        from llmr import modelito_adapter

        actions = {
            "status":       lambda: modelito_adapter.ollama_status(),
            "local_models": lambda: modelito_adapter.ollama_local_models(),
            "remote_models":lambda: modelito_adapter.ollama_remote_models(),
            "running_models": lambda: modelito_adapter.ollama_running_models(),
            "start":        lambda: modelito_adapter.ollama_start(),
            "stop":         lambda: modelito_adapter.ollama_stop(),
            "install":      lambda: modelito_adapter.ollama_install(),
            "download":     lambda: modelito_adapter.ollama_download(model),
            "delete":       lambda: modelito_adapter.ollama_delete(model),
            "serve":        lambda: modelito_adapter.ollama_serve(model),
            "stop_serving":  lambda: modelito_adapter.ollama_stop_serving(model),
        }
        if action not in actions:
            raise ValueError(f"Unknown Ollama action: {action}")
        return actions[action]()


def _choose_backend(base_url: str, token: str) -> tuple[Backend, str]:
    if _ping(base_url):
        return HttpBackend(base_url=base_url, token=token), f"HTTP server: {base_url}"
    return EmbeddedBackend(), "Embedded mode (no server)"


# ── Background workers ────────────────────────────────────────────────────────

class _PlanWorker(QThread):
    finished: pyqtSignal = pyqtSignal(dict)
    error:    pyqtSignal = pyqtSignal(str)

    def __init__(self, backend: Backend, prompt: str) -> None:
        super().__init__()
        self._backend = backend
        self._prompt  = prompt

    def run(self) -> None:
        try:
            self.finished.emit(self._backend.plan(self._prompt))
        except Exception as exc:
            self.error.emit(str(exc))


class _ExecuteWorker(QThread):
    finished: pyqtSignal = pyqtSignal(dict)
    error:    pyqtSignal = pyqtSignal(str)

    def __init__(self, backend: Backend, plan_id: str, dry_run: bool, approved: bool) -> None:
        super().__init__()
        self._backend  = backend
        self._plan_id  = plan_id
        self._dry_run  = dry_run
        self._approved = approved

    def run(self) -> None:
        try:
            self.finished.emit(self._backend.execute(self._plan_id, self._dry_run, self._approved))
        except Exception as exc:
            self.error.emit(str(exc))


class _ActionWorker(QThread):
    finished: pyqtSignal = pyqtSignal(dict)
    error:    pyqtSignal = pyqtSignal(str)

    def __init__(self, fn) -> None:
        super().__init__()
        self._fn = fn

    def run(self) -> None:
        try:
            self.finished.emit(self._fn())
        except Exception as exc:
            self.error.emit(str(exc))


class _ServerStartWatcher(QThread):
    ready:  pyqtSignal = pyqtSignal()
    failed: pyqtSignal = pyqtSignal(str)

    def __init__(self, url: str, timeout: int = 20) -> None:
        super().__init__()
        self._url     = url
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
    """Settings are staged in the dialog and persisted only by Save."""

    def __init__(self, backend: Backend, cached: dict, parent=None) -> None:
        super().__init__(parent)
        self._backend = backend
        self._workers: list[_ActionWorker] = []
        self._loading = False
        self._dirty = False
        self._live_provider = cached.get("provider", "openai")

        self.setWindowTitle("LLM-r Settings")
        self.setMinimumSize(760, 620)
        self.resize(860, 720)

        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QWidget()
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(16, 14, 16, 10)
        header_layout.setSpacing(4)
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #111827;")
        self._summary_lbl = QLabel("")
        self._summary_lbl.setStyleSheet("font-size: 12px; color: #6b7280;")
        header_layout.addWidget(title)
        header_layout.addWidget(self._summary_lbl)
        header.setLayout(header_layout)

        self._tabs = QTabWidget()
        _configure_tabs(self._tabs)
        self._build_model_tab()
        self._build_ollama_tab()
        self._build_runtime_tab()
        self._build_connection_tab()

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #c8d0dc;")

        footer = QHBoxLayout()
        footer.setContentsMargins(16, 10, 16, 12)
        footer.setSpacing(8)
        self._status_lbl = QLabel("")
        self._status_lbl.setStyleSheet("color: #6b7280; font-size: 12px;")
        self._save_btn = QPushButton("Save")
        self._save_btn.setProperty("role", "primary")
        self._save_btn.setStyle(self._save_btn.style())
        self._save_close_btn = QPushButton("Save and Close")
        self._save_close_btn.setProperty("role", "primary")
        self._save_close_btn.setStyle(self._save_close_btn.style())
        self._cancel_btn = QPushButton("Cancel")
        footer.addWidget(self._status_lbl, stretch=1)
        footer.addWidget(self._save_btn)
        footer.addWidget(self._save_close_btn)
        footer.addWidget(self._cancel_btn)

        root.addWidget(header)
        root.addWidget(self._tabs, stretch=1)
        root.addWidget(line)
        root.addLayout(footer)
        self.setLayout(root)

        self._populate(cached)
        self._wire_dirty_signals()
        self._set_dirty(False)
        self._install_text_shortcuts()

        self._save_btn.clicked.connect(lambda: self._save(close=False))
        self._save_close_btn.clicked.connect(lambda: self._save(close=True))
        self._cancel_btn.clicked.connect(self.reject)

        QTimer.singleShot(0, self._check_connection)
        QTimer.singleShot(50, self._populate_model_list)
        QTimer.singleShot(100, self._refresh_ollama)

    # ── UI builders ───────────────────────────────────────────────────────────

    def _new_edit(self, placeholder: str = "") -> QLineEdit:
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setClearButtonEnabled(True)
        edit.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        return edit

    def _new_combo(self, editable: bool = True, placeholder: str = "") -> QComboBox:
        combo = QComboBox()
        combo.setEditable(editable)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        combo.setMinimumContentsLength(28)
        combo.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        if placeholder and combo.lineEdit():
            combo.lineEdit().setPlaceholderText(placeholder)
            combo.lineEdit().setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        return combo

    def _build_model_tab(self) -> None:
        w = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        model_grp = QGroupBox("Active Planner Model")
        form = QFormLayout()
        form.setSpacing(9)

        self.provider_combo = self._new_combo(editable=True)
        self.provider_combo.addItems(_PROVIDERS)
        self.model_combo = self._new_combo(
            editable=True,
            placeholder="Choose a model from the list or type an exact model id",
        )
        self.refresh_models_btn = QPushButton("Refresh Models")
        self.model_status = QLabel("Model list not loaded.")
        self.model_status.setWordWrap(True)
        self.model_status.setStyleSheet("font-size: 12px; color: #6b7280;")

        model_row = QHBoxLayout()
        model_row.addWidget(self.model_combo, stretch=1)
        model_row.addWidget(self.refresh_models_btn)

        form.addRow("Provider", self.provider_combo)
        form.addRow("Model", model_row)
        form.addRow("", self.model_status)
        model_grp.setLayout(form)

        planner_grp = QGroupBox("Planner Guidance")
        planner_form = QFormLayout()
        planner_form.setSpacing(9)
        self.extra_prompt_enabled = QCheckBox("Use the LLM-r Ableton planning guidance")
        self.extra_prompt_path_edit = self._new_edit("Optional path to a custom planner prompt")
        self.prompt_browse_btn = QPushButton("Browse...")
        prompt_row = QHBoxLayout()
        prompt_row.addWidget(self.extra_prompt_path_edit, stretch=1)
        prompt_row.addWidget(self.prompt_browse_btn)
        planner_form.addRow(self.extra_prompt_enabled)
        planner_form.addRow("Prompt file", prompt_row)
        planner_grp.setLayout(planner_form)

        layout.addWidget(model_grp)
        layout.addWidget(planner_grp)
        layout.addStretch()
        w.setLayout(layout)
        self._tabs.addTab(w, "Model")

        self.refresh_models_btn.clicked.connect(self._populate_model_list)
        self.provider_combo.currentTextChanged.connect(self._on_provider_changed)
        self.prompt_browse_btn.clicked.connect(self._browse_prompt_file)

    def _build_ollama_tab(self) -> None:
        w = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        svc_grp = QGroupBox("Ollama Service")
        svc_layout = QVBoxLayout()
        svc_layout.setSpacing(8)
        self.ollama_status_lbl = QLabel("Status not checked.")
        self.ollama_status_lbl.setWordWrap(True)
        self.ollama_status_lbl.setStyleSheet("font-size: 12px; color: #6b7280;")

        svc_btns = QHBoxLayout()
        self.ollama_install_btn = QPushButton("Install")
        self.ollama_start_btn = QPushButton("Start Service")
        self.ollama_stop_btn = QPushButton("Stop Service")
        self.ollama_stop_btn.setProperty("role", "danger")
        self.ollama_stop_btn.setStyle(self.ollama_stop_btn.style())
        self.ollama_check_btn = QPushButton("Refresh")
        for btn in (
            self.ollama_install_btn,
            self.ollama_start_btn,
            self.ollama_stop_btn,
            self.ollama_check_btn,
        ):
            svc_btns.addWidget(btn)
        svc_btns.addStretch()
        svc_layout.addWidget(self.ollama_status_lbl)
        svc_layout.addLayout(svc_btns)
        svc_grp.setLayout(svc_layout)

        local_grp = QGroupBox("Local and Served Models")
        local_grp.setMinimumHeight(185)
        local_layout = QVBoxLayout()
        local_layout.setSpacing(7)
        self.local_models_combo = self._new_combo(
            editable=True,
            placeholder="Local Ollama models appear here",
        )
        self.running_models_combo = self._new_combo(
            editable=True,
            placeholder="Served Ollama models appear here",
        )

        self.set_ollama_model_btn = QPushButton("Set Active")
        self.set_ollama_model_btn.setToolTip("Use the selected local Ollama model for planning after Save.")
        self.serve_model_btn = QPushButton("Serve")
        self.serve_model_btn.setToolTip("Load the selected local model in Ollama.")
        self.serve_model_btn.setProperty("role", "primary")
        self.serve_model_btn.setStyle(self.serve_model_btn.style())
        self.delete_model_btn = QPushButton("Delete")
        self.delete_model_btn.setToolTip("Delete the selected local Ollama model.")
        self.delete_model_btn.setProperty("role", "danger")
        self.delete_model_btn.setStyle(self.delete_model_btn.style())
        self.refresh_local_btn = QPushButton("Refresh")
        self.refresh_local_btn.setToolTip("Reload local Ollama models.")

        self.stop_serving_btn = QPushButton("Stop")
        self.stop_serving_btn.setToolTip("Stop serving the selected loaded Ollama model.")
        self.stop_serving_btn.setProperty("role", "danger")
        self.stop_serving_btn.setStyle(self.stop_serving_btn.style())
        self.refresh_running_btn = QPushButton("Refresh")
        self.refresh_running_btn.setToolTip("Reload served Ollama models.")

        local_model_lbl = QLabel("Local model")
        local_model_lbl.setStyleSheet("font-weight: 600; color: #374151;")
        local_model_lbl.setMinimumWidth(90)
        served_model_lbl = QLabel("Served model")
        served_model_lbl.setStyleSheet("font-weight: 600; color: #374151;")
        served_model_lbl.setMinimumWidth(90)

        local_row = QHBoxLayout()
        local_row.setSpacing(8)
        local_row.addWidget(local_model_lbl)
        local_row.addWidget(self.local_models_combo, stretch=1)
        local_row.addWidget(self.set_ollama_model_btn)
        local_row.addWidget(self.serve_model_btn)
        local_row.addWidget(self.delete_model_btn)
        local_row.addWidget(self.refresh_local_btn)

        served_row = QHBoxLayout()
        served_row.setSpacing(8)
        served_row.addWidget(served_model_lbl)
        served_row.addWidget(self.running_models_combo, stretch=1)
        served_row.addWidget(self.stop_serving_btn)
        served_row.addWidget(self.refresh_running_btn)

        local_layout.addLayout(local_row)
        local_layout.addLayout(served_row)
        local_grp.setLayout(local_layout)

        remote_grp = QGroupBox("Downloadable Ollama Models")
        remote_layout = QVBoxLayout()
        remote_layout.setSpacing(8)
        self.remote_models_combo = self._new_combo(
            editable=True,
            placeholder="Choose a downloadable model or type one",
        )
        _set_combo_items(self.remote_models_combo, _COMMON_OLLAMA_MODELS)
        remote_btns = QHBoxLayout()
        self.list_remote_btn = QPushButton("Load Online List")
        self.download_model_btn = QPushButton("Download Selected")
        self.download_model_btn.setProperty("role", "primary")
        self.download_model_btn.setStyle(self.download_model_btn.style())
        remote_btns.addWidget(self.list_remote_btn)
        remote_btns.addWidget(self.download_model_btn)
        remote_btns.addStretch()
        remote_layout.addWidget(self.remote_models_combo)
        remote_layout.addLayout(remote_btns)
        remote_grp.setLayout(remote_layout)

        log_grp = QGroupBox("Ollama Activity")
        log_layout = QVBoxLayout()
        self.ollama_log = QTextEdit()
        self.ollama_log.setReadOnly(True)
        self.ollama_log.setMaximumHeight(110)
        self.ollama_log.setPlaceholderText("Ollama operation output appears here.")
        self.ollama_log.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        log_layout.addWidget(self.ollama_log)
        log_grp.setLayout(log_layout)

        layout.addWidget(svc_grp)
        layout.addWidget(local_grp)
        layout.addWidget(remote_grp)
        layout.addWidget(log_grp)
        layout.addStretch()
        w.setLayout(layout)
        self._tabs.addTab(w, "Ollama")

        self.ollama_check_btn.clicked.connect(self._refresh_ollama)
        self.ollama_start_btn.clicked.connect(lambda: self._run_ollama("start"))
        self.ollama_stop_btn.clicked.connect(lambda: self._run_ollama("stop"))
        self.ollama_install_btn.clicked.connect(lambda: self._run_ollama("install"))
        self.refresh_local_btn.clicked.connect(self._load_local_models)
        self.refresh_running_btn.clicked.connect(self._load_running_models)
        self.list_remote_btn.clicked.connect(self._load_remote_models)
        self.download_model_btn.clicked.connect(self._download_selected)
        self.delete_model_btn.clicked.connect(self._delete_selected)
        self.serve_model_btn.clicked.connect(self._serve_selected)
        self.stop_serving_btn.clicked.connect(self._stop_serving_selected)
        self.set_ollama_model_btn.clicked.connect(self._set_active_ollama_model)

    def _build_runtime_tab(self) -> None:
        w = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        exec_grp = QGroupBox("Execution Defaults")
        exec_form = QFormLayout()
        exec_form.setSpacing(9)
        self.dry_run_default = QCheckBox("Dry run by default")
        self.allow_destructive = QCheckBox("Allow destructive execution after review")
        exec_form.addRow(self.dry_run_default)
        exec_form.addRow(self.allow_destructive)
        exec_grp.setLayout(exec_form)

        ableton_grp = QGroupBox("AbletonOSC")
        ableton_form = QFormLayout()
        ableton_form.setSpacing(9)
        self.ableton_host_edit = self._new_edit("127.0.0.1")
        self.ableton_port_spin = QSpinBox()
        self.ableton_port_spin.setRange(1, 65535)
        self.ableton_port_spin.setValue(11000)
        ableton_form.addRow("OSC host", self.ableton_host_edit)
        ableton_form.addRow("OSC port", self.ableton_port_spin)
        ableton_grp.setLayout(ableton_form)

        layout.addWidget(exec_grp)
        layout.addWidget(ableton_grp)
        layout.addStretch()
        w.setLayout(layout)
        self._tabs.addTab(w, "Runtime")

    def _build_connection_tab(self) -> None:
        w = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        grp = QGroupBox("Server Connection")
        form = QFormLayout()
        form.setSpacing(9)
        self.url_edit = self._new_edit("http://127.0.0.1:8787")
        self.token_edit = self._new_edit("leave empty to disable auth")
        self.token_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.show_token_chk = QCheckBox("Show token")
        self.show_token_chk.toggled.connect(
            lambda v: self.token_edit.setEchoMode(
                QLineEdit.EchoMode.Normal if v else QLineEdit.EchoMode.Password
            )
        )
        self.check_btn = QPushButton("Check Connection")
        self.conn_status = QLabel("Not checked.")
        self.conn_status.setWordWrap(True)
        self.conn_status.setStyleSheet("font-size: 12px; color: #6b7280;")

        url_row = QHBoxLayout()
        url_row.addWidget(self.url_edit, stretch=1)
        url_row.addWidget(self.check_btn)
        token_row = QHBoxLayout()
        token_row.addWidget(self.token_edit, stretch=1)
        token_row.addWidget(self.show_token_chk)

        form.addRow("Server URL", url_row)
        form.addRow("API token", token_row)
        form.addRow("Mode", self.conn_status)
        grp.setLayout(form)

        layout.addWidget(grp)
        layout.addStretch()
        w.setLayout(layout)
        self._tabs.addTab(w, "Server")

        self.check_btn.clicked.connect(self._check_connection)

    # ── Populate and dirty tracking ───────────────────────────────────────────

    def _populate(self, cached: dict) -> None:
        self._loading = True
        self.url_edit.setText(cached.get("base_url", "http://127.0.0.1:8787"))
        self.token_edit.setText(cached.get("token", ""))

        provider = cached.get("provider", "openai")
        model = cached.get("model", "")
        live_error = ""
        try:
            live = self._backend.get_settings()
            provider = live.get("modelito_provider", provider)
            model = live.get("modelito_model", model)
            self.extra_prompt_enabled.setChecked(
                bool(live.get("planner_extra_prompt_enabled", True))
            )
            self.extra_prompt_path_edit.setText(live.get("planner_extra_prompt_path", ""))
            self.ableton_host_edit.setText(live.get("ableton_host", "127.0.0.1"))
            self.ableton_port_spin.setValue(int(live.get("ableton_port", 11000)))
        except Exception as exc:
            live_error = str(exc)
            self.extra_prompt_enabled.setChecked(
                bool(cached.get("planner_extra_prompt_enabled", True))
            )
            self.extra_prompt_path_edit.setText(cached.get("planner_extra_prompt_path", ""))
            self.ableton_host_edit.setText(cached.get("ableton_host", "127.0.0.1"))
            self.ableton_port_spin.setValue(int(cached.get("ableton_port", 11000)))

        self._live_provider = provider
        self.provider_combo.setCurrentText(provider)
        _set_combo_items(
            self.model_combo,
            _MODEL_FALLBACKS.get(provider, []) + ([model] if model else []),
            model,
        )

        self.dry_run_default.setChecked(bool(cached.get("dry_run", True)))
        self.allow_destructive.setChecked(bool(cached.get("allow_destructive", False)))
        self._loading = False
        self._update_summary()
        if live_error:
            self._set_status(f"Loaded saved settings; live settings unavailable: {live_error}", "warn")

    def _wire_dirty_signals(self) -> None:
        for edit in (
            self.url_edit,
            self.token_edit,
            self.extra_prompt_path_edit,
            self.ableton_host_edit,
        ):
            edit.textChanged.connect(self._mark_dirty)
        for combo in (self.provider_combo, self.model_combo):
            combo.currentTextChanged.connect(self._mark_dirty)
        for check in (
            self.extra_prompt_enabled,
            self.dry_run_default,
            self.allow_destructive,
        ):
            check.toggled.connect(self._mark_dirty)
        self.ableton_port_spin.valueChanged.connect(self._mark_dirty)

    def _mark_dirty(self, *_args) -> None:
        if not self._loading:
            self._set_dirty(True)
            self._update_summary()

    def _set_dirty(self, dirty: bool) -> None:
        self._dirty = dirty
        if dirty:
            self._set_status("Unsaved changes.", "warn")
        elif not self._status_lbl.text():
            self._set_status("Settings loaded.", "neutral")

    def _set_status(self, text: str, kind: str = "neutral") -> None:
        colors = {
            "neutral": "#6b7280",
            "ok": "#16a34a",
            "warn": "#b45309",
            "error": "#dc2626",
        }
        self._status_lbl.setText(text)
        self._status_lbl.setStyleSheet(f"color: {colors.get(kind, colors['neutral'])}; font-size: 12px;")

    def _update_summary(self) -> None:
        provider = _combo_text(self.provider_combo) or "provider"
        model = _combo_text(self.model_combo) or "model"
        conn_text = self.conn_status.text().lower() if hasattr(self, "conn_status") else ""
        mode = "HTTP mode" if conn_text.startswith("server reachable") else "embedded mode"
        dirty = " - unsaved" if self._dirty else ""
        self._summary_lbl.setText(f"{provider} / {model} - {mode}{dirty}")

    # ── Connection and model lists ────────────────────────────────────────────

    def _check_connection(self) -> None:
        url = self.url_edit.text().strip().rstrip("/")
        if not url:
            self.conn_status.setText("Enter a server URL.")
            self.conn_status.setStyleSheet("color: #dc2626; font-size: 12px;")
            return
        self.conn_status.setText("Checking...")
        self.conn_status.setStyleSheet("color: #6b7280; font-size: 12px;")

        def on_done(payload: dict) -> None:
            if payload.get("ok"):
                self.conn_status.setText("Server reachable. Save will use HTTP mode.")
                self.conn_status.setStyleSheet("color: #16a34a; font-size: 12px;")
            else:
                self.conn_status.setText("Server not reachable. Save will use embedded mode.")
                self.conn_status.setStyleSheet("color: #b45309; font-size: 12px;")
            self._update_summary()

        self._run_async(
            lambda: {"ok": _ping(url)},
            on_done,
            on_error=lambda msg: self._set_conn_error(msg),
            lock=(self.check_btn,),
        )

    def _set_conn_error(self, msg: str) -> None:
        self.conn_status.setText(f"Check failed: {msg}")
        self.conn_status.setStyleSheet("color: #dc2626; font-size: 12px;")

    def _on_provider_changed(self, provider: str) -> None:
        if self._loading:
            return
        current = _combo_text(self.model_combo)
        preferred = current if provider == self._live_provider else ""
        _set_combo_items(self.model_combo, _MODEL_FALLBACKS.get(provider, []), preferred)
        if provider == "ollama":
            QTimer.singleShot(0, self._load_local_models)
        self._mark_dirty()

    def _populate_model_list(self) -> None:
        provider = _combo_text(self.provider_combo)
        current = _combo_text(self.model_combo)
        self.model_status.setText("Loading models...")

        def on_done(payload: dict) -> None:
            models = [str(m) for m in payload.get("models", []) if str(m).strip()]
            models = _MODEL_FALLBACKS.get(provider, []) + models
            _set_combo_items(self.model_combo, models, current or payload.get("default_model", ""))
            p = payload.get("provider") or provider
            self.model_status.setText(f"{self.model_combo.count()} model(s) available for {p}.")

        def on_error(msg: str) -> None:
            _set_combo_items(self.model_combo, _MODEL_FALLBACKS.get(provider, []), current)
            self.model_status.setText(f"Could not refresh provider list: {msg}")

        self._run_async(
            lambda: self._backend.get_modelito_models(provider, current),
            on_done,
            on_error=on_error,
            lock=(self.refresh_models_btn,),
        )

    # ── Ollama ────────────────────────────────────────────────────────────────

    def _all_ollama_btns(self) -> tuple:
        return (
            self.ollama_install_btn,
            self.ollama_start_btn,
            self.ollama_stop_btn,
            self.ollama_check_btn,
            self.refresh_local_btn,
            self.refresh_running_btn,
            self.list_remote_btn,
            self.download_model_btn,
            self.delete_model_btn,
            self.serve_model_btn,
            self.stop_serving_btn,
            self.set_ollama_model_btn,
        )

    def _refresh_ollama(self) -> None:
        def on_done(payload: dict) -> None:
            self._set_ollama_status(payload)
            self._log_ollama(payload)
            QTimer.singleShot(0, self._load_local_models)
            QTimer.singleShot(0, self._load_running_models)

        self._run_async(
            lambda: self._backend.ollama("status"),
            on_done,
            on_error=lambda msg: self._set_ollama_error(msg),
            lock=self._all_ollama_btns(),
        )

    def _load_local_models(self) -> None:
        def on_done(payload: dict) -> None:
            models = [str(m) for m in payload.get("models", []) if str(m).strip()]
            _set_combo_items(self.local_models_combo, models, _combo_text(self.local_models_combo))
            if _combo_text(self.provider_combo) == "ollama":
                _set_combo_items(
                    self.model_combo,
                    models + _MODEL_FALLBACKS.get("ollama", []),
                    _combo_text(self.model_combo),
                )
            self._set_ollama_status(payload)

        self._run_async(
            lambda: self._backend.ollama("local_models"),
            on_done,
            on_error=lambda msg: self._set_ollama_error(msg),
            lock=(self.refresh_local_btn,),
        )

    def _load_running_models(self) -> None:
        def on_done(payload: dict) -> None:
            models = [str(m) for m in payload.get("models", []) if str(m).strip()]
            _set_combo_items(self.running_models_combo, models, _combo_text(self.running_models_combo))

        self._run_async(
            lambda: self._backend.ollama("running_models"),
            on_done,
            on_error=lambda msg: self._set_ollama_error(msg),
            lock=(self.refresh_running_btn,),
        )

    def _load_remote_models(self) -> None:
        self.ollama_status_lbl.setText("Loading downloadable models...")

        def on_done(payload: dict) -> None:
            models = [str(m) for m in payload.get("models", []) if str(m).strip()]
            _set_combo_items(
                self.remote_models_combo,
                models + _COMMON_OLLAMA_MODELS,
                _combo_text(self.remote_models_combo),
            )
            self._set_ollama_status(payload)

        self._run_async(
            lambda: self._backend.ollama("remote_models"),
            on_done,
            on_error=lambda msg: self._set_ollama_error(msg),
            lock=(self.list_remote_btn,),
        )

    def _run_ollama(self, action: str, model: str = "", after_success=None) -> None:
        labels = {
            "start": "Starting Ollama service...",
            "stop": "Stopping Ollama service...",
            "install": "Installing Ollama...",
            "download": f"Downloading {model}...",
            "delete": f"Deleting {model}...",
            "serve": f"Serving {model}...",
            "stop_serving": f"Stopping {model}...",
        }
        self.ollama_status_lbl.setText(labels.get(action, f"Running {action}..."))

        def on_done(payload: dict) -> None:
            self._set_ollama_status(payload)
            self._log_ollama(payload)
            if payload.get("ok", True) and callable(after_success):
                after_success(payload)
            if action in {"start", "stop", "install", "download", "delete", "serve", "stop_serving"}:
                QTimer.singleShot(0, self._load_local_models)
                QTimer.singleShot(0, self._load_running_models)

        self._run_async(
            lambda: self._backend.ollama(action, model),
            on_done,
            on_error=lambda msg: self._set_ollama_error(msg),
            lock=self._all_ollama_btns(),
        )

    def _download_selected(self) -> None:
        model = _combo_text(self.remote_models_combo)
        if not model:
            self.ollama_status_lbl.setText("Choose a downloadable model first.")
            return
        self._run_ollama("download", model)

    def _delete_selected(self) -> None:
        model = _combo_text(self.local_models_combo)
        if not model:
            self.ollama_status_lbl.setText("Choose a local model first.")
            return
        if QMessageBox.question(
            self,
            "Delete Local Model",
            f"Delete local Ollama model '{model}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        ) == QMessageBox.StandardButton.Yes:
            self._run_ollama("delete", model)

    def _serve_selected(self) -> None:
        model = _combo_text(self.local_models_combo)
        if not model:
            self.ollama_status_lbl.setText("Choose a local model to serve.")
            return
        self.provider_combo.setCurrentText("ollama")
        self.model_combo.setCurrentText(model)
        self._mark_dirty()
        self._run_ollama("serve", model)

    def _stop_serving_selected(self) -> None:
        model = _combo_text(self.running_models_combo)
        if not model:
            self.ollama_status_lbl.setText("Choose a served model to stop.")
            return
        self._run_ollama("stop_serving", model)

    def _set_active_ollama_model(self) -> None:
        model = _combo_text(self.local_models_combo)
        if not model:
            self.ollama_status_lbl.setText("Choose a local model first.")
            return
        self.provider_combo.setCurrentText("ollama")
        self.model_combo.setCurrentText(model)
        self._mark_dirty()
        self.ollama_status_lbl.setText(f"{model} selected. Click Save to use it for planning.")

    def _set_ollama_status(self, payload: dict) -> None:
        ok = payload.get("ok", True)
        self.ollama_status_lbl.setText(payload.get("message", "Ollama status updated."))
        self.ollama_status_lbl.setStyleSheet(
            f"font-size: 12px; color: {'#16a34a' if ok else '#dc2626'};"
        )

    def _set_ollama_error(self, msg: str) -> None:
        self.ollama_status_lbl.setText(f"Ollama action failed: {msg}")
        self.ollama_status_lbl.setStyleSheet("font-size: 12px; color: #dc2626;")
        self._log_ollama({"error": msg})

    def _log_ollama(self, payload) -> None:
        text = json.dumps(payload, indent=2, ensure_ascii=False) if isinstance(payload, dict) else str(payload)
        self.ollama_log.append(text)

    # ── File browser and async runner ─────────────────────────────────────────

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

    def _run_async(self, fn, on_success, *, on_error=None, lock=()) -> None:
        worker = _ActionWorker(fn)
        self._workers.append(worker)
        locked = tuple(lock)
        for button in locked:
            button.setEnabled(False)

        def cleanup() -> None:
            if worker in self._workers:
                self._workers.remove(worker)
            for button in locked:
                button.setEnabled(True)
            worker.deleteLater()

        worker.finished.connect(on_success)
        worker.finished.connect(lambda *_: cleanup())
        worker.error.connect(on_error or (lambda m: self._set_status(f"Error: {m}", "error")))
        worker.error.connect(lambda *_: cleanup())
        worker.start()

    def _install_text_shortcuts(self) -> None:
        actions = [
            ("Cut", QKeySequence.StandardKey.Cut, "cut"),
            ("Copy", QKeySequence.StandardKey.Copy, "copy"),
            ("Paste", QKeySequence.StandardKey.Paste, "paste"),
            ("Delete", QKeySequence.StandardKey.Delete, "delete"),
            ("Select All", QKeySequence.StandardKey.SelectAll, "select_all"),
        ]
        for label, shortcut, operation in actions:
            action = QAction(label, self)
            action.setShortcut(QKeySequence(shortcut))
            action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
            action.triggered.connect(lambda _checked=False, op=operation: self._text_action(op))
            self.addAction(action)

    def _text_action(self, operation: str) -> None:
        widget = QApplication.focusWidget()
        if operation == "cut" and hasattr(widget, "cut"):
            widget.cut()
        elif operation == "copy" and hasattr(widget, "copy"):
            widget.copy()
        elif operation == "paste" and hasattr(widget, "paste"):
            widget.paste()
        elif operation == "select_all" and hasattr(widget, "selectAll"):
            widget.selectAll()
        elif operation == "delete":
            if isinstance(widget, QLineEdit):
                widget.del_()
            elif isinstance(widget, QTextEdit):
                cursor = widget.textCursor()
                if cursor.hasSelection():
                    cursor.removeSelectedText()
                else:
                    cursor.deleteChar()

    # ── Save logic ────────────────────────────────────────────────────────────

    def values(self) -> dict:
        return {
            "base_url": self.url_edit.text().strip().rstrip("/") or "http://127.0.0.1:8787",
            "token": self.token_edit.text().strip(),
            "provider": _combo_text(self.provider_combo),
            "model": _combo_text(self.model_combo),
            "planner_extra_prompt_enabled": self.extra_prompt_enabled.isChecked(),
            "planner_extra_prompt_path": self.extra_prompt_path_edit.text().strip(),
            "dry_run": self.dry_run_default.isChecked(),
            "allow_destructive": self.allow_destructive.isChecked(),
            "ableton_host": self.ableton_host_edit.text().strip() or "127.0.0.1",
            "ableton_port": self.ableton_port_spin.value(),
        }

    def _runtime_patch(self, vals: dict) -> dict:
        return {
            "modelito_provider": vals["provider"],
            "modelito_model": vals["model"],
            "planner_extra_prompt_enabled": vals["planner_extra_prompt_enabled"],
            "planner_extra_prompt_path": vals["planner_extra_prompt_path"],
            "ableton_host": vals["ableton_host"],
            "ableton_port": vals["ableton_port"],
            "api_token": vals["token"] or None,
        }

    def _backend_for_save(self, vals: dict) -> tuple[Backend, str]:
        if isinstance(self._backend, HttpBackend) and self._backend.base_url == vals["base_url"]:
            return self._backend, f"HTTP server: {vals['base_url']}"
        return _choose_backend(vals["base_url"], vals["token"])

    def _save(self, close: bool) -> None:
        vals = self.values()
        if not vals["provider"] or not vals["model"]:
            self._set_status("Choose both a provider and a model before saving.", "error")
            self._tabs.setCurrentIndex(0)
            return

        backend, mode = self._backend_for_save(vals)
        try:
            backend.patch_settings(self._runtime_patch(vals))
        except Exception as exc:
            self._set_status(f"Settings were not saved because runtime settings failed: {exc}", "error")
            return

        _save_gui_settings(vals)
        self._backend = backend
        self._live_provider = vals["provider"]
        self._set_dirty(False)
        self._set_status(f"Settings saved. {mode}", "ok")
        self._update_summary()
        if close:
            self.accept()


# ── Main window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("LLM-r")
        self.setMinimumSize(720, 560)

        self._gui_cfg             = _load_gui_settings()
        self.last_plan_id         = ""
        self.last_requires_approval = False
        self._plan_action_count = 0
        self._plan_executed = False
        self._allow_destructive   = bool(self._gui_cfg.get("allow_destructive", False))
        self._worker: QThread | None = None
        self._server_proc: subprocess.Popen | None = None
        self._server_watcher: _ServerStartWatcher | None = None

        base_url = self._gui_cfg.get("base_url", os.getenv("LLMR_GUI_API_URL", "http://127.0.0.1:8787"))
        token    = self._gui_cfg.get("token", os.getenv("LLMR_GUI_API_TOKEN", ""))
        self._server_url = base_url
        self._backend, mode = _choose_backend(base_url, token)

        self._build_ui()
        self._status_bar.showMessage(mode)
        self._update_server_ui()

    def _build_ui(self) -> None:
        root   = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 6)
        layout.setSpacing(8)

        # ── Top bar: server + settings ────────────────────────────────────────
        top_bar = QHBoxLayout()
        top_bar.setSpacing(6)

        self._server_status_lbl = QLabel("Checking server…")
        self._server_status_lbl.setStyleSheet("font-size: 12px; color: #6b7280;")

        self._start_server_btn = QPushButton("Start Server")
        self._stop_server_btn  = QPushButton("Stop Server")
        self._stop_server_btn.setProperty("role", "danger")
        self._stop_server_btn.setStyle(self._stop_server_btn.style())

        self._settings_btn = QPushButton("⚙ Settings")
        self._settings_btn.setProperty("role", "primary")
        self._settings_btn.setStyle(self._settings_btn.style())

        top_bar.addWidget(self._server_status_lbl, stretch=1)
        top_bar.addWidget(self._start_server_btn)
        top_bar.addWidget(self._stop_server_btn)
        top_bar.addWidget(self._settings_btn)

        # ── Splitter: prompt (top) | response (bottom) ────────────────────────
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(6)

        # Prompt panel
        prompt_panel = QWidget()
        pp_layout    = QVBoxLayout()
        pp_layout.setContentsMargins(0, 0, 0, 0)
        pp_layout.setSpacing(6)

        prompt_lbl = QLabel("Prompt — describe what you want Ableton to do:")
        prompt_lbl.setStyleSheet("font-weight: 600; font-size: 12px; color: #374151;")

        self.prompt = QTextEdit()
        self.prompt.setPlaceholderText(
            "e.g. Set the tempo to 128 BPM, mute track 3, and start playback"
        )
        self.prompt.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        self.prompt.setMinimumHeight(90)

        action_row = QHBoxLayout()
        action_row.setSpacing(8)

        self.plan_btn    = QPushButton("Plan")
        self.plan_btn.setProperty("role", "primary")
        self.plan_btn.setStyle(self.plan_btn.style())
        self.plan_btn.setMinimumWidth(90)

        self.execute_btn = QPushButton("Execute")
        self.execute_btn.setProperty("role", "primary")
        self.execute_btn.setStyle(self.execute_btn.style())
        self.execute_btn.setMinimumWidth(90)
        self.execute_btn.setEnabled(False)

        self.dry_run = QCheckBox("Dry run")
        self.dry_run.setChecked(bool(self._gui_cfg.get("dry_run", True)))
        self.dry_run.setToolTip("Preview OSC messages without sending them to Ableton")

        self._plan_id_lbl = QLabel("")
        self._plan_id_lbl.setStyleSheet("color: #9ca3af; font-size: 11px;")

        action_row.addWidget(self.plan_btn)
        action_row.addWidget(self.execute_btn)
        action_row.addWidget(self.dry_run)
        action_row.addStretch()
        action_row.addWidget(self._plan_id_lbl)

        pp_layout.addWidget(prompt_lbl)
        pp_layout.addWidget(self.prompt)
        pp_layout.addLayout(action_row)
        prompt_panel.setLayout(pp_layout)

        # Response panel
        response_panel = QWidget()
        rp_layout = QVBoxLayout()
        rp_layout.setContentsMargins(0, 0, 0, 0)
        rp_layout.setSpacing(6)

        response_hdr = QHBoxLayout()
        response_lbl = QLabel("Plan Review")
        response_lbl.setStyleSheet("font-weight: 700; font-size: 13px; color: #111827;")
        self._current_model_lbl = QLabel("")
        self._current_model_lbl.setStyleSheet("font-size: 12px; color: #6b7280;")
        response_hdr.addWidget(response_lbl)
        response_hdr.addStretch()
        response_hdr.addWidget(self._current_model_lbl)

        self._response_tabs = QTabWidget()
        _configure_tabs(self._response_tabs)
        self._summary_tab = QWidget()
        summary_layout = QVBoxLayout()
        summary_layout.setContentsMargins(12, 12, 12, 12)
        summary_layout.setSpacing(8)
        self._summary_title = QLabel("No plan yet")
        self._summary_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #111827;")
        self._summary_detail = QLabel("Enter a prompt, click Plan, then review the parsed action list.")
        self._summary_detail.setWordWrap(True)
        self._summary_detail.setStyleSheet("font-size: 13px; color: #374151;")
        self._confidence_bar = QProgressBar()
        self._confidence_bar.setRange(0, 100)
        self._confidence_bar.setValue(0)
        self._confidence_bar.setFormat("Confidence: %p%")
        self._approval_lbl = QLabel("Approval: not required")
        self._approval_lbl.setStyleSheet("font-size: 12px; color: #6b7280;")
        summary_layout.addWidget(self._summary_title)
        summary_layout.addWidget(self._summary_detail)
        summary_layout.addWidget(self._confidence_bar)
        summary_layout.addWidget(self._approval_lbl)
        summary_layout.addStretch()
        self._summary_tab.setLayout(summary_layout)

        self._actions_table = self._make_table(
            ["#", "Tool", "Safety", "Description", "Args", "OSC Address"]
        )
        self._execution_table = self._make_table(
            ["#", "Status", "Tool", "Args", "OSC Address", "Message"]
        )
        self._response_raw = QTextEdit()
        self._response_raw.setReadOnly(True)
        self._response_raw.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        self._response_raw.setPlaceholderText("Raw JSON appears here after a plan or execution.")
        self._last_payload: dict = {}
        self._last_plan_payload: dict = {}

        self._response_tabs.addTab(self._summary_tab, "Summary")
        self._response_tabs.addTab(self._actions_table, "Actions")
        self._response_tabs.addTab(self._execution_table, "Execution")
        self._response_tabs.addTab(self._response_raw, "Raw JSON")

        rp_layout.addLayout(response_hdr)
        rp_layout.addWidget(self._response_tabs, stretch=1)
        response_panel.setLayout(rp_layout)

        splitter.addWidget(prompt_panel)
        splitter.addWidget(response_panel)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

        layout.addLayout(top_bar)
        layout.addWidget(splitter, stretch=1)

        root.setLayout(layout)
        self.setCentralWidget(root)

        # Status bar
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)

        # Signals
        self.plan_btn.clicked.connect(self.on_plan)
        self.execute_btn.clicked.connect(self.on_execute)
        self._settings_btn.clicked.connect(self.on_settings)
        self._start_server_btn.clicked.connect(self.on_start_server)
        self._stop_server_btn.clicked.connect(self.on_stop_server)
        self._install_edit_menu()
        self._update_model_badge()

    # ── Output rendering ──────────────────────────────────────────────────────

    def _make_table(self, headers: list[str]) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setWordWrap(True)
        table.verticalHeader().setVisible(False)
        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        for index in range(len(headers) - 1):
            header.setSectionResizeMode(index, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(len(headers) - 1, QHeaderView.ResizeMode.Stretch)
        return table

    def _set_table_rows(self, table: QTableWidget, rows: list[list[str]]) -> None:
        table.setRowCount(0)
        for row_idx, values in enumerate(rows):
            table.insertRow(row_idx)
            for col_idx, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(row_idx, col_idx, item)
        table.resizeRowsToContents()

    def _show_output(self, payload: dict, is_error: bool = False) -> None:
        self._last_payload = payload
        self._response_raw.setPlainText(json.dumps(payload, indent=2, ensure_ascii=False))

        if is_error:
            self._show_error_payload(payload)
        elif "planned_actions" in payload:
            self._show_plan_payload(payload)
        elif "execution_report" in payload or "executed_count" in payload:
            self._show_execution_payload(payload)
        else:
            self._summary_title.setText("Response")
            self._summary_detail.setText(json.dumps(payload, indent=2, ensure_ascii=False))
            self._confidence_bar.setValue(0)
            self._approval_lbl.setText("")
            self._response_tabs.setCurrentWidget(self._summary_tab)

    def _show_plan_payload(self, payload: dict) -> None:
        self._last_plan_payload = payload
        actions = payload.get("planned_actions", []) or []
        confidence = max(0, min(100, int(float(payload.get("confidence", 0.0)) * 100)))
        requires_approval = bool(payload.get("requires_approval", False))

        self._summary_title.setText(f"Plan ready: {len(actions)} action(s)")
        detail = payload.get("explanation") or "No explanation provided."
        self._summary_detail.setText(str(detail))
        self._confidence_bar.setValue(confidence)
        self._approval_lbl.setText(
            "Approval: required for destructive actions"
            if requires_approval
            else "Approval: not required"
        )
        self._approval_lbl.setStyleSheet(
            f"font-size: 12px; color: {'#b45309' if requires_approval else '#16a34a'};"
        )

        rows: list[list[str]] = []
        for idx, action in enumerate(actions, start=1):
            destructive = bool(action.get("destructive", False))
            rows.append([
                str(idx),
                str(action.get("tool", "")),
                "Destructive" if destructive else "Safe",
                str(action.get("description", "")),
                _json_text(action.get("args", [])),
                str(action.get("address", "")),
            ])
        self._set_table_rows(self._actions_table, rows)
        self._set_table_rows(self._execution_table, [])
        self._response_tabs.setCurrentWidget(self._actions_table if rows else self._summary_tab)

    def _show_execution_payload(self, payload: dict) -> None:
        report = payload.get("execution_report", []) or []
        dry_run = bool(payload.get("dry_run", False))
        count = payload.get("executed_count", len(report))
        if dry_run:
            self._summary_title.setText(f"Dry run complete: {count} action(s)")
            self._summary_detail.setText("No OSC messages were sent to Ableton.")
        else:
            self._summary_title.setText(f"Executed: {count} action(s)")
            self._summary_detail.setText("OSC messages were sent to Ableton for this plan.")
        self._confidence_bar.setValue(
            max(0, min(100, int(float(self._last_plan_payload.get("confidence", 0.0)) * 100)))
            if self._last_plan_payload
            else 0
        )
        self._approval_lbl.setText(
            "Execution mode: dry run" if dry_run else "Execution mode: live OSC"
        )
        self._approval_lbl.setStyleSheet(
            f"font-size: 12px; color: {'#0891b2' if dry_run else '#16a34a'};"
        )

        rows: list[list[str]] = []
        for idx, item in enumerate(report, start=1):
            if isinstance(item, dict):
                status = str(item.get("status", "ok"))
                message = str(item.get("error") or item.get("message") or item.get("result") or "")
                rows.append([
                    str(item.get("index", idx - 1)),
                    status,
                    str(item.get("tool", "")),
                    _json_text(item.get("args", [])),
                    str(item.get("address", "")),
                    message,
                ])
            else:
                rows.append([str(idx), "info", str(item), "", "", ""])
        self._set_table_rows(self._execution_table, rows)
        self._response_tabs.setCurrentWidget(self._execution_table if rows else self._summary_tab)

    def _show_error_payload(self, payload: dict) -> None:
        message = payload.get("error", payload) if isinstance(payload, dict) else str(payload)
        self._summary_title.setText("Error")
        self._summary_detail.setText(str(message))
        self._confidence_bar.setValue(0)
        self._approval_lbl.setText("")
        self._set_table_rows(self._execution_table, [])
        self._response_tabs.setCurrentWidget(self._summary_tab)

    def _update_model_badge(self) -> None:
        provider = self._gui_cfg.get("provider", "")
        model = self._gui_cfg.get("model", "")
        if not provider or not model:
            try:
                live = self._backend.get_settings()
                provider = live.get("modelito_provider", provider)
                model = live.get("modelito_model", model)
            except Exception:
                pass
        self._current_model_lbl.setText(f"{provider} / {model}" if provider and model else "")

    def _install_edit_menu(self) -> None:
        edit_menu = self.menuBar().addMenu("Edit")
        actions = [
            ("Cut", QKeySequence.StandardKey.Cut, lambda: self._dispatch_text_action("cut")),
            ("Copy", QKeySequence.StandardKey.Copy, lambda: self._dispatch_text_action("copy")),
            ("Paste", QKeySequence.StandardKey.Paste, lambda: self._dispatch_text_action("paste")),
            ("Delete", QKeySequence.StandardKey.Delete, lambda: self._dispatch_text_action("delete")),
            (
                "Select All",
                QKeySequence.StandardKey.SelectAll,
                lambda: self._dispatch_text_action("select_all"),
            ),
        ]
        for label, shortcut, callback in actions:
            action = QAction(label, self)
            action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(callback)
            edit_menu.addAction(action)

    def _dispatch_text_action(self, action: str) -> None:
        widget = QApplication.focusWidget()
        if isinstance(widget, QTableWidget) and action == "copy":
            self._copy_table_selection(widget)
            return
        if action == "cut" and hasattr(widget, "cut"):
            widget.cut()
        elif action == "copy" and hasattr(widget, "copy"):
            widget.copy()
        elif action == "paste" and hasattr(widget, "paste"):
            widget.paste()
        elif action == "select_all" and hasattr(widget, "selectAll"):
            widget.selectAll()
        elif action == "delete":
            if isinstance(widget, QLineEdit):
                widget.del_()
            elif isinstance(widget, QTextEdit):
                cursor = widget.textCursor()
                if cursor.hasSelection():
                    cursor.removeSelectedText()
                else:
                    cursor.deleteChar()

    def _copy_table_selection(self, table: QTableWidget) -> None:
        indexes = table.selectedIndexes()
        if not indexes:
            return
        rows = sorted({idx.row() for idx in indexes})
        cols = sorted({idx.column() for idx in indexes})
        lines = []
        for row in rows:
            values = []
            for col in cols:
                item = table.item(row, col)
                values.append(item.text() if item else "")
            lines.append("\t".join(values))
        QApplication.clipboard().setText("\n".join(lines))

    # ── UI state ──────────────────────────────────────────────────────────────

    def _set_busy(self, busy: bool) -> None:
        self.plan_btn.setEnabled(not busy)
        self.execute_btn.setEnabled(not busy and self._can_execute())
        self.prompt.setReadOnly(busy)

    def _can_execute(self) -> bool:
        return bool(self.last_plan_id) and self._plan_action_count > 0 and not self._plan_executed

    # ── Plan ──────────────────────────────────────────────────────────────────

    def on_plan(self) -> None:
        prompt = self.prompt.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "No Prompt", "Please enter a prompt first.")
            return
        self._set_busy(True)
        self.last_plan_id = ""
        self._plan_action_count = 0
        self._plan_executed = False
        self.last_requires_approval = False
        self._plan_id_lbl.setText("")
        self._status_bar.showMessage("Planning… (this may take a few seconds)")

        self._worker = _PlanWorker(self._backend, prompt)
        self._worker.finished.connect(self._on_plan_done)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.start()

    def _on_plan_done(self, payload: dict) -> None:
        self.last_plan_id           = payload.get("plan_id", "")
        self.last_requires_approval = bool(payload.get("requires_approval", False))
        self._plan_action_count = len(payload.get("planned_actions", []) or [])
        self._plan_id_lbl.setText(f"Plan: {_short_id(self.last_plan_id)}" if self.last_plan_id else "")
        self._show_output(payload)
        self._set_busy(False)
        self._status_bar.showMessage(
            f"Plan ready — {self._plan_action_count} action(s). Review and click Execute."
        )

    # ── Execute ───────────────────────────────────────────────────────────────

    def on_execute(self) -> None:
        if not self.last_plan_id:
            QMessageBox.warning(self, "No Plan", "Create a plan first.")
            return
        dry_run = self.dry_run.isChecked()
        if self.last_requires_approval and not dry_run and not self._allow_destructive:
            QMessageBox.warning(
                self, "Approval Required",
                "This plan includes destructive actions.\n\n"
                "Enable 'Allow destructive execution' in Settings → Execution, "
                "or keep Dry run checked.",
            )
            return
        self._set_busy(True)
        self._status_bar.showMessage("Executing…")

        self._worker = _ExecuteWorker(
            self._backend, self.last_plan_id,
            dry_run=dry_run,
            approved=self._allow_destructive or dry_run,
        )
        self._worker.finished.connect(self._on_execute_done)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.start()

    def _on_execute_done(self, payload: dict) -> None:
        self._show_output(payload)
        if not payload.get("dry_run"):
            self._plan_executed = True
        self._set_busy(False)
        label = "Dry run complete — no changes sent to Ableton." if payload.get("dry_run") \
                else f"Executed {payload.get('executed_count', '?')} action(s)."
        self._status_bar.showMessage(label)

    # ── Error ─────────────────────────────────────────────────────────────────

    def _on_error(self, message: str) -> None:
        self._set_busy(False)
        self._status_bar.showMessage(f"Error: {message}")
        self._show_output({"error": message}, is_error=True)

    # ── Server control ────────────────────────────────────────────────────────

    def _update_server_ui(self) -> None:
        running = self._server_proc is not None and self._server_proc.poll() is None
        self._start_server_btn.setEnabled(not running)
        self._stop_server_btn.setEnabled(running)

        if running:
            self._server_status_lbl.setText(f"Server running at {self._server_url}")
            self._server_status_lbl.setStyleSheet("font-size: 12px; color: #16a34a;")
        elif _ping(self._server_url):
            self._server_status_lbl.setText(f"External server at {self._server_url}")
            self._server_status_lbl.setStyleSheet("font-size: 12px; color: #2563eb;")
            self._start_server_btn.setEnabled(False)
            self._stop_server_btn.setEnabled(False)
        else:
            self._server_status_lbl.setText("No server — using embedded mode")
            self._server_status_lbl.setStyleSheet("font-size: 12px; color: #6b7280;")

    def on_start_server(self) -> None:
        self._start_server_btn.setEnabled(False)
        self._server_status_lbl.setText("Starting server…")
        self._server_status_lbl.setStyleSheet("font-size: 12px; color: #d97706;")
        backend_script = _PROJECT_ROOT / "backend" / "main.py"
        self._server_proc = subprocess.Popen(
            [sys.executable, str(backend_script)], cwd=str(_PROJECT_ROOT)
        )
        self._server_watcher = _ServerStartWatcher(self._server_url)
        self._server_watcher.ready.connect(self._on_server_ready)
        self._server_watcher.failed.connect(self._on_server_failed)
        self._server_watcher.finished.connect(self._server_watcher.deleteLater)
        self._server_watcher.start()

    def _on_server_ready(self) -> None:
        self._backend, mode = _choose_backend(self._server_url, self._gui_cfg.get("token", ""))
        self._status_bar.showMessage(mode)
        self._update_server_ui()

    def _on_server_failed(self, message: str) -> None:
        self._server_status_lbl.setText(f"Server failed: {message}")
        self._server_status_lbl.setStyleSheet("font-size: 12px; color: #dc2626;")
        if self._server_proc and self._server_proc.poll() is None:
            self._server_proc.terminate()
        self._server_proc = None
        self._update_server_ui()

    def on_stop_server(self) -> None:
        if self._server_proc and self._server_proc.poll() is None:
            self._server_proc.terminate()
            try:
                self._server_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._server_proc.kill()
        self._server_proc = None
        self._backend, mode = _choose_backend(self._server_url, self._gui_cfg.get("token", ""))
        self._status_bar.showMessage(mode)
        self._update_server_ui()

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
        dlg.exec()

        # Re-read persisted settings so Save-without-close changes are reflected.
        self._gui_cfg = _load_gui_settings()

        self._server_url = self._gui_cfg.get("base_url", self._server_url)
        token            = self._gui_cfg.get("token", "")
        self._backend, mode = _choose_backend(self._server_url, token)
        self._status_bar.showMessage(mode)
        self._update_server_ui()
        self._allow_destructive = bool(self._gui_cfg.get("allow_destructive", False))
        self.dry_run.setChecked(bool(self._gui_cfg.get("dry_run", True)))
        self._update_model_badge()


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    app = QApplication(sys.argv)
    _apply_theme(app)
    win = MainWindow()
    win.resize(900, 680)
    win.show()
    app.exec()


if __name__ == "__main__":
    main()
