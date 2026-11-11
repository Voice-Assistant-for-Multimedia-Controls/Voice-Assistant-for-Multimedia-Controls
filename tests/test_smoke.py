import threading
import unittest
from unittest import mock

from main import run_assistant


class TestSmoke(unittest.TestCase):
    def test_run_assistant_handles_supported_commands_and_stops(self):
        voice_input = mock.Mock()
        voice_input.listen_for_command.side_effect = ["play music", "quit"]
        handler = mock.Mock()
        stop_event = threading.Event()

        run_assistant(voice_input, handler, stop_event)

        self.assertTrue(stop_event.is_set())
        handler.handle.assert_any_call("play music")

    def test_main_initializes_worker_thread(self):
        with mock.patch("main.FeedbackService"), \
             mock.patch("main.MultimediaController"), \
             mock.patch("main.CommandHandler"), \
             mock.patch("main.VoiceInput"), \
             mock.patch("main.run_assistant") as run_assistant_mock, \
             mock.patch("main.threading.Thread") as thread_mock:
            thread = mock.Mock()
            thread_mock.return_value = thread

            import main
            main.main()

        thread.start.assert_called_once()
        thread.join.assert_called_once_with(timeout=3)
        run_assistant_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
