import unittest

from src.gesture_mapping import GestureMapping


class GestureMappingTests(unittest.TestCase):
    def setUp(self):
        self.mapping = GestureMapping()

    def test_supported_gestures_map_to_voice_commands(self):
        expected = {
            "open_palm": "play",
            "open palm": "play",
            "fist": "pause",
            "thumbs_up": "volume up",
            "thumbs down": "volume down",
        }
        for gesture, command in expected.items():
            with self.subTest(gesture=gesture):
                self.assertEqual(self.mapping.map_gesture(gesture), command)

    def test_case_and_whitespace_are_normalized(self):
        self.assertEqual(self.mapping.map_gesture("  OPEN PALM "), "play")
        self.assertEqual(self.mapping.map_gesture("Thumbs   Up"), "volume up")

    def test_unknown_or_invalid_gestures_are_ignored(self):
        for gesture in (None, "", "wave", 42):
            with self.subTest(gesture=gesture):
                self.assertIsNone(self.mapping.map_gesture(gesture))


if __name__ == "__main__":
    unittest.main()
