#!/usr/bin/env bash
set -euo pipefail

# Install only .vst3 bundles from the release vendor package into a VST3 folder.
# Usage: scripts/install_vst3.sh [TARGET_DIR]

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST_DIR="$REPO_ROOT/release"
PLUGIN_FOLDER="$(basename "$REPO_ROOT")"
VENDOR="Tomas Laurenzo"

usage() {
  cat <<EOF
Usage: $(basename "$0") [TARGET_DIR]
Installs .vst3 bundles from the release vendor package into TARGET_DIR.
Defaults to ~/Library/Audio/Plug-Ins/VST3
EOF
}

TARGET_DIR="${1:-$HOME/Library/Audio/Plug-Ins/VST3}"
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

# Prefer an extracted vendor folder, fallback to the vendor zip
vendor_dir="$DIST_DIR/$VENDOR/$PLUGIN_FOLDER"
tmpdir=""
vst3_list=""

if [[ -d "$vendor_dir" ]]; then
  echo "Searching for .vst3 bundles in $vendor_dir"
  vst3_list=$(find "$vendor_dir" -maxdepth 1 -name '*.vst3' -not -name '.*' -type d -print 2>/dev/null || true)
else
  vendor_zip=$(ls -t "$DIST_DIR/${VENDOR// /_}-${PLUGIN_FOLDER}-*.zip" 2>/dev/null | head -n1 || true)
  if [[ -z "$vendor_zip" ]]; then
    echo "No vendor dir or vendor zip found for '$VENDOR' in $DIST_DIR"
    exit 1
  fi
  echo "Found vendor zip: $vendor_zip"
  tmpdir=$(mktemp -d)
  echo "Extracting vendor zip to: $tmpdir"
  unzip -q "$vendor_zip" -d "$tmpdir"
  vendor_dir="$tmpdir/$VENDOR/$PLUGIN_FOLDER"
  vst3_list=$(find "$vendor_dir" -maxdepth 1 -name '*.vst3' -not -name '.*' -type d -print 2>/dev/null || true)
fi

if [[ -z "$vst3_list" ]]; then
  echo "No .vst3 bundles found for $VENDOR/$PLUGIN_FOLDER"
  [[ -n "$tmpdir" ]] && rm -rf "$tmpdir"
  exit 0
fi

validate_vst3_bundle() {
  local bundle="$1"
  local macos_dir="$bundle/Contents/MacOS"

  if [[ ! -d "$macos_dir" ]]; then
    echo "Invalid VST3 bundle: $bundle has no Contents/MacOS directory." >&2
    return 1
  fi

  if ! find "$macos_dir" -maxdepth 1 -type f -perm -111 -print -quit | grep -q .; then
    echo "Invalid VST3 bundle: $bundle has no executable plugin binary in Contents/MacOS." >&2
    return 1
  fi
}

echo "Installing .vst3 bundles to: $TARGET_DIR_EXPANDED"
mkdir -p "$TARGET_DIR_EXPANDED"

while IFS= read -r vst3; do
  if [[ -z "$vst3" ]]; then
    continue
  fi
  validate_vst3_bundle "$vst3"
  echo "Copying: $vst3 -> $TARGET_DIR_EXPANDED/"
  rsync -a "$vst3" "$TARGET_DIR_EXPANDED/"
done <<< "$vst3_list"

echo "Installation finished."
[[ -n "$tmpdir" ]] && rm -rf "$tmpdir"

exit 0
