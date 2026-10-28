
"""Command handling module — task owner: Prajwal GT."""


class CommandHandler:
    """Map recognized commands to the appropriate project action."""

    COMMANDS = {
        "play": "play",
        "play music": "play",
        "play the music": "play",
        "resume": "resume",
        "resume music": "resume",
        "pause": "pause",
        "pause music": "pause",
        "next": "next_track",
        "next track": "next_track",
        "previous": "previous_track",
        "previous track": "previous_track",
        "volume up": "volume_up",
        "volume down": "volume_down",
    }

    def __init__(self, controller, feedback) -> None:
        self.controller = controller
        self.feedback = feedback

    @staticmethod
    def normalize(command: str) -> str:
        """Normalize command text before matching."""
        return " ".join(command.lower().strip().split())

    def handle(self, command: str):
        """Recognize supported commands and route them safely."""
        normalized = self.normalize(command or "")

        if not normalized:
            return self.feedback.say(
                "Unclear command. Please try again."
            )

        action_name = self.COMMANDS.get(normalized)

        if action_name is None:
            return self.feedback.say(
                f"Unsupported command: '{normalized}'. No action taken."
            )

        action = getattr(self.controller, action_name, None)

        if not callable(action):
            return self.feedback.say(
                f"Command '{normalized}' recognized, but its action "
                "is not implemented yet."
            )

        result = action()

        if result is not None:
            return self.feedback.say(str(result))

        return self.feedback.say(f"Command '{normalized}' executed.")
