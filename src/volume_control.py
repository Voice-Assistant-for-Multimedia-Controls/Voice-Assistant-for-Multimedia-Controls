"""Software volume control using the host computer's media keys."""


class VolumeControl:
    """Control system media volume without an external hardware device."""

    def volume_up(self):
        """Increase the host computer's media volume."""
        import pyautogui

        pyautogui.press("volumeup")
        return "Volume up media key sent."

    def volume_down(self):
        """Decrease the host computer's media volume."""
        import pyautogui

        pyautogui.press("volumedown")
        return "Volume down media key sent."
