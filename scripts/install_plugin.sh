#!/usr/bin/env bash
set -euo pipefail

# Installs the latest vendor zip produced by scripts/build_plugin.sh
# Usage: scripts/install_plugin.sh [TARGET_DIR]

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST_DIR="$REPO_ROOT/release"
PLUGIN_FOLDER="$(basename "$REPO_ROOT")"

usage() {
  cat <<EOF
Usage: $(basename "$0") [TARGET_DIR]
Installs the latest vendor zip produced by scripts/build_plugin.sh into TARGET_DIR.
Defaults to ~/Music/Ableton/User Library/Installed Packs
EOF
}

TARGET_DIR="${1:-$HOME/Music/Ableton/User Library/Installed Packs}"
if [[ "${TARGET_DIR}" == "-h" || "${TARGET_DIR}" == "--help" ]]; then
  usage
  exit 0
fi
TARGET_DIR_EXPANDED="${TARGET_DIR/#\~/$HOME}"

if [[ ! -d "$DIST_DIR" ]]; then
  echo "Release directory not found: $DIST_DIR"
  echo "Run: ./scripts/build_plugin.sh --all"
  exit 1
fi

# Find the most recent vendor zip matching the plugin name
vendor_zip=$(ls -t "$DIST_DIR"/*-"$PLUGIN_FOLDER"-*.zip 2>/dev/null | head -n1 || true)

if [[ -z "$vendor_zip" ]]; then
  echo "No vendor zip found in $DIST_DIR. Run: ./scripts/build_plugin.sh --all"
  exit 1
fi

echo "Found vendor zip: $vendor_zip"
echo "Installing to: $TARGET_DIR_EXPANDED"

mkdir -p "$TARGET_DIR_EXPANDED"

# Unzip vendor into target, preserving folder structure. Fall back to copying the zip.
if unzip -o "$vendor_zip" -d "$TARGET_DIR_EXPANDED" >/dev/null; then
  echo "Unzipped $vendor_zip -> $TARGET_DIR_EXPANDED"
else
  echo "Unzip failed; copying zip as fallback."
  cp -a "$vendor_zip" "$TARGET_DIR_EXPANDED/"
  echo "Copied $vendor_zip -> $TARGET_DIR_EXPANDED/"
fi

echo "Install complete. Restart or refresh Ableton Live if necessary."

exit 0
