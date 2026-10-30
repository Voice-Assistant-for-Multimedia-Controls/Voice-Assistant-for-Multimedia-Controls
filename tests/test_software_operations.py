import contextlib
import io
import unittest
from unittest.mock import Mock, patch

from src.command_handler import CommandHandler
from src.feedback_service import FeedbackService
from src.multimedia_controller import MultimediaController
from src.volume_control import VolumeControl
from main import run_assistant


class SoftwareOperationsTests(unittest.TestCase):
    def setUp(self):
        self.media_keys = Mock()
        self.pyautogui = patch.dict(
            "sys.modules",
            {"pyautogui": self.media_keys},
        )
        self.pyautogui.start()
        self.addCleanup(self.pyautogui.stop)

    def test_controller_sends_media_keys_for_all_supported_actions(self):
        controller = MultimediaController(volume_control=VolumeControl())

        controller.play()
        controller.resume()
        controller.pause()
        controller.next_track()
        controller.previous_track()
        controller.volume_up()
        controller.volume_down()

        self.assertEqual(
            [call.args[0] for call in self.media_keys.press.call_args_list],
            [
                "playpause",
                "playpause",
                "playpause",
                "nexttrack",
                "prevtrack",
                "volumeup",
                "volumedown",
            ],
        )

    def test_continuous_loop_processes_repeated_commands_until_exit(self):
        commands = iter(
            [
                "play",
                None,
                "volume up",
                "volume up",
                "next track",
                "previous track",
                "pause",
                "exit",
            ]
        )
        voice_input = Mock()
        voice_input.listen_for_command.side_effect = lambda: next(commands)
        controller = MultimediaController(volume_control=VolumeControl())
        handler = CommandHandler(controller, FeedbackService())

        with contextlib.redirect_stdout(io.StringIO()):
            run_assistant(voice_input, handler)

        self.assertEqual(
            [call.args[0] for call in self.media_keys.press.call_args_list],
            [
                "playpause",
                "volumeup",
                "volumeup",
                "nexttrack",
                "prevtrack",
                "playpause",
            ],
        )
        self.assertEqual(voice_input.listen_for_command.call_count, 8)


if __name__ == "__main__":
    unittest.main()
