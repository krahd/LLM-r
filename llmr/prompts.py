from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import Any, Iterable, Protocol


DEFAULT_PLANNER_EXTRA_PROMPT_PATH = (
    Path(__file__).resolve().parent.parent / "docs" / "LLM_ASSISTANT_PROMPT.md"
)
PACKAGED_PLANNER_EXTRA_PROMPT = "LLM_ASSISTANT_PROMPT.md"
PLANNER_PROMPT_PACKAGE_DIR = "planner_prompts"
DEFAULT_PLANNER_PROMPT_SECTIONS = (
    "core_planner.md",
    "ableton_context.md",
    "composition_contract.md",
    "drums.md",
    "piano.md",
    "effects_and_automation.md",
)


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


def load_packaged_prompt_section(name: str) -> str:
    try:
        return (
            files("llmr")
            .joinpath(PLANNER_PROMPT_PACKAGE_DIR)
            .joinpath(name)
            .read_text(encoding="utf-8")
            .strip()
        )
    except OSError:
        return ""


def load_packaged_prompt_sections(
    section_names: Iterable[str] = DEFAULT_PLANNER_PROMPT_SECTIONS,
) -> list[str]:
    return [section for name in section_names if (section := load_packaged_prompt_section(name))]


def render_tool_capabilities(tool_capabilities: Iterable[Any]) -> str:
    rows: list[str] = []
    for cap in tool_capabilities:
        rows.append(
            "- "
            f"{cap.tool.value} ({cap.domain}, transport={cap.transport}, safety={cap.safety}): "
            f"{cap.description}; args={cap.args_schema}"
        )
    return "\n".join(rows)


def render_ableton_context(ableton_context: dict[str, Any] | None = None) -> str:
    if not ableton_context:
        return (
            "Ableton runtime context is unavailable. Assume tempo=120 BPM, 4/4, "
            "Session View semantics for clip tools, and avoid claiming knowledge of "
            "selected tracks, selected clips, or Arrangement View."
        )
    lines = []
    for key in sorted(ableton_context):
        value = ableton_context[key]
        lines.append(f"- {key}: {value!r}")
    return "\n".join(lines)


def compose_planner_prompt(
    tool_capabilities: Iterable[Any],
    *,
    extra_prompt: str = "",
    ableton_context: dict[str, Any] | None = None,
) -> str:
    sections = load_packaged_prompt_sections()
    prompt = "\n\n".join(sections)
    prompt += "\n\n## Available executable tools\n"
    prompt += render_tool_capabilities(tool_capabilities)
    prompt += "\n\n## Current Ableton context\n"
    prompt += render_ableton_context(ableton_context)
    if extra_prompt.strip():
        prompt += f"\n\n## Additional optional guidance\n{extra_prompt.strip()}\n"
    return prompt.strip() + "\n"


def compose_repair_prompt(
    *,
    invalid_output: str,
    tool_capabilities: Iterable[Any],
    extra_prompt: str = "",
    ableton_context: dict[str, Any] | None = None,
) -> str:
    prompt = compose_planner_prompt(
        tool_capabilities,
        extra_prompt=extra_prompt,
        ableton_context=ableton_context,
    )
    prompt += (
        "\nThe previous model output was not valid executable LLM-r JSON. "
        "Repair it now. Return ONLY the JSON envelope. Do not add Markdown.\n\n"
        "Invalid output to repair:\n"
        f"{invalid_output.strip()}\n"
    )
    return prompt
