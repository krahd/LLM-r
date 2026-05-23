from pathlib import Path


CPP_FILE = Path("native/vst3/llmr_vst3_plugin.cpp")


def _function_body(source: str, signature: str) -> str:
    start = source.find(signature)
    assert start >= 0, f"Could not find function signature: {signature}"

    brace_start = source.find("{", start)
    assert brace_start >= 0, f"Could not find function body start for: {signature}"

    depth = 0
    for index in range(brace_start, len(source)):
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[brace_start + 1:index]

    raise AssertionError(f"Could not find function body end for: {signature}")


def test_show_advanced_settings_has_no_automatic_runtime_probes() -> None:
    source = CPP_FILE.read_text(encoding="utf-8")
    body = _function_body(source, "void showAdvancedSettings()")

    assert "checkDeviceBridgeStatus();" not in body
    assert "ollamaListModels();" not in body
    assert "ollamaRefreshOnlineModels(" not in body


def test_http_request_has_main_thread_guard() -> None:
    source = CPP_FILE.read_text(encoding="utf-8")
    body = _function_body(source, "NSString *httpRequest(")

    assert "[NSThread isMainThread]" in body
    assert "blocking HTTP request attempted on the UI thread" in body


def test_device_bridge_check_uses_short_global_status_updates() -> None:
    source = CPP_FILE.read_text(encoding="utf-8")
    body = _function_body(source, "void checkDeviceBridgeStatus()")

    assert "setStatus(rs);" not in body
    assert "Device Bridge reachable." in body
    assert "Device Bridge not reachable. See Advanced Settings." in body
    assert "Choose Ableton User Library before installing the bridge." in body
