
"""Multimedia controller for YouTube and Windows media controls."""

import time

import pyautogui
import pygetwindow as gw

from src.volume_control import VolumeControl


class MultimediaController:
    """Control YouTube playback and system volume."""

    def __init__(self, volume_control=None):
        self.volume_control = volume_control or VolumeControl()

    @staticmethod
    def _find_youtube_window():
        """Find an open YouTube window."""
        for window in gw.getAllWindows():
            title = (window.title or "").lower()
            if "youtube" in title and window.width > 0:
                return window
        return None

    def _youtube_key(self, key, shift=False):
        """Focus YouTube and send a keyboard shortcut."""
        window = self._find_youtube_window()

        if window is None:
            return False

        try:
            if window.isMinimized:
                window.restore()

            window.activate()
            time.sleep(0.5)

            if shift:
                pyautogui.hotkey("shift", key)
            else:
                pyautogui.press(key)

            return True
        except Exception as error:
            print(f"YouTube control error: {error}")
            return False

    def play(self):
        if self._youtube_key("k"):
            return "YouTube play/pause shortcut sent."
        pyautogui.press("play")
        return "Play media key sent."

    def resume(self):
        return self.play()

    def pause(self):
        if self._youtube_key("k"):
            return "YouTube play/pause shortcut sent."
        pyautogui.press("pause")
        return "Pause media key sent."

    def next_track(self):
        if self._youtube_key("n", shift=True):
            return "YouTube next-video shortcut sent."
        pyautogui.press("nexttrack")
        return "Next-track media key sent."

    def previous_track(self):
        if self._youtube_key("p", shift=True):
            return "YouTube previous-video shortcut sent."
        pyautogui.press("prevtrack")
        return "Previous-track media key sent."

    def volume_up(self):
        return self.volume_control.volume_up()

    def volume_down(self):
        return self.volume_control.volume_down()
