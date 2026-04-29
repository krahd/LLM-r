#!/usr/bin/env bash
set -euo pipefail

# Build local VST3 bundles, install them into Ableton's User Library plug-in
# folder, quit Ableton Live if running, and open the local test set.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VST3_BUILD_DIR="${VST3_BUILD_DIR:-$REPO_ROOT/build/vst3}"
TEST_VST3_SRC="${TEST_VST3_SRC:-$REPO_ROOT/test_assets/vst3}"
VST3_TARGET="${1:-$HOME/Music/Ableton/User Library/Plug-Ins/VST3}"
VST3_TARGET_EXPANDED="${VST3_TARGET/#\~/$HOME}"
TEST_SET="$REPO_ROOT/Test Set Project/Test Set.als"

usage() {
  cat <<EOF
Usage: $(basename "$0") [VST3_TARGET_DIR]
Builds local VST3 bundles, installs them into Ableton's User Library plug-in
folder, and opens Test Set Project/Test Set.als.

Defaults:
  VST3_TARGET_DIR=$HOME/Music/Ableton/User Library/Plug-Ins/VST3
  VST3_BUILD_DIR=$REPO_ROOT/build/vst3

Build command selection:
  1. LLMR_VST3_BUILD_CMD, if set
  2. scripts/build_vst3.sh, if present and executable
  3. test_assets/vst3/*.vst3 copied into build/vst3 as deterministic test bundles

Test switches:
  LLMR_SKIP_ABLETON_QUIT=1 skips quitting Ableton
  LLMR_SKIP_ABLETON_OPEN=1 skips opening the test set
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

build_vst3_bundles() {
  rm -rf "$VST3_BUILD_DIR"
  mkdir -p "$VST3_BUILD_DIR"

  if [[ -n "${LLMR_VST3_BUILD_CMD:-}" ]]; then
    echo "Building VST3 bundles with LLMR_VST3_BUILD_CMD..."
    (cd "$REPO_ROOT" && bash -lc "$LLMR_VST3_BUILD_CMD")
    return
  fi

  if [[ -x "$REPO_ROOT/scripts/build_vst3.sh" ]]; then
    echo "Building VST3 bundles with scripts/build_vst3.sh..."
    "$REPO_ROOT/scripts/build_vst3.sh" "$VST3_BUILD_DIR"
    return
  fi

  if [[ -d "$TEST_VST3_SRC" ]]; then
    echo "Building test VST3 bundles from: $TEST_VST3_SRC"
    while IFS= read -r -d '' bundle; do
      cp -a "$bundle" "$VST3_BUILD_DIR/"
    done < <(find "$TEST_VST3_SRC" -maxdepth 1 -name '*.vst3' -not -name '.*' -type d -print0 2>/dev/null || true)
    return
  fi

  echo "No VST3 build command or test VST3 source found." >&2
  exit 1
}

find_built_vst3_bundles() {
  find "$VST3_BUILD_DIR" -maxdepth 1 -name '*.vst3' -not -name '.*' -type d -print0 2>/dev/null
}

install_vst3_bundles() {
  local installed=0

  mkdir -p "$VST3_TARGET_EXPANDED"
  echo "Installing built VST3 bundles to: $VST3_TARGET_EXPANDED"

  while IFS= read -r -d '' bundle; do
    local name
    name="$(basename "$bundle")"
    echo "  $name -> $VST3_TARGET_EXPANDED/"
    rsync -a --delete "$bundle" "$VST3_TARGET_EXPANDED/"
    installed=1
  done < <(find_built_vst3_bundles)

  if [[ $installed -eq 0 ]]; then
    echo "No .vst3 bundles were built in $VST3_BUILD_DIR" >&2
    exit 1
  fi
}

quit_ableton_live() {
  if [[ "${LLMR_SKIP_ABLETON_QUIT:-0}" == "1" ]]; then
    echo "Skipping Ableton quit because LLMR_SKIP_ABLETON_QUIT=1"
    return
  fi

  echo "Attempting to quit Ableton Live if it is running..."
  shopt -s nullglob
  local apps=(/Applications/Ableton\ Live*.app)
  shopt -u nullglob

  if [[ ${#apps[@]} -gt 0 ]]; then
    echo "Found Ableton app bundles: ${apps[*]}"
    for app_path in "${apps[@]}"; do
      local app_name
      app_name="$(basename "$app_path" .app)"
      echo "Quitting: $app_name"
      osascript -e "tell application \"$app_name\" to quit" >/dev/null 2>&1 || true
    done
  else
    echo "No Ableton application bundle found under /Applications"
  fi

  pkill -f "Ableton Live" >/dev/null 2>&1 || true
}

select_ableton_app() {
  shopt -s nullglob
  local apps=(/Applications/Ableton\ Live*.app)
  shopt -u nullglob
  local selected=""

  for app_path in "${apps[@]}"; do
    if [[ "$(basename "$app_path")" == "Ableton Live 12 Suite.app" ]]; then
      selected="$app_path"
      break
    fi
  done

  if [[ -z "$selected" ]]; then
    for app_path in "${apps[@]}"; do
      local name
      name="$(basename "$app_path")"
      if [[ "$name" != *"Beta.app" && "$name" != *"beta.app" ]]; then
        selected="$app_path"
        break
      fi
    done
  fi

  if [[ -z "$selected" && ${#apps[@]} -gt 0 ]]; then
    selected="${apps[0]}"
  fi

  if [[ -n "$selected" ]]; then
    basename "$selected" .app
  fi
}

open_test_set() {
  if [[ "${LLMR_SKIP_ABLETON_OPEN:-0}" == "1" ]]; then
    echo "Skipping Ableton open because LLMR_SKIP_ABLETON_OPEN=1"
    return
  fi

  local app_name
  app_name="$(select_ableton_app)"

  echo "Opening Test Set: $TEST_SET"
  if [[ -n "$app_name" ]]; then
    echo "Opening with: $app_name"
    open -a "$app_name" "$TEST_SET" || open "$TEST_SET" || echo "Could not open Test Set in Ableton."
  else
    open "$TEST_SET" || echo "Could not open Test Set (no Ableton app found)."
  fi
}

build_vst3_bundles
install_vst3_bundles
quit_ableton_live
sleep 1
open_test_set

echo "Done."
