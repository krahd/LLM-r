from pathlib import Path


CPP_FILE = Path("native/vst3/llmr_vst3_plugin.cpp")


def test_duration_and_fallback_helpers_exist() -> None:
    source = CPP_FILE.read_text(encoding="utf-8")

    assert "double parseRequestedDurationBeats(" in source
    assert "bool isDrumCompositionRequest(" in source
    assert "bool isPianoCompositionRequest(" in source
    assert "NSDictionary *buildJazzDrumPlan(" in source
    assert "NSDictionary *buildPianoBalladPlan(" in source


def test_planning_uses_piano_and_drum_fallbacks() -> None:
    source = CPP_FILE.read_text(encoding="utf-8")

    assert "fallback = localPianoPlan(userPrompt);" in source
    assert "fallback = localDrumLoopPlan(userPrompt);" in source


def test_llm_waits_longer_and_can_continue_or_cancel() -> None:
    source = CPP_FILE.read_text(encoding="utf-8")

    assert "continueWaitingDecisionForLLM" in source
    assert '@"Wait 5 More Minutes"' in source
    assert '@"Wait Without Timeout"' in source
    assert '@"Cancel Request"' in source
    assert "[request setTimeoutInterval:24.0 * 60.0 * 60.0];" in source
