# Release — Build & publish binaries

This repository includes a GitHub Actions workflow that builds and publishes release artifacts (source distributions, wheels, and standalone binaries) when you push a tag matching `v*`.

## Release artefact roles

- **Primary**: the VST3 plug-in (`LLM-r.vst3`) and the bundled `LLMRDeviceBridge` Remote Script are the main deliverables for end users.
- **Companion surfaces**: the Python FastAPI server, PyQt GUI, and web UI are companion tools for headless and development workflows. Wheels and sdist are development/integration artefacts.

## Pre-tag checklist

Run all of these before tagging a release:

```bash
# Tests
python3 -m pytest -q

# Lint
ruff check .

# Compile-check Python surfaces
PYTHONPYCACHEPREFIX=/tmp/llmr-pyc python3 -m py_compile \
  gui/pyqt_app.py backend/device_server.py llmr/device_bridge.py \
  llmr/osc_replies.py llmr/device_parameters.py \
  remote_scripts/LLMRDeviceBridge/__init__.py \
  remote_scripts/LLMRDeviceBridge/LLMRDeviceBridge.py \
  scripts/smoke_test_live_integration.py

# Build package
python3 -m build

# Whitespace check
git diff --check
```

## Pre-release UI checklist

Do not mark these complete unless you manually exercised the release candidate build or packaged app that users will receive.

- First-run flow checked
- Readiness display checked where shipped
- Plan, dry run, and execute flow checked
- Local runtime tabs checked
- VST3 UI checked
- Web UI checked

Interpret the checklist literally:

- The current shipped VST3 should be checked for its actual plan/review/execute workflow, settings, Device Bridge checks, and Ollama controls.
- The current shipped PyQt GUI and web UI should be checked for readiness display.
- The current shipped local runtime tabs are the PyQt Ollama and oMLX tabs; the VST3 does not currently ship an oMLX management tab.

## macOS validation steps

These are required before tagging but are not automated in CI:

```bash
./scripts/build_vst3.sh
bash scripts/test_install_vst3_and_open.sh "$HOME/Library/Audio/Plug-Ins/VST3"
python3 scripts/smoke_test_live_integration.py
```

## Version consistency checklist

Before tagging `vX.Y.Z`, verify the version number is consistent in all of these places:

- `pyproject.toml` — `version = "X.Y.Z"`
- `llmr/__init__.py` — `__version__ = "X.Y.Z"`
- `native/vst3/llmr_vst3_plugin.cpp` — `#define LLMR_VERSION "X.Y.Z"`
- `scripts/build_vst3.sh` — version strings in the plist
- `docs/RELEASE.md` — tag examples
- `docs/DEVELOPMENT_PLAN.md` — current package version
- `STATUS.md` — version field

## Creating a release

How to create a release via GitHub (recommended):

1. Confirm all pre-tag checklist steps pass.
2. Verify version consistency across all sources above.
3. Create a tag locally:

```bash
git tag v0.6.9
git push origin v0.6.9
```

4. The workflow `.github/workflows/release.yml` will run on tag push, build artifacts for multiple platforms, and create a GitHub Release attaching the built files.

Local build (for testing):

1. Activate your virtualenv and run the helper script:

```bash
./scripts/build_release.sh
```

2. After the script completes, you'll find artifacts in:

- `dist/` — sdist and wheel files
- `release/` — PyInstaller-built standalone executables (platform-specific, ignored by git)

Local install helpers:

- `scripts/install_plugin.sh` installs the latest vendor zip from `release/`.
- `scripts/install_vst3.sh` installs `.vst3` bundles from the vendor package
  into `~/Library/Audio/Plug-Ins/VST3` by default.
- `scripts/test_install_vst3_and_open.sh` is a local macOS helper that builds
  VST3 bundles, installs them into the user Library VST3 plug-in folder, and
  opens the ignored `Test Set Project/Test Set.als` test set. Set
  `LLMR_VST3_BUILD_CMD` to override the default `scripts/build_vst3.sh` build.
  The helper rejects placeholder `.vst3` directories that do not contain an
  executable plugin binary under `Contents/MacOS`.
