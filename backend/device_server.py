#!/usr/bin/env python3
"""Development-only HTTP contract simulator for LLM-r Device Bridge.

Production device loading is handled by remote_scripts/LLMRDeviceBridge, which
runs inside Ableton Live's control-surface Python runtime. An external Python
process cannot import Ableton's Live API, so this server intentionally does not
attempt to load real devices unless simulation mode is enabled.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

log_dir = Path.home() / ".llmr"
log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "device_backend.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM-r Device Bridge Simulator")


class DeviceLoadRequest(BaseModel):
    track_index: int = Field(ge=0)
    query: str = Field(min_length=1, max_length=256)
    device_type: str = "instrument"


def _simulate_enabled() -> bool:
    return os.getenv("LLMR_DEVICE_SERVER_SIMULATE", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _require_simulation() -> None:
    if not _simulate_enabled():
        raise HTTPException(
            status_code=503,
            detail=(
                "This process cannot access Ableton's Live API. Install and enable "
                "the LLMRDeviceBridge Remote Script in Ableton Live, or set "
                "LLMR_DEVICE_SERVER_SIMULATE=1 for contract testing."
            ),
        )


@app.get("/health")
async def health_check() -> dict[str, Any]:
    return {
        "status": "ok",
        "mode": "simulator",
        "simulated_loads_enabled": _simulate_enabled(),
        "live_api_available": False,
    }


@app.get("/api/devices/list")
async def list_devices(query: str = "", device_type: str = "all") -> dict[str, Any]:
    _require_simulation()
    devices = [
        {"name": "Drum Rack", "type": "drum", "is_loadable": True},
        {"name": "Wavetable", "type": "instrument", "is_loadable": True},
        {"name": "Operator", "type": "instrument", "is_loadable": True},
        {"name": "Echo", "type": "audio_effect", "is_loadable": True},
        {"name": "EQ Eight", "type": "audio_effect", "is_loadable": True},
    ]
    normalized_query = query.strip().lower()
    normalized_type = device_type.strip().lower()
    if normalized_query:
        devices = [item for item in devices if normalized_query in item["name"].lower()]
    if normalized_type not in {"", "all"}:
        devices = [item for item in devices if item["type"] == normalized_type]
    return {"devices": devices, "count": len(devices)}


@app.post("/api/devices/load")
async def load_device(request: DeviceLoadRequest) -> dict[str, Any]:
    _require_simulation()
    logger.info(
        "Simulated device load: %s on track %s (%s)",
        request.query,
        request.track_index,
        request.device_type,
    )
    return {
        "status": "simulated",
        "track_index": request.track_index,
        "query": request.query,
        "device_type": request.device_type,
        "loaded_item": request.query,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8788, log_level="info")
