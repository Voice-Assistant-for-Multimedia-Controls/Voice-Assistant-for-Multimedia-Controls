
"""Command handling module — task owner: Prajwal GT."""


class CommandHandler:
    """Map recognized voice commands to multimedia actions."""

    COMMANDS = {
        # Play
        "play": "play",
        "play music": "play",
        "play the music": "play",
        "start music": "play",
        "start playing": "play",

        # Resume
        "resume": "resume",
        "resume music": "resume",
        "continue music": "resume",
        "continue playing": "resume",

        # Pause
        "pause": "pause",
        "pause music": "pause",
        "pause the music": "pause",
        "stop": "pause",
        "stop music": "pause",
        "stop playing": "pause",

        # Next track/video
        "next": "next_track",
        "next music": "next_track",
        "next track": "next_track",
        "next song": "next_track",
        "next video": "next_track",
        "play next": "next_track",
        "play next song": "next_track",
        "skip": "next_track",
        "skip song": "next_track",

        # Previous track/video
        "previous": "previous_track",
        "previous music": "previous_track",
        "previous track": "previous_track",
        "previous song": "previous_track",
        "previous video": "previous_track",
        "play previous": "previous_track",
        "play previous song": "previous_track",
        "go back": "previous_track",
        "last song": "previous_track",

        # Volume
        "volume up": "volume_up",
        "increase volume": "volume_up",
        "increase the volume": "volume_up",
        "turn up volume": "volume_up",
        "volume down": "volume_down",
        "decrease volume": "volume_down",
        "decrease the volume": "volume_down",
        "turn down volume": "volume_down",
    }

    def __init__(self, controller, feedback) -> None:
        self.controller = controller
        self.feedback = feedback

    @staticmethod
    def normalize(command: str) -> str:
        """Normalize recognized speech before matching."""
        return " ".join((command or "").lower().strip().split())

    def handle(self, command: str):
        """Recognize a command and execute its controller action."""
        normalized = self.normalize(command)

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
                f"Action '{action_name}' is missing from the multimedia controller."
            )

        try:
            result = action()
            if result is not None:
                return self.feedback.say(str(result))

            return self.feedback.say(
                f"Command '{normalized}' processed."
            )

        except Exception as error:
            return self.feedback.say(
                f"Failed to execute '{normalized}': {error}"
            )
