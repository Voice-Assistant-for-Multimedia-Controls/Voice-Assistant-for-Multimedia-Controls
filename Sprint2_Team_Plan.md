# Sprint 2 Plan — Integration, Reliability, and Validation

**Team:** Group 12  
**Focus:** Integrate voice and gesture controls, improve reliability, and validate end-to-end behavior.

> Before submission, update task statuses to match the GitHub Project board and actual test evidence.

## Sprint goal
Integrate the team modules into a reliable voice-and-gesture multimedia assistant, test cross-module behavior, and document limitations and demo steps.

## Team task allocation

### Prajwal GT — Voice-flow reliability
- Improve handling of microphone failures, empty recognition results, and unclear speech.
- Verify supported commands after integration.
- Ensure the assistant exits cleanly on the agreed exit command.
- Add regression tests for command-loop behavior and unsupported commands.

**Acceptance criteria**
- Empty or unclear speech does not trigger unintended media actions.
- Supported commands continue to work after integration.
- Exit and error paths behave as expected.

### Shreedhar R — Volume-control integration
- Verify volume commands through voice input and agreed gesture mappings.
- Test repeated volume commands and controller delegation.
- Keep media-key actions mockable for automated tests.
- Document the difference between dispatching a media key and verifying the operating system's actual volume change.

**Acceptance criteria**
- Voice/gesture volume commands route to the volume module consistently.
- Automated tests do not need to send real media-key events.
- Manual results and known limitations are recorded.

### Shrinivas S J — Track navigation and feedback integration
- Verify next/previous commands from voice input and agreed gesture mappings.
- Ensure feedback communicates recognized commands and relevant errors.
- Test feedback when speech output is unavailable, if text-to-speech is enabled.
- Add or update integration tests for navigation and feedback.

**Acceptance criteria**
- Next/previous commands invoke the correct controller operations.
- Terminal feedback remains available if speech output fails.
- Controller errors do not crash the whole assistant.

### Sarang S Nair — Gesture stability and camera lifecycle
- Integrate gesture recognition with the shared command handler.
- Validate stable gesture detection and prevent repeated commands from a held pose.
- Improve camera/model initialization and cleanup.
- Test supported gestures, unknown gestures, and camera-unavailable behavior.

**Acceptance criteria**
- Stable supported gestures map to the intended command.
- Uncertain or unknown gestures do not trigger media actions.
- Camera and MediaPipe resources are released when gesture control stops.

## Integration and system testing — all team members
- Test voice and gesture controls together.
- Check play/resume, pause, next track, previous track, volume up, and volume down where implemented.
- Run `python -m unittest discover -v`.
- Perform manual microphone and webcam checks on the target Windows environment.
- Test exit behavior, missing-device behavior, and repeated commands.
- Update test results, setup instructions, and the project board.
- Prepare a demo flow and record deviations from the SRS, design specification, or test plan.

## Sprint 2 deliverables
- Integrated voice-and-gesture application.
- Regression and integration tests for team-owned features.
- Updated setup instructions and test results.
- Demo checklist and documented limitations.

## Definition of done
- Team-owned changes are reviewed and merged using the agreed workflow.
- Automated tests pass, or failures have documented follow-up actions.
- Manual checks are recorded separately from mocked tests.
- The final demo accurately describes implemented features and remaining work.
