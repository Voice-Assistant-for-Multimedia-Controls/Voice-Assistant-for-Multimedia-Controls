# Windows Continuous Delivery

The Windows CD workflow is defined in `.github/workflows/cd.yml`.

## Pull request package validation

For every pull request targeting `main`, GitHub Actions builds the portable Windows x64 application and uploads the ZIP package and SHA-256 checksum as a temporary workflow artifact. This is a preview for validation; it does not publish a public GitHub Release.

## Automatic release

1. A change is merged or pushed into `main`.
2. The existing `CI/CD` workflow runs.
3. Only when that workflow succeeds for a push to `main`, the CD workflow starts.
4. GitHub Actions builds a portable Windows x64 application with PyInstaller.
5. The build bundles the MediaPipe hand-landmarker model.
6. The workflow creates a GitHub Release containing:
   - `SonicAssistant-Windows-x64.zip`
   - `SonicAssistant-Windows-x64.sha256`

The automatic release tag uses the form `v1.0.N`, where `N` is the CD workflow run number.

## Manual release

The workflow can also be started from **Actions → CD - Windows Release → Run workflow**, on the `main` branch. An optional release tag can be supplied, for example `v1.0.5`. If left blank, the workflow generates a tag automatically. A manual run also performs syntax, lint, unit, and smoke checks before packaging.

## Running a release

1. Download `SonicAssistant-Windows-x64.zip` from the GitHub Release.
2. Extract the complete `SonicAssistant` folder.
3. Keep `SonicAssistant.exe` and the `_internal` folder together.
4. Run `SonicAssistant.exe`.
5. Grant microphone and camera permissions when prompted.

This is a portable Windows x64 build, not a signed installer. Microphone, webcam, speaker, and media-player behavior still depends on the target PC and its permissions. Voice recognition requires an internet connection.

## Permissions

The build job has read-only repository access. The separate release-publishing job requests `contents: write` only so it can create a GitHub Release and attach the packaged files.
