from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Literal

BridgeInstallState = Literal["not_installed", "installed", "double_nested"]


BRIDGE_FOLDER_NAME = "LLMR_Bridge"


def derive_remote_scripts_path(user_library_path: str | Path) -> Path:
    return Path(user_library_path).expanduser() / "Remote Scripts"


def derive_bridge_install_target(user_library_path: str | Path) -> Path:
    return derive_remote_scripts_path(user_library_path) / BRIDGE_FOLDER_NAME


def derive_bridge_init_path(user_library_path: str | Path) -> Path:
    return derive_bridge_install_target(user_library_path) / "__init__.py"


def derive_double_nested_init_path(user_library_path: str | Path) -> Path:
    return derive_bridge_install_target(user_library_path) / BRIDGE_FOLDER_NAME / "__init__.py"


def detect_bridge_install_state(user_library_path: str | Path) -> BridgeInstallState:
    if derive_bridge_init_path(user_library_path).is_file():
        return "installed"
    if derive_double_nested_init_path(user_library_path).is_file():
        return "double_nested"
    return "not_installed"


def _add_candidate(candidates: list[Path], value: Path) -> None:
    resolved = value.expanduser()
    if resolved.is_dir() and resolved not in candidates:
        candidates.append(resolved)


def _iter_remote_scripts_user_library_parents(volume_root: Path) -> Iterable[Path]:
    try:
        for remote_scripts in volume_root.rglob("Remote Scripts"):
            parent = remote_scripts.parent
            if parent.name.lower().find("user library") != -1:
                yield parent
    except OSError:
        return


def detect_user_library_candidates(
    *,
    home: str | Path | None = None,
    volume_roots: Iterable[str | Path] | None = None,
) -> List[Path]:
    base_home = Path(home).expanduser() if home is not None else Path.home()
    candidates: list[Path] = []

    # Default Ableton User Library location.
    _add_candidate(candidates, base_home / "Music" / "Ableton" / "User Library")

    roots: list[Path]
    if volume_roots is None:
        volumes_root = Path("/Volumes")
        if volumes_root.is_dir():
            roots = [p for p in volumes_root.iterdir() if p.is_dir()]
        else:
            roots = []
    else:
        roots = [Path(root).expanduser() for root in volume_roots]

    for root in roots:
        if not root.is_dir():
            continue

        # Pattern: /Volumes/*/Ableton/User Library
        _add_candidate(candidates, root / "Ableton" / "User Library")

        # Pattern: /Volumes/*/*Ableton*/*User Library*
        try:
            for first in root.iterdir():
                if not first.is_dir():
                    continue
                if "ableton" not in first.name.lower():
                    continue
                for second in first.iterdir():
                    if second.is_dir() and "user library" in second.name.lower():
                        _add_candidate(candidates, second)
        except OSError:
            pass

        # Also pick User Library folders by finding plausible Remote Scripts parents.
        for parent in _iter_remote_scripts_user_library_parents(root):
            _add_candidate(candidates, parent)

    return candidates
