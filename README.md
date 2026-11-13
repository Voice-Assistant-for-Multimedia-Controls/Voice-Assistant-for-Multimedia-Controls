# Voice Assistant for Multimedia Controls — Team Starter

[![CI/CD](https://github.com/Voice-Assistant-for-Multimedia-Controls/Voice-Assistant-for-Multimedia-Controls/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Voice-Assistant-for-Multimedia-Controls/Voice-Assistant-for-Multimedia-Controls/actions/workflows/ci.yml)

This repository contains the shared **starter scaffold** only. It intentionally
does not implement the project features. Team members should complete their
assigned TODOs in separate branches and raise pull requests for review.

## Structure

```text
Voice-Assistant-for-Multimedia-Controls/
├── main.py
├── requirements.txt
└── src/
    ├── __init__.py
    ├── voice_input.py
    ├── command_handler.py
    ├── multimedia_controller.py
    ├── feedback_service.py
    ├── volume_control.py
    ├── track_navigation.py
    ├── gesture_control.py
    └── gesture_mapping.py
```

## Suggested task ownership

- **Prajwal GT:** voice input, predefined voice-command detection/routing,
  play/resume, pause, and safe handling of unsupported commands.
- **Shreedhar R:** software volume up/down using the computer's media keys.
- **Shrinivas S J:** next/previous track and command feedback.
- **Sarang S Nair:** MediaPipe gesture recognition and gesture mapping.

Confirm task scope and filenames with the team before implementation. These
ownership notes follow the team's current SRS assignment summary; adjust only
if the team agrees to a documented change.

## Workflow

1. Pull the latest shared branch.
2. Create a branch for your own assigned task.
3. Implement only your assigned TODOs.
4. Run the tests you add for your feature.
5. Commit your changes and open a PR.
6. Ask the repository owner/team member to review before merging.
7. Test the integrated project after PRs are merged.

## Important

- The voice-command loop and basic media controls are implemented. Other
  features may still be incomplete; check for methods marked `TODO`.
- Follow the submitted SRS, SAD, and Test Plan.
- Record deviations from those documents and explain them in the final demo.
- Add only the dependencies actually selected and used by the team.

## Shreedhar R — volume control and CI/CD pipeline

Implemented the assigned volume-up and volume-down commands as host-computer
media-key actions using PyAutoGUI. The existing command handler routes spoken
volume commands to the multimedia controller, which delegates to the volume
control module. This replaces the proposed external-device communication
approach with direct software control: no ESP32, Raspberry Pi, serial port, or
other external controller is required.

Added automated tests for both key mappings and repeated commands. The
assistant was also tested with a live microphone: it recognized "volume up"
and "volume down" and dispatched the corresponding media keys. The tests do
not independently verify the Windows volume indicator or audible output.

Shreedhar also implemented the project CI/CD workflow in
`.github/workflows/ci.yml`, covering code checks, unit tests, smoke tests, and
coverage reporting for the main branch. The repository also includes the
hardware-validation workflow in `.github/workflows/hardware-validation.yml`
for device-dependent validation on a self-hosted Windows runner when the
camera, microphone, and speakers are available.

## Software-only communication and continuous-operation checks

The multimedia controller sends host-computer media-key events for play,
resume, pause, next track, previous track, and volume changes. No external
controller or other additional hardware is used for these media actions.
`test_software_operations.py` replaces PyAutoGUI with a mock and supplies
commands through a fake voice-input source, so it verifies key mapping,
repeated commands, and continued listening after an empty recognition result
without using a microphone or sending real key events.

Run the software-only checks with:

```powershell
python -m unittest discover -v
```

These automated checks confirm that the application requests the expected
host media-key events. They do not prove that a particular media player,
Windows volume setting, speaker, or physical audio device responds to them.

Install the project's listed dependencies and run the assistant:

```powershell
python -m pip install -r requirements.txt
python main.py
```

## CI/CD Pipeline and Known Limitations

GitHub Actions runs the project's unit tests automatically to catch regressions
before changes are merged. The workflow is defined in
`.github/workflows/ci.yml` and runs on pushes to `main` and pull requests
targeting `main`. It uses a GitHub-hosted Windows runner with Python 3.11,
installs dependencies from `requirements.txt`, and executes
`python -m unittest discover -v`. A failed test causes the workflow check to
fail on the pull request.

The automated tests use mocks instead of physical devices: microphone input
and webcam capture are mocked in `tests/test_hardware_free_operations.py`,
speech output is mocked in `tests/test_feedback_service.py`, and media-key
presses and desktop-window lookup are mocked in
`tests/test_software_operations.py`. The tests verify application behavior
against those simulated interfaces without opening a microphone, camera, or
speaker or sending real media-key actions.

Manual testing on a real Windows computer is still needed to verify microphone
and online speech-recognition behavior, webcam permissions and gesture
recognition, audible text-to-speech output, and whether the active media player
responds correctly to keyboard shortcuts and system media keys. CI cannot
confirm physical-device availability, audio quality, camera image quality,
media-player behavior, or hardware-specific driver issues.

## Shreedhar R — CI/CD pipeline (US-16)

Added the GitHub Actions CI workflow in `.github/workflows/ci.yml`. It runs on
pushes to `main` and pull requests targeting `main`, checks Python syntax and
critical lint errors, runs the full unittest suite, runs smoke tests, and
uploads a coverage report. The README also includes a badge linking to the
workflow.

Added hardware-free tests that mock microphone input and webcam capture, and
updated software-operation tests to mock media-key and window interactions.
The tests can run in CI without a microphone, webcam, speakers, or real key
presses. Documented which device-dependent behaviors still need manual
verification. A separate, manually dispatched/scheduled hardware-validation
workflow requires a configured self-hosted Windows runner with devices
attached; it is not part of the standard pull-request checks.

This work complements the separate volume-control contribution above, which
implements the host-level volume up/down media-key actions and the related
gesture and voice integration covered in US-11.

## Shrinivas S J — track navigation and feedback

Implemented next/previous track navigation routed through the shared
multimedia controller, with logging for failures. Added a feedback
service that prints and speaks command results, with configurable
voice rate and volume and a success/failure `report()` helper.

Added unit tests for both modules in `tests/`. The tests mock the
controller and the text-to-speech engine, so they run without audio
or a microphone.

`FeedbackService.track_changed(direction, success)` speaks the result of a next/previous track request.

## Prajwal GT — Voice Input and Command Handling

Implemented the voice-input and predefined voice-command handling functionality for the Voice Assistant for Multimedia Controls project.

Integrated speech recognition to capture spoken commands through the microphone and convert them into text for processing. Implemented predefined command mappings in `src/command_handler.py` to identify recognized phrases and route them to the appropriate multimedia controller actions.

Added command normalization to handle capitalization, leading and trailing spaces, and repeated spaces.

Implemented support for play, resume, pause, stop music, next track, previous track, volume up, and volume down commands through the shared command handler.

Added safe handling for empty input, unsupported commands, and unavailable controller actions. Unsupported phrases generate feedback without executing an invalid action.

The main files involved in the voice-command functionality are:

- `src/voice_input.py` — Microphone input and speech recognition.
- `src/command_handler.py` — Command normalization, recognition, and routing.
- `src/multimedia_controller.py` — Playback-control integration.
- `main.py` — Voice-assistant initialization and continuous listening.

Live microphone testing confirmed recognition of the "play music" command and dispatch to the multimedia controller. Actual playback behavior in YouTube and Firefox requires further verification.

## Supported voice commands

| Action | Phrases |
|---|---|
| Play | play, play music, play the music |
| Resume | resume, resume music |
| Pause | pause, pause music, stop, stop music |
| Next track | next, next track, next song, play next, play next song |
| Previous track | previous, previous track, previous song, play previous, play previous song |
| Volume | volume up, volume down |

Commands must be spoken as the complete phrase. Anything else is
reported as unsupported and no action is taken.