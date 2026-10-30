import unittest
from unittest.mock import MagicMock

from src.track_navigation import TrackNavigation


class TestTrackNavigation(unittest.TestCase):
    def setUp(self):
        self.controller = MagicMock()
        self.nav = TrackNavigation(self.controller)

    def test_next_track_calls_controller(self):
        self.assertTrue(self.nav.next_track())
        self.controller.next_track.assert_called_once()

    def test_previous_track_calls_controller(self):
        self.assertTrue(self.nav.previous_track())
        self.controller.previous_track.assert_called_once()

    def test_next_track_returns_false_on_error(self):
        self.controller.next_track.side_effect = RuntimeError("fail")
        self.assertFalse(self.nav.next_track())

    def test_previous_track_returns_false_on_error(self):
        self.controller.previous_track.side_effect = RuntimeError("fail")
        self.assertFalse(self.nav.previous_track())


if __name__ == "__main__":
    unittest.main()