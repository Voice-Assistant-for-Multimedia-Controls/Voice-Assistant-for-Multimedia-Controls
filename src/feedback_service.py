
"""Feedback module — text feedback for voice commands."""


class FeedbackService:
    """Display feedback after a command is processed."""

    def say(self, message: str) -> str:
        """Print a message and return it."""
        print(f"Assistant: {message}")
        return message
