#!/usr/bin/env bash
set -euo pipefail

# Build helper for local plugin releases.
# Usage: scripts/build_plugin.sh [--gui] [--server] [--all] [--clean] [--version X.Y.Z]
#                               [--vendor NAME] [--vst3-dir PATH] [--au-dir PATH] [--vst-dir PATH]

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
Usage: $(basename "$0") [--gui] [--server] [--all] [--clean] [--version X.Y.Z] [--vendor NAME] [--vst3-dir PATH] [--au-dir PATH] [--vst-dir PATH]
Builds local plugin binaries and packages them into release/ as zip files.
Options:
  --gui       build GUI binary
  --server    build server binary
  --all       build both (default)
  --clean     clean previous build artifacts before building
  --vendor    set vendor name (default: Tomas Laurenzo)
    --vst3-dir  include .vst3 bundles from this directory (default: build/vst3)
    --au-dir    include AudioUnit (.component) bundles from this directory (default: build/au)
    --vst-dir   include VST (.vst) bundles from this directory (default: build/vst)
  --version   set explicit version (overrides pyproject.toml)
  -h, --help  show this help
EOF
}

# defaults
BUILD_GUI=0
BUILD_SERVER=0
CLEAN=0
VENDOR="Tomas Laurenzo"
VST3_DIR="$REPO_ROOT/build/vst3"
AU_DIR="$REPO_ROOT/build/au"
VST_DIR="$REPO_ROOT/build/vst"

PLUGIN_FOLDER="$(basename "$REPO_ROOT")"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --gui) BUILD_GUI=1; shift ;;
    --server) BUILD_SERVER=1; shift ;;
    --all) BUILD_GUI=1; BUILD_SERVER=1; shift ;;
    --clean) CLEAN=1; shift ;;
    --vendor) VENDOR="$2"; shift 2 ;;
    --vst3-dir) VST3_DIR="$2"; shift 2 ;;
      --au-dir) AU_DIR="$2"; shift 2 ;;
      --vst-dir) VST_DIR="$2"; shift 2 ;;
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
"$PYTHON" -m pip install --upgrade build pyinstaller
"$PYTHON" -m pip install -e .

if [[ $BUILD_GUI -eq 1 ]]; then
  echo "Installing GUI extras..."
  "$PYTHON" -m pip install -e ".[gui]"
fi

echo "Building sdist/wheel..."
"$PYTHON" -m build --sdist --wheel

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

  files=()
  for candidate in *"$name"*; do
    if [[ -f "$candidate" && "$candidate" != *.zip ]]; then
      files+=( "$candidate" )
    fi
  done

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
  (cd "$DIST_DIR" && zip -r "$vendor_zip" "$VENDOR" >/dev/null)

  popd >/dev/null
}

# After packaging, include any .vst3 bundles found in VST3_DIR into the vendor folder
copy_vst3_bundles() {
  local vst3_src
  vst3_src="${VST3_DIR/#\~/$HOME}"
  if [[ -d "$vst3_src" ]]; then
    echo "Including .vst3 bundles from: $vst3_src"
    vendor_dir="$DIST_DIR/$VENDOR/$PLUGIN_FOLDER"
    mkdir -p "$vendor_dir"
    while IFS= read -r -d '' vst3; do
      echo "Copying $vst3 -> $vendor_dir/"
      cp -a "$vst3" "$vendor_dir/"
    done < <(find "$vst3_src" -maxdepth 1 -name '*.vst3' -not -name '.*' -type d -print0 2>/dev/null || true)

    # Recreate vendor zip to include vst3 bundles
    vendor_zip="${VENDOR// /_}-${PLUGIN_FOLDER}-${VERSION}.zip"
    (cd "$DIST_DIR" && zip -r "$vendor_zip" "$VENDOR" >/dev/null)
  else
    echo "No VST3 source dir found at: $vst3_src"
  fi
}

if [[ $BUILD_GUI -eq 1 ]]; then
  run_pyinstaller "llm-r-gui" "$SPEC_GUI" "$GUI_SCRIPT"
  package "llm-r-gui"
fi

if [[ $BUILD_SERVER -eq 1 ]]; then
  run_pyinstaller "llm-r-server" "$SPEC_SERVER" "$SERVER_SCRIPT"
  package "llm-r-server"
fi

copy_vst3_bundles

copy_au_bundles() {
  local au_src
  au_src="${AU_DIR/#\~/$HOME}"
  if [[ -d "$au_src" ]]; then
    echo "Including .component (AU) bundles from: $au_src"
    vendor_dir="$DIST_DIR/$VENDOR/$PLUGIN_FOLDER"
    mkdir -p "$vendor_dir"
    while IFS= read -r -d '' au; do
      echo "Copying $au -> $vendor_dir/"
      cp -a "$au" "$vendor_dir/"
    done < <(find "$au_src" -maxdepth 1 -name '*.component' -not -name '.*' -type d -print0 2>/dev/null || true)

    vendor_zip="${VENDOR// /_}-${PLUGIN_FOLDER}-${VERSION}.zip"
    (cd "$DIST_DIR" && zip -r "$vendor_zip" "$VENDOR" >/dev/null)
  else
    echo "No AU source dir found at: $au_src"
  fi
}

copy_vst_bundles() {
  local vst_src
  vst_src="${VST_DIR/#\~/$HOME}"
  if [[ -d "$vst_src" ]]; then
    echo "Including .vst bundles from: $vst_src"
    vendor_dir="$DIST_DIR/$VENDOR/$PLUGIN_FOLDER"
    mkdir -p "$vendor_dir"
    while IFS= read -r -d '' vst; do
      echo "Copying $vst -> $vendor_dir/"
      cp -a "$vst" "$vendor_dir/"
    done < <(find "$vst_src" -maxdepth 1 -name '*.vst' -not -name '.*' -type d -print0 2>/dev/null || true)

    vendor_zip="${VENDOR// /_}-${PLUGIN_FOLDER}-${VERSION}.zip"
    (cd "$DIST_DIR" && zip -r "$vendor_zip" "$VENDOR" >/dev/null)
  else
    echo "No VST source dir found at: $vst_src"
  fi
}

copy_au_bundles
copy_vst_bundles

echo "Done. Artifacts:"
ls -1 "$DIST_DIR" || true
