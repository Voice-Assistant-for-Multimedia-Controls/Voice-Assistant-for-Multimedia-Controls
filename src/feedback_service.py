
"""Command feedback module — owner: Shrinivas S J."""


class FeedbackService:
    """Provide feedback when a voice command is processed."""

    def say(self, message: str) -> bool:
        """Display command feedback to the user."""
        if not isinstance(message, str) or not message.strip():
            return False

        print(message)
        return True
