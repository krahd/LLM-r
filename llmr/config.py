import json
import os
from pathlib import Path

from pydantic import BaseModel

_SETTINGS_PATH = Path(os.getenv("LLMR_SETTINGS_PATH", ".llmr/settings.json"))
_DEFAULT_PLANNER_EXTRA_PROMPT_PATH = (
    Path(__file__).resolve().parent.parent / "docs" / "LLM_ASSISTANT_PROMPT.md"
)


def _read_file() -> dict:
    if _SETTINGS_PATH.exists():
        try:
            return json.loads(_SETTINGS_PATH.read_text())
        except Exception:
            return {}
    return {}


# Read once at startup; env vars take precedence over file, file over hardcoded defaults.
_file_cfg: dict = _read_file()


def _resolve(env_key: str, file_key: str, default):
    v = os.getenv(env_key)
    if v is not None:
        return v
    v = _file_cfg.get(file_key)
    if v is not None:
        return v
    return default


def _resolve_bool(env_key: str, file_key: str, default: bool) -> bool:
    v = _resolve(env_key, file_key, default)
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() not in {"0", "false", "no", "off", ""}


class Settings(BaseModel):
    ableton_host: str
    ableton_port: int
    modelito_model: str
    modelito_provider: str
    planner_extra_prompt_enabled: bool
    planner_extra_prompt_path: str
    app_host: str
    app_port: int
    plan_store_path: str
    macro_store_path: str
    session_store_path: str
    api_token: str

    def save(self) -> None:
        """Persist runtime-editable settings to disk."""
        _SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        _SETTINGS_PATH.write_text(
            json.dumps(
                {
                    "ableton_host": self.ableton_host,
                    "ableton_port": self.ableton_port,
                    "modelito_model": self.modelito_model,
                    "modelito_provider": self.modelito_provider,
                    "planner_extra_prompt_enabled": self.planner_extra_prompt_enabled,
                    "planner_extra_prompt_path": self.planner_extra_prompt_path,
                    "api_token": self.api_token,
                },
                indent=2,
            )
        )


settings = Settings(
    ableton_host=_resolve("LLMR_ABLETON_HOST", "ableton_host", "127.0.0.1"),
    ableton_port=int(_resolve("LLMR_ABLETON_PORT", "ableton_port", 11000)),
    modelito_model=_resolve("LLMR_MODEL", "modelito_model", "gpt-4.1-mini"),
    modelito_provider=_resolve("LLMR_PROVIDER", "modelito_provider", "openai"),
    planner_extra_prompt_enabled=_resolve_bool(
        "LLMR_PLANNER_EXTRA_PROMPT_ENABLED",
        "planner_extra_prompt_enabled",
        True,
    ),
    planner_extra_prompt_path=_resolve(
        "LLMR_PLANNER_EXTRA_PROMPT_PATH",
        "planner_extra_prompt_path",
        str(_DEFAULT_PLANNER_EXTRA_PROMPT_PATH),
    ),
    app_host=os.getenv("LLMR_HOST", "0.0.0.0"),
    app_port=int(os.getenv("LLMR_PORT", "8787")),
    plan_store_path=os.getenv("LLMR_PLAN_STORE_PATH", ".llmr/plans.json"),
    macro_store_path=os.getenv("LLMR_MACRO_STORE_PATH", ".llmr/macros.json"),
    session_store_path=os.getenv("LLMR_SESSION_STORE_PATH", ".llmr/sessions.json"),
    api_token=_resolve("LLMR_API_TOKEN", "api_token", ""),
)