- The default local VST3 smoke bundle is named `LLM-r.vst3` and reports
  `Tomas Laurenzo` as its VST3 factory vendor. It is advertised as a minimal
  VST3 instrument with a native Cocoa editor view. The editor is self-contained:
  it exposes provider/model settings, readiness chips for AbletonOSC and
  LLMRDeviceBridge status checks, Plan and Details response tabs, explicit
  Save/Cancel settings, Advanced Settings for API keys and Ollama
  status/model control, prompt entry, plan review, dry-run, auto-approve,
  destructive-action approval, and direct AbletonOSC plus Device Bridge
  execution. The shipped VST3 does not currently expose the same readiness
  strip as PyQt/web and does not currently ship an oMLX management tab.
- The primary release/install path should stay focused on the VST3 bundle plus
  the bundled LLMRDeviceBridge Remote Script. Server, web UI, and PyQt GUI
  artifacts are companion tools for advanced/headless workflows.
- The PyQt desktop GUI exposes the same plan/review/execute workflow with
  Plan, Action Table, Run Log, and Details tabs, plus the same Auto-approve
  option. Its main Settings screen is intentionally limited to provider/model
  and execution defaults; Advanced Settings owns API keys, Ollama controls,
  oMLX controls, server connection, AbletonOSC, planner guidance, and the
  most complete shipped readiness display.
- The web UI is a lightweight browser companion with readiness chips, prompt,
  plan/review/execute controls, Run Log, and Details tab. It should be checked
  separately from the VST3 because its UI surface is different.

Notes and caveats:

- Building the GUI binary requires `PyQt6` (optional). Install with `pip install -e .[gui]` if you want the GUI bundled.
- PyInstaller builds are platform-specific and may require additional tooling on each platform; CI builds run on `ubuntu-latest`, `macos-latest`, and `windows-latest` to produce per-platform artifacts.
- If the GitHub Actions job fails to upload an asset automatically, you can also create a release manually and upload the files from `dist/` and `release/`.

## Troubleshooting: "This VST3 plug-in could not be opened" in Ableton Live

If Ableton shows `LLM-r: This VST3 plug-in could not be opened`, verify these items:

1. **Install path and bundle shape**
   - Install to the user VST3 folder: `~/Library/Audio/Plug-Ins/VST3`.
   - The bundle must contain an executable at `LLM-r.vst3/Contents/MacOS/LLM-r`.
   - Use `scripts/install_vst3.sh` or `scripts/test_install_vst3_and_open.sh` to avoid copying an incomplete placeholder bundle.

2. **Remove duplicate old copies**
   - Keep only one `LLM-r.vst3` (user folder recommended).
   - Remove stale copies from `/Library/Audio/Plug-Ins/VST3` and re-scan plug-ins in Live.

3. **Clear macOS quarantine on downloaded bundles**
   - If the bundle came from a zip download, clear quarantine:

   ```bash
   xattr -dr com.apple.quarantine ~/Library/Audio/Plug-Ins/VST3/LLM-r.vst3
   ```

4. **Check architecture and minimum OS**
   - Local builds are universal on Apple Silicon (`arm64` + `x86_64`) and use `-mmacosx-version-min=11.0`.
   - On Intel Macs older than macOS 11, this test bundle will fail to load.

5. **Restart Live after reinstall**
   - Quit Live completely, reinstall the bundle, then reopen Live and run plug-in rescan.

Quick validation commands:

```bash
file ~/Library/Audio/Plug-Ins/VST3/LLM-r.vst3/Contents/MacOS/LLM-r
codesign -dv --verbose=4 ~/Library/Audio/Plug-Ins/VST3/LLM-r.vst3
spctl -a -vv ~/Library/Audio/Plug-Ins/VST3/LLM-r.vst3
```

Update GitHub "About" box programmatically (optional):

If you have the GitHub CLI (`gh`) installed and authenticated, you can update the repository description and topics from the command line. Example:

```bash
# set a short description
gh repo edit --description "LLM-r is an Ableton Live LLM bridge"

# add recommended topics (run multiple times or use multiple --add-topic flags)
gh repo edit --add-topic llm --add-topic ableton --add-topic modelito --add-topic osc --add-topic music --add-topic automation --add-topic plugin
```

If `gh` is not available, update the About box in the repository web UI (top-right 'About' edit button on the repo page).
