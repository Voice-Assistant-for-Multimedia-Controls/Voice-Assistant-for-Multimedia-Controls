
"""Shared multimedia controller interface.

Task owners should implement only their assigned methods and coordinate
interfaces before merging. This file contains basic Windows media-key
actions for play, resume, and pause.
"""


class MultimediaController:
    """Interface for multimedia actions."""

    def play(self):
        """Play multimedia using the Windows media key."""
        import pyautogui

        pyautogui.press("playpause")
        return "Play/resume media key sent."

    def resume(self):
        """Resume multimedia using the Windows media key."""
        import pyautogui

        pyautogui.press("playpause")
        return "Play/resume media key sent."

    def pause(self):
        """Pause multimedia using the Windows media key."""
        import pyautogui

        pyautogui.press("playpause")
        return "Pause media key sent."

    def next_track(self):
        """TODO (Shrinivas): implement next-track behavior."""
        raise NotImplementedError

    def previous_track(self):
        """TODO (Shrinivas): implement previous-track behavior."""
        raise NotImplementedError

    def volume_up(self):
        """TODO (Shreedhar): implement volume-up behavior."""
        raise NotImplementedError

    def volume_down(self):
        """TODO (Shreedhar): implement volume-down behavior."""
        raise NotImplementedError
