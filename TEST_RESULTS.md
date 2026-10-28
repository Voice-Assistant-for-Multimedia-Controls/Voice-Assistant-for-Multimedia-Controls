
# Voice Assistant — Sprint 1 Test Results

## US-01: Recognize Predefined Voice Commands

### Test 1: Voice input
- Action: Spoke a command into the laptop microphone.
- Expected: Speech is captured and converted to text.
- Result: Passed during manual testing.

### Test 2: Supported command routing
- Action: Ran `test_command_handler.py` with the command `play the music`.
- Expected: The play action is called by the test controller.
- Result: Passed.

### Test 3: Unsupported command
- Action: Tested the command `hello`.
- Expected: The command is rejected without triggering a media action.
- Result: Passed in the command-handler unit test.

### Test 4: Empty command
- Action: Tested an empty command.
- Expected: The handler reports an unclear command without triggering a media action.
- Result: Passed in the command-handler unit test.

### Notes
- Occasional unclear speech was observed during manual microphone testing.
- The command-handler tests use a fake controller. Actual media playback must be verified separately.

## US-04 / US-09: Software Volume Control

### Automated checks
- Action: Ran `python -m unittest discover -v`.
- Expected: Volume up/down issue the matching host media key, repeated
  commands remain independent, and the multimedia controller routes both
  operations through the software volume control.
- Result: Passed using a mocked media-key interface; no hardware is required.

### Manual verification
- Action: Ran the assistant with the laptop microphone and spoke "volume up"
  twice and "volume down" twice.
- Result: The commands were recognized and the matching host media-key actions
  were sent. An unsupported phrase was rejected without an action.
- Limitation: The Windows volume indicator and audible output were not
  independently verified.
