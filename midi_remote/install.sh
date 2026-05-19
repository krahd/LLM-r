#!/usr/bin/env bash
set -euo pipefail

# Simple installer for the LLMRRemote package. Use LIVE_REMOTE_PATH to override
# the target directory. Default is a no-op reminder — set LIVE_REMOTE_PATH.

TARGET=${1:-}
if [[ "$TARGET" == "" ]]; then
  if [[ -n "${LIVE_REMOTE_PATH:-}" ]]; then
    TARGET="$LIVE_REMOTE_PATH"
  else
    echo "Usage: $0 --target /path/to/MIDI\ Remote\ Scripts or set LIVE_REMOTE_PATH"
    exit 1
  fi
fi

SRC_DIR=$(dirname "$0")/LLMRRemote

if [[ ! -d "$SRC_DIR" ]]; then
  echo "Cannot find $SRC_DIR"
  exit 2
fi

echo "Installing LLMRRemote -> $TARGET"
mkdir -p "$TARGET"
rsync -a --delete "$SRC_DIR" "$TARGET/"
echo "Installed. Restart Ableton Live to pick up the remote script."
