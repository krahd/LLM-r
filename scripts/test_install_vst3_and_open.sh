#!/usr/bin/env bash
set -euo pipefail

# Build the local release package, include plugin bundles if any are present,
# install VST3 bundles, quit Ableton Live if running, and open the local test set.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VST3_TARGET="${1:-$HOME/Library/Audio/Plug-Ins/VST3}"
VST3_TARGET_EXPANDED="${VST3_TARGET/#\~/$HOME}"
TEST_SET="$REPO_ROOT/Test Set Project/Test Set.als"

echo "Building project and including local plugin bundles if present..."
bash "$REPO_ROOT/scripts/build_plugin.sh" --clean --all \
  --vst3-dir "$REPO_ROOT/build/vst3" \
  --au-dir "$REPO_ROOT/build/au" \
  --vst-dir "$REPO_ROOT/build/vst"

echo "Installing VST3 bundles to: $VST3_TARGET_EXPANDED"
bash "$REPO_ROOT/scripts/install_vst3.sh" "$VST3_TARGET_EXPANDED"

echo "Attempting to quit Ableton Live if it's running..."
# Try common Ableton application names
for app in "Ableton Live" "Ableton Live 12 Suite" "Ableton Live 12" "Ableton Live 11 Suite" "Ableton Live 11"; do
  osascript -e 'tell application "'"$app"'" to quit' >/dev/null 2>&1 || true
done
# Fallback: try to kill any remaining processes
pkill -f "Ableton Live" >/dev/null 2>&1 || true

sleep 1

echo "Opening Test Set: $TEST_SET"
open -a "Ableton Live" "$TEST_SET" || open "$TEST_SET" || echo "Could not open Test Set in Ableton."

echo "Done."

exit 0
