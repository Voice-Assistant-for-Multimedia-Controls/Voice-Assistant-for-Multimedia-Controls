
"""Command feedback module — owner: Shrinivas S J."""


class FeedbackService:
    """Provide feedback when a voice command is processed."""

    def say(self, message: str) -> str:
        """Display command feedback and return it."""
        if not isinstance(message, str) or not message.strip():
            return ""

        print(f"Assistant: {message}")
        return message
