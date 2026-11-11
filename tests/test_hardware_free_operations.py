import threading
import unittest
from unittest.mock import MagicMock, Mock, patch

from main import run_gesture_controls
from src.voice_input import VoiceInput


class HardwareFreeOperationsTests(unittest.TestCase):
    @patch("src.voice_input.sr.Recognizer")
    @patch("src.voice_input.sr.Microphone")
    def test_voice_input_recognizes_command_with_mocked_microphone(
        self,
        mock_microphone,
        mock_recognizer,
    ):
        source = object()
        microphone = MagicMock()
        microphone.__enter__.return_value = source
        mock_microphone.return_value = microphone

        recognizer = Mock()
        recognizer.recognize_google.return_value = "  Play Music  "
        mock_recognizer.return_value = recognizer

        voice_input = VoiceInput(device_index=2)

        self.assertEqual(voice_input.listen_for_command(), "play music")
        mock_microphone.assert_called_once_with(
            device_index=2,
            sample_rate=44100,
        )
        recognizer.adjust_for_ambient_noise.assert_called_once_with(
            source,
            duration=1,
        )
        recognizer.listen.assert_called_once_with(
            source,
            timeout=10,
            phrase_time_limit=6,
        )

    @patch("main.GestureControl")
    def test_gesture_controls_dispatch_command_with_mocked_webcam(
        self,
        mock_gesture_control,
    ):
        frame = object()
        camera = Mock()
        camera.read.return_value = (True, frame)
        gesture_control = Mock()
        gesture_control.camera = camera
        gesture_control.show_window = False
        gesture_control.recognize_gesture.return_value = "open_palm"
        mock_gesture_control.return_value = gesture_control

        handler = Mock()
        stop_event = threading.Event()
        handler.handle.side_effect = lambda _command: stop_event.set()
        feedback = Mock()
        cv2 = Mock()
        cv2.flip.return_value = frame

        with patch.dict("sys.modules", {"cv2": cv2}):
            run_gesture_controls(handler, feedback, stop_event)

        mock_gesture_control.assert_called_once_with(camera_index=1)
        gesture_control.start_camera.assert_called_once()
        camera.read.assert_called_once()
        gesture_control.recognize_gesture.assert_called_once_with(frame)
        handler.handle.assert_called_once_with("play")
        gesture_control.close.assert_called_once()
        cv2.destroyAllWindows.assert_called_once()


if __name__ == "__main__":
    unittest.main()
