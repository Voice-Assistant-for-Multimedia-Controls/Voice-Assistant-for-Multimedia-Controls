# Sprint 1 Plan — Voice Assistant for Multimedia Controls

**Team:** Group 12  
**Focus:** Core voice-command flow and software multimedia controls.

> Before submission, update task statuses to match the GitHub Project board and verified test results.

## Sprint goal
Deliver the core voice assistant that recognizes supported commands, routes them to multimedia actions, provides feedback, and includes basic automated tests.

## Team task allocation

### Prajwal GT — Voice input and command handling
- Implement microphone input and speech-to-text handling.
- Define and route supported voice commands.
- Support play/resume and pause commands.
- Handle empty, unclear, and unsupported commands safely.
- Add unit tests for command routing and unsupported input.

**Acceptance criteria**
- Supported phrases route to the intended controller action.
- Empty or unsupported input does not trigger a media action.
- Voice-input errors are handled without crashing the command loop.

### Shreedhar R — Software volume control
- Implement volume-up and volume-down using host-computer media keys.
- Connect volume commands through the command handler and multimedia controller.
- Add tests for key mappings and repeated volume commands.
- Document that the implementation uses software media-key events and requires no external controller hardware.

**Acceptance criteria**
- Volume commands dispatch the correct media-key actions.
- Automated tests can verify key mappings without changing the real system volume.
- Limitations in verifying the Windows volume indicator or audible output are documented.

### Shrinivas S J — Track navigation and command feedback
- Implement next-track and previous-track navigation through the shared controller.
- Provide feedback for processed commands.
- Handle invalid feedback messages safely.
- Add tests for successful navigation requests and controller errors.

**Acceptance criteria**
- Next/previous requests call the corresponding controller method.
- Navigation reports success or failure consistently.
- Feedback is clear; if speech output is enabled, terminal feedback still works when speech initialization fails.

### Sarang S Nair — Gesture recognition foundation
- Implement webcam-based gesture recognition.
- Define supported gesture labels and map them to command names.
- Avoid triggering actions for unknown or uncertain gestures.
- Add tests for gesture-to-command mapping.

**Acceptance criteria**
- Supported gestures map only to intended commands.
- Unknown or empty gestures do not trigger actions.
- Camera/model initialization failures are reported safely.

## Integration and testing — all team members
- Confirm module interfaces and command names.
- Run `python -m unittest discover -v`.
- Test voice-command routing and software media-key behavior.
- Record known limitations and update the GitHub Project board.
- Review team members' changes before merging.

## Sprint 1 deliverables
- Python modules for voice input, command handling, multimedia control, feedback, volume, navigation, and gesture recognition/mapping.
- Automated tests for implemented modules.
- Setup and test instructions in the README or test notes.

## Definition of done
- Code is committed to the correct branch.
- Relevant tests pass, or failures are documented.
- Tasks are not marked complete without code or test evidence.
- Changes are reviewed and integrated through the agreed team workflow.
