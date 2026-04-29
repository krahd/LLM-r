from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import Protocol


DEFAULT_PLANNER_EXTRA_PROMPT_PATH = (
    Path(__file__).resolve().parent.parent / "docs" / "LLM_ASSISTANT_PROMPT.md"
)
PACKAGED_PLANNER_EXTRA_PROMPT = "LLM_ASSISTANT_PROMPT.md"


class PlannerPromptSettings(Protocol):
    planner_extra_prompt_enabled: bool
    planner_extra_prompt_path: str


def load_prompt_text(path: str) -> str:
    if not path:
        return ""
    try:
        return Path(path).expanduser().read_text(encoding="utf-8")
    except OSError:
        return ""


def default_planner_extra_prompt() -> str:
    prompt = load_prompt_text(str(DEFAULT_PLANNER_EXTRA_PROMPT_PATH))
    if prompt:
        return prompt
    try:
        return files("llmr").joinpath(PACKAGED_PLANNER_EXTRA_PROMPT).read_text(encoding="utf-8")
    except OSError:
        return ""


def planner_extra_prompt(settings: PlannerPromptSettings) -> str:
    if not settings.planner_extra_prompt_enabled:
        return ""
    if Path(settings.planner_extra_prompt_path).expanduser() == DEFAULT_PLANNER_EXTRA_PROMPT_PATH:
        return default_planner_extra_prompt()
    return load_prompt_text(settings.planner_extra_prompt_path)
