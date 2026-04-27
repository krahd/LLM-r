#!/usr/bin/env bash
set -euo pipefail

# Build helper for local plugin releases.
# Usage: scripts/build_plugin.sh [--gui] [--server] [--all] [--clean] [--version X.Y.Z]

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON=${PYTHON:-python3}
DIST_DIR="$REPO_ROOT/release"
BUILD_DIR="$REPO_ROOT/build/pyinstaller"
SPEC_GUI="$REPO_ROOT/llm-r-gui.spec"
SPEC_SERVER="$REPO_ROOT/llm-r-server.spec"
GUI_SCRIPT="$REPO_ROOT/gui/pyqt_app.py"
SERVER_SCRIPT="$REPO_ROOT/backend/main.py"

usage() {
  cat <<EOF
Usage: $(basename "$0") [--gui] [--server] [--all] [--clean] [--version X.Y.Z]
Builds local plugin binaries and packages them into release/ as zip files.
Options:
  --gui       build GUI binary
  --server    build server binary
  --all       build both (default)
  --clean     clean previous build artifacts before building
  --vendor    set vendor name (default: Tomas Laurenzo)
  --version   set explicit version (overrides pyproject.toml)
  -h, --help  show this help
EOF
}

# defaults
BUILD_GUI=0
BUILD_SERVER=0
CLEAN=0
VENDOR="Tomas Laurenzo"

PLUGIN_FOLDER="$(basename "$REPO_ROOT")"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --gui) BUILD_GUI=1; shift ;;
    --server) BUILD_SERVER=1; shift ;;
    --all) BUILD_GUI=1; BUILD_SERVER=1; shift ;;
    --clean) CLEAN=1; shift ;;
    --vendor) VENDOR="$2"; shift 2 ;;
    --version) VERSION="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 1 ;;
  esac
done

if [[ $BUILD_GUI -eq 0 && $BUILD_SERVER -eq 0 ]]; then
  BUILD_GUI=1
  BUILD_SERVER=1
fi

if [[ $CLEAN -eq 1 ]]; then
  echo "Cleaning $DIST_DIR and $BUILD_DIR and build/ and dist/"
  rm -rf "$DIST_DIR" "$BUILD_DIR" "$REPO_ROOT/build" "$REPO_ROOT/dist"
fi

mkdir -p "$DIST_DIR"
mkdir -p "$BUILD_DIR"

echo "Using python: $PYTHON"
"$PYTHON" -m pip install --upgrade pip
"$PYTHON" -m pip install --upgrade build pyinstaller || true

if [[ $BUILD_GUI -eq 1 ]]; then
  echo "Installing GUI extras..."
  "$PYTHON" -m pip install --upgrade "PyQt6" || true
fi

echo "Building sdist/wheel (best-effort)..."
"$PYTHON" -m build --sdist --wheel || true

if [[ -z "${VERSION:-}" ]]; then
  VERSION="$($PYTHON - <<PY
import tomllib, os
p=os.path.join("$REPO_ROOT","pyproject.toml")
with open(p,'rb') as f:
    data=tomllib.load(f)
print(data['project'].get('version','0.0.0'))
PY
)"
fi

echo "Building version: $VERSION"

run_pyinstaller() {
  local name="$1"
  local spec="$2"
  local script="$3"
  echo "Building $name..."
  if [[ -f "$spec" ]]; then
    pyinstaller --clean --noconfirm --distpath "$DIST_DIR" --workpath "$BUILD_DIR" "$spec"
  else
    pyinstaller --clean --noconfirm --distpath "$DIST_DIR" --workpath "$BUILD_DIR" --onefile --name "$name" "$script"
  fi
}

package() {
  local name="$1"
  local out="$DIST_DIR/${name}-${VERSION}.zip"
  echo "Packaging $name -> $out"
  pushd "$DIST_DIR" >/dev/null
  shopt -s nullglob 2>/dev/null || true
  files=( "$name" "$name"* )
  if [[ ${#files[@]} -eq 0 ]]; then
    echo "No artifacts found for $name in $DIST_DIR, skipping packaging."
    popd >/dev/null
    return
  fi
  zip -r "$out" "${files[@]}"

  # Create vendor install folder (e.g. release/Tomas Laurenzo/LLM-r/) and copy artifacts
  vendor_dir="$DIST_DIR/$VENDOR/$PLUGIN_FOLDER"
  mkdir -p "$vendor_dir"
  for f in "${files[@]}"; do
    if [[ -e "$f" ]]; then
      cp -a "$f" "$vendor_dir/"
    fi
  done

  # Create a vendor-level zip for easy install into Ableton (underscores for spaces)
  vendor_zip="${VENDOR// /_}-${PLUGIN_FOLDER}-${VERSION}.zip"
  (cd "$DIST_DIR" && zip -r "$vendor_zip" "$VENDOR" >/dev/null || true)

  popd >/dev/null
}

if [[ $BUILD_GUI -eq 1 ]]; then
  run_pyinstaller "llm-r-gui" "$SPEC_GUI" "$GUI_SCRIPT"
  package "llm-r-gui"
fi

if [[ $BUILD_SERVER -eq 1 ]]; then
  run_pyinstaller "llm-r-server" "$SPEC_SERVER" "$SERVER_SCRIPT"
  package "llm-r-server"
fi

echo "Done. Artifacts:"
ls -1 "$DIST_DIR" || true
