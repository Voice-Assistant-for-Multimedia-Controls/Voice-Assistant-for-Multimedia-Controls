import unittest
from unittest.mock import Mock, patch

from src.multimedia_controller import MultimediaController
from src.volume_control import VolumeControl


class VolumeControlTests(unittest.TestCase):
    def setUp(self):
        self.media_keys = Mock()
        self.pyautogui = patch.dict(
            "sys.modules",
            {"pyautogui": self.media_keys},
        )
        self.pyautogui.start()
        self.addCleanup(self.pyautogui.stop)
        self.controller = MultimediaController(
            volume_control=VolumeControl()
        )

    def test_volume_up_sends_host_volume_up_key(self):
        result = self.controller.volume_up()

        self.media_keys.press.assert_called_once_with("volumeup")
        self.assertEqual(result, "Volume up media key sent.")

    def test_volume_down_sends_host_volume_down_key(self):
        result = self.controller.volume_down()

        self.media_keys.press.assert_called_once_with("volumedown")
        self.assertEqual(result, "Volume down media key sent.")

    def test_repeated_commands_send_one_key_press_per_command(self):
        self.controller.volume_up()
        self.controller.volume_up()
        self.controller.volume_down()

        self.assertEqual(
            [call.args[0] for call in self.media_keys.press.call_args_list],
            ["volumeup", "volumeup", "volumedown"],
        )


if __name__ == "__main__":
    unittest.main()
