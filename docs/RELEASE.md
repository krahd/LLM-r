# Release — Build & publish binaries

This repository includes a GitHub Actions workflow that builds and publishes release artifacts (source distributions, wheels, and standalone binaries) when you push a tag matching `v*`.

How to create a release via GitHub (recommended):

1. Create a tag locally (bump the version as appropriate):

```bash
git tag v1.5.2
git push origin v1.5.2
```

2. The workflow `.github/workflows/release.yml` will run on tag push, build artifacts for multiple platforms, and create a GitHub Release attaching the built files.

Local build (for testing):

1. Activate your virtualenv and run the helper script:

```bash
./scripts/build_release.sh
```

2. After the script completes, you'll find artifacts in:

- `dist/` — sdist and wheel files
- `release/` — PyInstaller-built standalone executables (platform-specific)

Notes and caveats:

- Building the GUI binary requires `PyQt6` (optional). Install with `pip install -e .[gui]` if you want the GUI bundled.
- PyInstaller builds are platform-specific and may require additional tooling on each platform; CI builds run on `ubuntu-latest`, `macos-latest`, and `windows-latest` to produce per-platform artifacts.
- If the GitHub Actions job fails to upload an asset automatically, you can also create a release manually and upload the files from `dist/` and `release/`.
