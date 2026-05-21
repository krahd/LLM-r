from pathlib import Path

from llmr.bridge_install_paths import (
    BRIDGE_FOLDER_NAME,
    derive_bridge_init_path,
    derive_bridge_install_target,
    derive_remote_scripts_path,
    detect_bridge_install_state,
    detect_user_library_candidates,
)


def test_derives_remote_scripts_and_target_paths(tmp_path: Path) -> None:
    user_library = tmp_path / "My Ableton" / "User Library"
    assert derive_remote_scripts_path(user_library) == user_library / "Remote Scripts"
    assert derive_bridge_install_target(
        user_library) == user_library / "Remote Scripts" / BRIDGE_FOLDER_NAME


def test_detects_valid_install(tmp_path: Path) -> None:
    base = tmp_path / "llmr-bridge-valid"
    target = derive_bridge_install_target(base)
    target.mkdir(parents=True, exist_ok=True)
    derive_bridge_init_path(base).write_text("# init\n", encoding="utf-8")
    assert detect_bridge_install_state(base) == "installed"


def test_detects_missing_install(tmp_path: Path) -> None:
    base = tmp_path / "llmr-bridge-missing"
    assert detect_bridge_install_state(base) == "not_installed"


def test_detects_double_nested_install(tmp_path: Path) -> None:
    user_library = tmp_path / "Ableton" / "User Library"
    nested = derive_bridge_install_target(user_library) / BRIDGE_FOLDER_NAME
    nested.mkdir(parents=True)
    (nested / "__init__.py").write_text("# init\n", encoding="utf-8")
    assert detect_bridge_install_state(user_library) == "double_nested"


def test_candidate_detection_handles_missing_music_directory(tmp_path: Path) -> None:
    fake_home = tmp_path / "home-without-music"
    fake_home.mkdir()
    assert detect_user_library_candidates(home=fake_home, volume_roots=[]) == []


def test_candidate_detection_finds_external_volume_style_path(tmp_path: Path) -> None:
    volume_root = tmp_path / "ExternalSSD"
    user_library = volume_root / "Ableton" / "User Library"
    (user_library / "Remote Scripts").mkdir(parents=True)

    candidates = detect_user_library_candidates(home=tmp_path / "home", volume_roots=[volume_root])
    assert user_library in candidates


def test_detection_not_limited_to_default_music_path(tmp_path: Path) -> None:
    fake_home = tmp_path / "home"
    fake_home.mkdir()

    external = tmp_path / "Volumes" / "Portable" / "Ableton" / "User Library"
    (external / "Remote Scripts").mkdir(parents=True)

    candidates = detect_user_library_candidates(
        home=fake_home, volume_roots=[tmp_path / "Volumes" / "Portable"])
    assert external in candidates
