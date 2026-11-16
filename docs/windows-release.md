# Windows Continuous Delivery

The Windows CD workflow is defined in `.github/workflows/cd.yml`.

## Automatic release

1. A change is pushed or merged into `main`.
2. The existing `CI/CD` workflow runs.
3. Only when that workflow completes successfully for a push to `main`, the CD workflow starts.
4. GitHub Actions builds a portable Windows x64 application with PyInstaller.
5. The build bundles the MediaPipe hand-landmarker model.
6. The workflow creates a GitHub Release containing:
   - `SonicAssistant-Windows-x64.zip`
   - `SonicAssistant-Windows-x64.sha256`

The automatic release tag uses the form `v1.0.N`, where `N` is the CD workflow run number.

## Manual release

The workflow can also be started from **Actions → CD - Windows Release → Run workflow**. An optional release tag can be supplied, for example `v1.0.5`. If left blank, the workflow generates a tag automatically.

## Running a release

1. Download `SonicAssistant-Windows-x64.zip) from the GitHub Release.
2. Extract the complete `SonicAssistant` folder.
3. Keep `SonicAssistant.exe` and the `_internal` folder together.
4. Run `SonicAssistant.exe`.
5. Grant microphone and camera permissions when prompted.

This is a portable Windows x64 build, not a signed installer. Microphone, webcam, speaker, and media-player behavior still depends on the target PC and its permissions. Voice recognition requires an internet connection.

## Permissions

The workflow requests only `contents: write` so it can create a GitHub Release and attach the packaged files. It runs automatically only after a successful push-triggered CI run on `main`.
