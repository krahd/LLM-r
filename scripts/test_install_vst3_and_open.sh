#!/usr/bin/env bash
set -euo pipefail

# Install .vst3 bundles from build/vst3/ into the system VST3 folder,
# quit Ableton Live if running, and open the local test set.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VST3_SRC="${VST3_SRC:-$REPO_ROOT/build/vst3}"
VST3_TARGET="${1:-$HOME/Library/Audio/Plug-Ins/VST3}"
VST3_TARGET_EXPANDED="${VST3_TARGET/#\~/$HOME}"
TEST_SET="$REPO_ROOT/Test Set Project/Test Set.als"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  echo "Usage: $(basename "$0") [VST3_TARGET_DIR]"
  echo "Installs .vst3 bundles from build/vst3/ and opens Test Set Project/Test Set.als."
  echo "Defaults to ~/Library/Audio/Plug-Ins/VST3"
  exit 0
fi

echo "Installing VST3 bundles from: $VST3_SRC"
mkdir -p "$VST3_TARGET_EXPANDED"

installed=0
while IFS= read -r -d '' bundle; do
  name="$(basename "$bundle")"
  echo "  $name → $VST3_TARGET_EXPANDED/"
  rsync -a "$bundle" "$VST3_TARGET_EXPANDED/"
  installed=1
done < <(find "$VST3_SRC" -maxdepth 1 -name '*.vst3' -not -name '.*' -type d -print0 2>/dev/null || true)

if [[ $installed -eq 0 ]]; then
  echo "No .vst3 bundles found in $VST3_SRC"
  echo "Build your plugin first so that $VST3_SRC/YourPlugin.vst3 exists."
fi


echo "Attempting to quit Ableton Live if it's running..."
# Detect installed Ableton application bundles under /Applications
shopt -s nullglob
apps=(/Applications/Ableton\ Live*.app)
shopt -u nullglob
suite_app=""
suite_app_name=""
if [[ ${#apps[@]} -gt 0 ]]; then
  echo "Found Ableton app bundles: ${apps[*]}"
  # Prefer the explicit Suite build if present
  for p in "${apps[@]}"; do
    if [[ "$(basename "$p")" == "Ableton Live 12 Suite.app" ]]; then
      suite_app="$p"
      break
    fi
  done
  # If Suite not found, prefer a non-Beta build
  if [[ -z "$suite_app" ]]; then
    for p in "${apps[@]}"; do
      name="$(basename "$p")"
      if [[ "$name" != *"Beta.app" && "$name" != *"beta.app" ]]; then
        suite_app="$p"
        break
      fi
    done
  fi
  # Fallback: pick the first match
  if [[ -z "$suite_app" ]]; then
    suite_app="${apps[0]}"
  fi
  suite_app_name="$(basename "$suite_app" .app)"

  # Quit all found Ableton app bundles to ensure a clean restart
  for appPath in "${apps[@]}"; do
    appName="$(basename "$appPath" .app)"
    echo "Quitting: $appName"
    osascript -e "tell application \"$appName\" to quit" >/dev/null 2>&1 || true
  done
else
  echo "No Ableton application bundle found under /Applications"
fi

# Fallback: try to kill any remaining processes named Ableton Live
pkill -f "Ableton Live" >/dev/null 2>&1 || true

sleep 1

echo "Opening Test Set: $TEST_SET"
if [[ -n "$suite_app_name" ]]; then
  echo "Opening with: $suite_app_name"
  open -a "$suite_app_name" "$TEST_SET" || open "$TEST_SET" || echo "Could not open Test Set in Ableton."
else
  open "$TEST_SET" || echo "Could not open Test Set (no Ableton app found)."
fi

echo "Done."

exit 0
