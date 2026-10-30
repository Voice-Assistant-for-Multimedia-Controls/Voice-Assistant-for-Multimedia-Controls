# Voice Assistant for Multimedia Controls — Team Starter

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

## Shreedhar R — completed volume-control contribution

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