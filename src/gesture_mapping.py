"""Translate recognized gestures into existing voice-command vocabulary."""


class GestureMapping:
    """Map supported gesture labels to commands accepted by CommandHandler.

    ``None`` is returned for unknown, empty, or unsupported gestures so that
    an uncertain detection never accidentally executes a multimedia action.
    """

    GESTURE_COMMANDS = {
        "open_palm": "play",
        "open palm": "play",
        "openpalm": "play",
        "open hand": "play",
        "fist": "pause",
        "closed fist": "pause",
        "closed_fist": "pause",
        "thumbs_up": "volume up",
        "thumbs up": "volume up",
        "thumbsup": "volume up",
        "thumbs_down": "volume down",
        "thumbs down": "volume down",
        "thumbsdown": "volume down",
    }

    def map_gesture(self, gesture: str):
        """Return the corresponding command-handler command or ``None``."""
        if not isinstance(gesture, str):
            return None

        normalized = gesture.strip().lower().replace("_", " ").replace("-", " ")
        normalized = " ".join(normalized.split())
        compact = normalized.replace(" ", "")

        for candidate in (normalized, compact):
            command = self.GESTURE_COMMANDS.get(candidate)
            if command is not None:
                return command

        return None
