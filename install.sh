#!/usr/bin/env bash
set -euo pipefail

# Convenience installer for local Ableton test installs.
# Build first with:
#   ./scripts/build_plugin.sh --all

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$SCRIPT_DIR/scripts/install_plugin.sh" "$@"
