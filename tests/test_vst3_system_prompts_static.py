from pathlib import Path


CPP_FILE = Path("native/vst3/llmr_vst3_plugin.cpp")


def test_system_prompt_storage_keys_and_window_actions_exist() -> None:
    source = CPP_FILE.read_text(encoding="utf-8")

    assert "llmr.vst3.system_prompt_custom" in source
    assert "llmr.vst3.system_prompt_preset" in source
    assert "openSystemPromptsWindow" in source
    assert "saveSystemPromptFromEditor" in source
    assert "saveSystemPromptToFile" in source
    assert "loadSystemPromptFromFile" in source
    assert "resetSystemPromptToDefault" in source
    assert "kLlmrEditorActionSystemPromptPresetChanged" in source
    assert "systemPromptPresetChanged" in source


def test_system_prompt_keeps_tool_catalog_appended() -> None:
    source = CPP_FILE.read_text(encoding="utf-8")

    assert "[prompt appendString:toolCatalogPrompt()];" in source
