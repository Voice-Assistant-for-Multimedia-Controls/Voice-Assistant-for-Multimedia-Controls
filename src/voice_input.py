"""Voice input module — task owner: Prajwal GT."""


class VoiceInput:
    """Capture a spoken command and return recognized text."""

    def __init__(self, feedback=None) -> None:
        self.feedback = feedback

    def listen_for_command(self):
        """TODO (Prajwal): implement microphone capture and speech recognition.

        Return the recognized command as a string, or None if no command was
        understood. Follow the submitted SRS, SAD, and Test Plan.
        """
        raise NotImplementedError("Voice input has not been implemented yet.")
