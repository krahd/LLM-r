# Release — Build & publish binaries

This repository includes a GitHub Actions workflow that builds and publishes release artifacts (source distributions, wheels, and standalone binaries) when you push a tag matching `v*`.

How to create a release via GitHub (recommended):

1. Create a tag locally after confirming `pyproject.toml` and `llmr/__init__.py`
   contain the intended version:

```bash
git tag v0.5.4
git push origin v0.5.4
```

2. The workflow `.github/workflows/release.yml` will run on tag push, build artifacts for multiple platforms, and create a GitHub Release attaching the built files.

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
  `Tomas Laurenzo` as its VST3 factory vendor.

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
