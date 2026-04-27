from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib import request

try:
    from PyQt6.QtWidgets import (
        QApplication,
        QCheckBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "PyQt6 is required for the GUI scaffold. Install with: pip install PyQt6"
    ) from exc


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
            "POST",
            "/api/execute",
            {"plan_id": plan_id, "dry_run": dry_run, "approved": approved},
        )


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("LLM-r GUI (Scaffold)")
        self.client = ApiClient(
            base_url=os.getenv("LLMR_GUI_API_URL", "http://127.0.0.1:8787"),
            token=os.getenv("LLMR_GUI_API_TOKEN", ""),
        )
        self.last_plan_id = ""

        root = QWidget()
        layout = QVBoxLayout()

        self.prompt = QTextEdit()
        self.prompt.setPlaceholderText("Describe what you want Ableton to do...")

        button_row = QHBoxLayout()
        self.plan_btn = QPushButton("Plan")
        self.execute_btn = QPushButton("Execute")
        self.execute_btn.setEnabled(False)
        self.dry_run = QCheckBox("Dry run")
        self.dry_run.setChecked(True)
        button_row.addWidget(self.plan_btn)
        button_row.addWidget(self.execute_btn)
        button_row.addWidget(self.dry_run)

        self.plan_id = QLineEdit()
        self.plan_id.setReadOnly(True)
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        layout.addWidget(QLabel("Prompt"))
        layout.addWidget(self.prompt)
        layout.addLayout(button_row)
        layout.addWidget(QLabel("Latest Plan ID"))
        layout.addWidget(self.plan_id)
        layout.addWidget(QLabel("Response"))
        layout.addWidget(self.output)

        root.setLayout(layout)
        self.setCentralWidget(root)

        self.plan_btn.clicked.connect(self.on_plan)
        self.execute_btn.clicked.connect(self.on_execute)

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


def main() -> None:
    app = QApplication([])
    win = MainWindow()
    win.resize(840, 620)
    win.show()
    app.exec()


if __name__ == "__main__":
    main()
