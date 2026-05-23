from pathlib import Path


WEB_INDEX = Path("web/index.html")


def _read_web_index() -> str:
    assert WEB_INDEX.exists(), "web/index.html must exist"
    return WEB_INDEX.read_text(encoding="utf-8")


def test_web_index_exists() -> None:
    assert WEB_INDEX.exists()


def test_web_index_contains_required_ids() -> None:
    html = _read_web_index()
    required_ids = [
        "basicProvider",
        "basicModel",
        "saveBasicSettingsBtn",
        "refreshBasicModelsBtn",
        "localRuntimePanel",
        "localRuntimeCards",
        "planBtn",
        "execBtn",
        "dry",
        "autoApprove",
        "approve",
        "planView",
        "runView",
        "detailsView",
        "macroSelect",
        "capsList",
    ]
    for required_id in required_ids:
        assert f'id="{required_id}"' in html


def test_web_index_contains_required_api_endpoints() -> None:
    html = _read_web_index()
    required_endpoints = [
        "/api/settings",
        "/api/readiness",
        "/api/ollama/status",
        "/api/omlx/status",
        "/api/macros",
        "/api/capabilities",
        "/api/plan",
    ]
    for endpoint in required_endpoints:
        assert endpoint in html


def test_web_index_contains_fallback_functions() -> None:
    html = _read_web_index()
    required_functions = [
        "function escapeHtml",
        "function renderPlan",
        "function updateControlStates",
    ]
    for function_name in required_functions:
        assert function_name in html


def test_web_index_contains_required_safety_copy() -> None:
    html = _read_web_index()
    required_copy = [
        "Preview only",
        "Live Execution Enabled",
        "Allow destructive actions",
    ]
    for text in required_copy:
        assert text in html
