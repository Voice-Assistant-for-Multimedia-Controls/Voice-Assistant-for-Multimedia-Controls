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

Install the project's listed dependencies and run the assistant:

```powershell
python -m pip install -r requirements.txt
python main.py
```
