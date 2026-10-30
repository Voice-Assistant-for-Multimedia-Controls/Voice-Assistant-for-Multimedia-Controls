"""Command feedback module — owner: Shrinivas S J."""

import logging

import pyttsx3

logger = logging.getLogger(__name__)


class FeedbackService:
    """Provide text and spoken feedback when a command is processed."""

    def __init__(self, rate: int = 170, volume: float = 1.0):
        """Initialize text-to-speech when available."""
        self.engine = None

        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", rate)
            self.engine.setProperty("volume", volume)
        except Exception as error:
            self.engine = None
            logger.warning("Speech output unavailable: %s", error)
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
                logger.warning("Could not speak message: %s", error)
                print(f"Assistant: Could not speak message ({error})")

        return message