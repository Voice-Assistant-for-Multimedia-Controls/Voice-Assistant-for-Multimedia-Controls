"""Translate recognized gestures into existing voice-command vocabulary."""


class GestureMapping:
    """Map supported gesture labels to commands accepted by CommandHandler.

    ``None`` is returned for unknown, empty, or unsupported gestures so that
    an uncertain detection never accidentally executes a multimedia action.
    """

    GESTURE_COMMANDS = {
        "open_palm": "play",
        "open palm": "play",
        "fist": "pause",
        "thumbs_up": "volume up",
        "thumbs up": "volume up",
        "thumbs_down": "volume down",
        "thumbs down": "volume down",
    }

    def map_gesture(self, gesture: str):
        """Return the corresponding command-handler command or ``None``."""
        if not isinstance(gesture, str):
            return None
        normalized = " ".join(gesture.strip().lower().replace("-", " ").split())
        # Accept underscore and spaced variants consistently.
        normalized = normalized.replace(" ", "_") if normalized in {
            "open palm", "thumbs up", "thumbs down", "swipe right", "swipe left"
        } else normalized
        return self.GESTURE_COMMANDS.get(normalized)
