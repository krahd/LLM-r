from __future__ import annotations

from typing import Any


COMMON_DEVICE_PARAMETER_MAPS: dict[str, dict[str, dict[str, Any]]] = {
    "*": {
        "device_on": {
            "index": 0,
            "min": 0.0,
            "max": 1.0,
            "aliases": ["on", "enabled", "activator", "device activator"],
            "description": "Ableton device activator, normalized 0..1.",
        }
    },
    "utility": {},
    "auto filter": {},
    "eq eight": {},
    "compressor": {},
    "reverb": {},
    "echo": {},
    "drum rack": {},
    "operator": {},
    "wavetable": {},
}


def _normalize(value: str) -> str:
    return " ".join(str(value or "").strip().lower().replace("_", " ").split())


def _combined_map(device_name: str) -> dict[str, dict[str, Any]]:
    maps: dict[str, dict[str, Any]] = dict(COMMON_DEVICE_PARAMETER_MAPS["*"])
    maps.update(COMMON_DEVICE_PARAMETER_MAPS.get(_normalize(device_name), {}))
    return maps


def resolve_parameter(device_name: str, parameter_name: str) -> dict[str, Any]:
    normalized_parameter = _normalize(parameter_name)
    for canonical, spec in _combined_map(device_name).items():
        names = [canonical, *spec.get("aliases", [])]
        if normalized_parameter in {_normalize(name) for name in names}:
            return {"name": canonical, **spec}
    raise ValueError(
        f"Unknown safe semantic parameter '{parameter_name}' for device '{device_name}'"
    )


def parameter_maps() -> dict[str, Any]:
    return {
        "maps": {
            device_name: _combined_map(device_name)
            for device_name in COMMON_DEVICE_PARAMETER_MAPS
        },
        "notes": [
            "Indexes are normalized Ableton parameter indexes used by AbletonOSC.",
            "Only mapped semantic names should be automated by name.",
            "Use runtime device parameter readback for unmapped parameters.",
        ],
    }
