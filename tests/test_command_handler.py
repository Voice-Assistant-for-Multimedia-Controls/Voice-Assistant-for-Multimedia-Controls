
import unittest
from unittest.mock import patch

from src.command_handler import CommandHandler
from src.multimedia_controller import MultimediaController


class FakeFeedback:
    def __init__(self):
        self.messages = []

    def say(self, message):
        self.messages.append(message)


class MultimediaCommandTests(unittest.TestCase):

    def setUp(self):
        self.controller = MultimediaController()
        self.feedback = FakeFeedback()
        self.handler = CommandHandler(
            self.controller, self.feedback
        )

    # Original command-handler tests

    def test_play_music(self):
        with patch.object(
            self.controller, "play", return_value="Playing"
        ) as mock_play:
            self.handler.handle("play the music")
            mock_play.assert_called_once()
        print("PLAY MUSIC TEST: PASSED")

    def test_unsupported_command(self):
        self.handler.handle("hello")
        self.assertIn(
            "Unsupported command", self.feedback.messages[-1]
        )
        print("UNSUPPORTED COMMAND TEST: PASSED")

    def test_empty_command(self):
        self.handler.handle("")
        self.assertIn(
            "Unclear command", self.feedback.messages[-1]
        )
        print("EMPTY COMMAND TEST: PASSED")

    # Four multimedia controller tests

    @patch("src.multimedia_controller.pyautogui.press")
    @patch.object(MultimediaController, "_youtube_key", return_value=False)
    def test_previous_song(self, mock_youtube, mock_press):
        self.handler.handle("previous song")
        mock_press.assert_called_once_with("prevtrack")
        print("PREVIOUS SONG TEST: PASSED")

    @patch("src.multimedia_controller.pyautogui.press")
    @patch.object(MultimediaController, "_youtube_key", return_value=False)
    def test_next_song(self, mock_youtube, mock_press):
        self.handler.handle("next song")
        mock_press.assert_called_once_with("nexttrack")
        print("NEXT SONG TEST: PASSED")

    @patch("src.multimedia_controller.pyautogui.press")
    @patch.object(MultimediaController, "_youtube_key", return_value=False)
    def test_pause(self, mock_youtube, mock_press):
        self.handler.handle("pause")
        mock_press.assert_called_once_with("playpause")
        print("PAUSE TEST: PASSED")

    @patch("src.multimedia_controller.pyautogui.press")
    @patch.object(MultimediaController, "_youtube_key", return_value=False)
    def test_resume(self, mock_youtube, mock_press):
        self.handler.handle("resume")
        mock_press.assert_called_once_with("playpause")
        print("RESUME TEST: PASSED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
