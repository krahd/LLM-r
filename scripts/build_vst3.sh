#!/usr/bin/env bash
set -euo pipefail

# Build the local macOS VST3 bundle used by the install/open smoke task.
# This currently builds a minimal native VST3 bundle binary so the task installs
# an actual bundle executable, not a placeholder directory.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${1:-$REPO_ROOT/build/vst3}"
SRC="$REPO_ROOT/native/vst3/llmr_vst3_stub.c"
BUNDLE_NAME="${LLMR_VST3_BUNDLE_NAME:-LLM-r.vst3}"
BUNDLE_DIR="$OUT_DIR/$BUNDLE_NAME"
EXECUTABLE_NAME="${BUNDLE_NAME%.vst3}"
MACOS_DIR="$BUNDLE_DIR/Contents/MacOS"
RESOURCES_DIR="$BUNDLE_DIR/Contents/Resources"
INFO_PLIST="$BUNDLE_DIR/Contents/Info.plist"
PKG_INFO="$BUNDLE_DIR/Contents/PkgInfo"
BINARY="$MACOS_DIR/$EXECUTABLE_NAME"

usage() {
  cat <<EOF
Usage: $(basename "$0") [OUT_DIR]
Builds $BUNDLE_NAME into OUT_DIR.
Defaults to build/vst3.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "VST3 bundle build is currently supported on macOS only." >&2
  exit 1
fi

if ! command -v clang >/dev/null 2>&1; then
  echo "clang is required to build the VST3 bundle." >&2
  exit 1
fi

rm -rf "$BUNDLE_DIR"
mkdir -p "$MACOS_DIR" "$RESOURCES_DIR"

cat > "$INFO_PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>$EXECUTABLE_NAME</string>
  <key>CFBundleIdentifier</key>
  <string>net.tomaslaurenzo.llm-r.vst3</string>
  <key>CFBundleName</key>
  <string>LLM-r</string>
  <key>CFBundlePackageType</key>
  <string>BNDL</string>
  <key>CFBundleShortVersionString</key>
  <string>0.5.4</string>
  <key>CFBundleVersion</key>
  <string>0.5.4</string>
</dict>
</plist>
PLIST

printf "BNDL????" > "$PKG_INFO"

clang -dynamiclib \
  -fvisibility=hidden \
  -arch "$(uname -m)" \
  -mmacosx-version-min=11.0 \
  "$SRC" \
  -o "$BINARY"

chmod +x "$BINARY"

if command -v codesign >/dev/null 2>&1; then
  codesign --force --sign - "$BUNDLE_DIR" >/dev/null 2>&1 || true
fi

echo "Built VST3 bundle: $BUNDLE_DIR"
