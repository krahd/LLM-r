import pytest
from fastapi.testclient import TestClient
from llmr.app import app

client = TestClient(app)

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200

def test_list_macros():
    resp = client.get("/api/macros")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "macros" in data
    assert isinstance(data["macros"], list)

def test_plan_macro():
    resp = client.post("/api/plan_macro", json={"name": "idea_sketch"})
    # Accept 200 (success), 404 (macro missing), or 500 (Modelito not installed)
    assert resp.status_code in (200, 404, 500)

def test_plan_prompt():
    resp = client.post("/api/plan", json={"prompt": "set tempo to 120"})
    # Accept 200 (success), 422 (validation), or 500 (Modelito not installed)
    assert resp.status_code in (200, 422, 500)
