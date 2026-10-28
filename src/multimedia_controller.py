
"""Shared multimedia controller interface.

Supports playback, track navigation, and volume control.
"""

from src.volume_control import VolumeControl


class MultimediaController:
    """Interface for multimedia actions."""

    def __init__(self, volume_control=None):
        self.volume_control = volume_control or VolumeControl()

    def play(self):
        """Play or resume multimedia using the Windows media key."""
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
        """Skip to the next track using the system media key."""
        import pyautogui

        pyautogui.press("nexttrack")
        return "Next-track media key sent."

    def previous_track(self):
        """Return to the previous track using the system media key."""
        import pyautogui

        pyautogui.press("prevtrack")
        return "Previous-track media key sent."

    def volume_up(self):
        """Increase volume using the team's volume controller."""
        return self.volume_control.volume_up()

    def volume_down(self):
        """Decrease volume using the team's volume controller."""
        return self.volume_control.volume_down()
