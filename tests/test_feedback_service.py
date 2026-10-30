import logging
import unittest
from unittest.mock import MagicMock, patch

from src.feedback_service import FeedbackService


class TestFeedbackService(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    @patch("src.feedback_service.pyttsx3.init")
    def test_say_speaks_and_returns_stripped_message(self, mock_init):
        engine = MagicMock()
        mock_init.return_value = engine
        service = FeedbackService()

        self.assertEqual(service.say("  Next track  "), "Next track")
        engine.say.assert_called_once_with("Next track")
        engine.runAndWait.assert_called_once()

    @patch("src.feedback_service.pyttsx3.init")
    def test_empty_message_is_ignored(self, mock_init):
        engine = MagicMock()
        mock_init.return_value = engine
        service = FeedbackService()

        self.assertEqual(service.say("   "), "")
        engine.say.assert_not_called()

    @patch("src.feedback_service.pyttsx3.init")
    def test_non_string_message_is_ignored(self, mock_init):
        mock_init.return_value = MagicMock()
        service = FeedbackService()

        self.assertEqual(service.say(None), "")

    @patch("src.feedback_service.pyttsx3.init", side_effect=RuntimeError("no audio"))
    def test_works_without_speech_engine(self, _mock_init):
        service = FeedbackService()

        self.assertIsNone(service.engine)
        self.assertEqual(service.say("Hello"), "Hello")

    @patch("src.feedback_service.pyttsx3.init")
    def test_speech_failure_still_returns_message(self, mock_init):
        engine = MagicMock()
        engine.runAndWait.side_effect = RuntimeError("speaker error")
        mock_init.return_value = engine
        service = FeedbackService()

        self.assertEqual(service.say("Hello"), "Hello")

    @patch("src.feedback_service.pyttsx3.init")
    def test_report_chooses_message_by_result(self, mock_init):
        mock_init.return_value = MagicMock()
        service = FeedbackService()

        self.assertEqual(service.report(True, "Done", "Failed"), "Done")
        self.assertEqual(service.report(False, "Done", "Failed"), "Failed")


if __name__ == "__main__":
    unittest.main()

    @patch("src.feedback_service.pyttsx3.init")
    def test_track_changed_success_and_failure(self, mock_init):
            mock_init.return_value = MagicMock()
            service = FeedbackService()

            self.assertEqual(service.track_changed("next", True), "Playing next track")
            self.assertEqual(
            service.track_changed("previous", False),
            "Sorry, I couldn't go to the previous track",
        )

    @patch("src.feedback_service.pyttsx3.init")
    def test_track_changed_ignores_unknown_direction(self, mock_init):
        mock_init.return_value = MagicMock()
        service = FeedbackService()

        self.assertEqual(service.track_changed("sideways", True), "")




    