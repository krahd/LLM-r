#!/usr/bin/env bash
set -euo pipefail

echo "Preparing local release build..."
python -m pip install --upgrade pip
pip install build pyinstaller
pip install -e ".[gui]"

echo "Building wheel and sdist..."
python -m build --sdist --wheel

echo "Building standalone binaries with PyInstaller..."
mkdir -p release
pyinstaller --onefile --name llm-r-gui gui/pyqt_app.py --distpath release --workpath build/pyinstaller
pyinstaller --onefile --name llm-r-server backend/main.py --distpath release --workpath build/pyinstaller

echo "Done. Artifacts are in the 'dist/' and 'release/' directories."
