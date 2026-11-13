import contextlib
import io
import threading
import unittest
from unittest.mock import Mock, patch

from src.command_handler import CommandHandler
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
        self.multimedia_pyautogui = patch(
            "src.multimedia_controller.pyautogui",
            self.media_keys,
        )
        self.multimedia_pyautogui.start()
        self.addCleanup(self.multimedia_pyautogui.stop)
        self.windows = patch(
            "src.multimedia_controller.gw.getAllWindows",
            return_value=[],
        )
        self.windows.start()
        self.addCleanup(self.windows.stop)

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
                "play",
                "play",
                "pause",
                "nexttrack",
                "prevtrack",
                "volumeup",
                "volumedown",
            ],
        )

    def test_volume_commands_accept_common_voice_variants(self):
        handler = CommandHandler(MultimediaController(volume_control=VolumeControl()), Mock())

        for command in (
            "volume up",
            "turn up the volume",
            "make it louder",
            "volume down",
            "turn down the volume",
            "make it quieter",
        ):
            handler.handle(command)

        self.assertEqual(
            [call.args[0] for call in self.media_keys.press.call_args_list],
            [
                "volumeup",
                "volumeup",
                "volumeup",
                "volumedown",
                "volumedown",
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
        handler = CommandHandler(controller, Mock())
        stop_event = threading.Event()

        with contextlib.redirect_stdout(io.StringIO()):
            run_assistant(voice_input, handler, stop_event)

        self.assertEqual(
            [call.args[0] for call in self.media_keys.press.call_args_list],
            [
                "play",
                "volumeup",
                "volumeup",
                "nexttrack",
                "prevtrack",
                "pause",
            ],
        )
        self.assertEqual(voice_input.listen_for_command.call_count, 8)
        self.assertTrue(stop_event.is_set())


if __name__ == "__main__":
    unittest.main()
