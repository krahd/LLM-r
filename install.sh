!/bin/bash
set -euo pipefail

# LLM-r Plugin Installer for Ableton Live on macOS

# This script is meant to be run after building the plugin with build_release.sh.

# It copies the built plugin from the release/ directory to the Ableton MIDI Remote Scripts folder on macOS. Adjust the destination path as needed for other platforms.

cp -R release/"Tomas Laurenzo" ~/Library/Audio/MIDI\ Remote\ Scripts/

echo "Plugin installed to Ableton MIDI Remote Scripts folder. Please restart Ableton Live to load the new plugin."
