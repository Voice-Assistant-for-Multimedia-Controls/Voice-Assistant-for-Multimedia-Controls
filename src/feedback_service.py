
"""Command feedback module — owner: Shrinivas S J."""

import pyttsx3


class FeedbackService:
    """Provide text and spoken feedback when a command is processed."""

    def __init__(self):
        """Initialize text-to-speech when available."""
        self.engine = None

        try:
            self.engine = pyttsx3.init()
        except Exception as error:
            print(f"Assistant: Speech output unavailable ({error})")

    def say(self, message: str) -> str:
        """Display feedback, speak it when possible, and return the message."""
        if not isinstance(message, str) or not message.strip():
            return ""

        message = message.strip()
        print(f"Assistant: {message}")

        if self.engine is not None:
            try:
                self.engine.say(message)
                self.engine.runAndWait()
            except Exception as error:
                print(f"Assistant: Could not speak message ({error})")

        return message
