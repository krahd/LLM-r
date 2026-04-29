#!/usr/bin/env bash
set -euo pipefail

# Build the local release package, include plugin bundles if any are present,
# install VST3 bundles, quit Ableton Live if running, and open the local test set.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VST3_TARGET="${1:-$HOME/Library/Audio/Plug-Ins/VST3}"
VST3_TARGET_EXPANDED="${VST3_TARGET/#\~/$HOME}"
TEST_SET="$REPO_ROOT/Test Set Project/Test Set.als"

echo "Building GUI and including VST3 bundles if present..."
# Build only the GUI and include any local VST3 bundles for testing
bash "$REPO_ROOT/scripts/build_plugin.sh" --clean --gui \
  --vst3-dir "$REPO_ROOT/build/vst3"
  --au-dir "$REPO_ROOT/build/au" \
  --vst-dir "$REPO_ROOT/build/vst"

echo "Installing VST3 bundles to: $VST3_TARGET_EXPANDED"
bash "$REPO_ROOT/scripts/install_vst3.sh" "$VST3_TARGET_EXPANDED"


echo "Attempting to quit Ableton Live if it's running..."
# Detect installed Ableton application bundles under /Applications and quit them
shopt -s nullglob
apps=(/Applications/Ableton\ Live*.app)
shopt -u nullglob
if [[ ${#apps[@]} -gt 0 ]]; then
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
if [[ ${#apps[@]} -gt 0 ]]; then
  # Prefer the first matched app bundle
  appPathToOpen="${apps[0]}"
  echo "Opening with: $appPathToOpen"
  open -a "$appPathToOpen" "$TEST_SET" || open "$TEST_SET" || echo "Could not open Test Set in Ableton."
else
  open "$TEST_SET" || echo "Could not open Test Set (no Ableton app found)."
fi

echo "Done."

exit 0
