#!/usr/bin/env bash
set -euo pipefail

echo "Preparing local release build..."
python -m pip install --upgrade pip
pip install build pyinstaller

echo "Building wheel and sdist..."
python -m build --sdist --wheel

echo "Building standalone binaries with PyInstaller (may be platform-specific)..."
mkdir -p release
pyinstaller --onefile --name llm-r-gui gui/pyqt_app.py --distpath release --workpath build/pyinstaller || true
pyinstaller --onefile --name llm-r-server backend/main.py --distpath release --workpath build/pyinstaller || true

echo "Done. Artifacts are in the 'dist/' and 'release/' directories."
