"""Webcam-based hand gesture recognition using MediaPipe's Hand Landmarker.

Recognized gestures are emitted once per gesture hold. A neutral/no-hand
period is required before the same gesture can trigger again, preventing a
held hand pose from repeatedly sending multimedia commands.

Note: this uses the MediaPipe *Tasks* API (``HandLandmarker``). The older
``mediapipe.solutions`` API was removed in recent MediaPipe releases, which
is what caused "module 'mediapipe' has no attribute 'solutions'".
"""

from __future__ import annotations

import time
import urllib.request
from pathlib import Path
from typing import Optional

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
DEFAULT_MODEL_PATH = (
    Path(__file__).resolve().parent.parent / "models" / "hand_landmarker.task"
)


class GestureControl:
    """Capture camera frames and recognize stable, configured gestures.

    ``recognize_gesture`` returns one of ``open_palm``, ``fist``,
    ``thumbs_up`` or ``thumbs_down`` when a gesture has been stable for the
    configured number of frames. It returns ``None`` otherwise.
    """

    def __init__(
        self,
        camera_index: int = 0,
        min_detection_confidence: float = 0.75,
        min_tracking_confidence: float = 0.70,
        stable_frames: int = 5,
        show_window: bool = True,
        model_path: Optional[str] = None,
    ) -> None:
        if stable_frames < 1:
            raise ValueError("stable_frames must be at least 1")
        self.camera_index = camera_index
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.stable_frames = stable_frames
        self.show_window = show_window
        self.model_path = Path(model_path) if model_path else DEFAULT_MODEL_PATH
        self.camera = None
        self.hands = None  # HandLandmarker instance
        self._candidate: Optional[str] = None
        self._candidate_count = 0
        self._gesture_latched = False
        self._last_timestamp_ms = 0

    def _ensure_model(self) -> Path:
        """Return the path to the hand model, downloading it on first use."""
        path = self.model_path
        if path.exists() and path.stat().st_size > 0:
            return path

        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(".download")
        try:
            urllib.request.urlretrieve(MODEL_URL, temp_path)
            temp_path.replace(path)
        except Exception as error:
            temp_path.unlink(missing_ok=True)
            raise RuntimeError(
                "Hand model not found and automatic download failed. "
                f"Download {MODEL_URL} and save it as {path}."
            ) from error
        return path

    def start_camera(self):
        """Initialize MediaPipe and open the webcam; return the capture object.

        Raises ``RuntimeError`` with an actionable message if the camera or
        MediaPipe setup is unavailable.
        """
        try:
            import cv2
            from mediapipe.tasks.python import BaseOptions, vision
        except ImportError as error:
            raise RuntimeError(
                "Gesture dependencies are missing. Install requirements.txt."
            ) from error

        if self.camera is not None and self.camera.isOpened():
            return self.camera

        # Load the model first so a missing model fails before the camera opens.
        model_file = self._ensure_model()
        options = vision.HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(model_file)),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=self.min_detection_confidence,
            min_hand_presence_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence,
        )
        self.hands = vision.HandLandmarker.create_from_options(options)

        self.camera = cv2.VideoCapture(self.camera_index)
        if not self.camera.isOpened():
            self.camera.release()
            self.camera = None
            self.hands.close()
            self.hands = None
            raise RuntimeError(
                f"Could not open webcam index {self.camera_index}. "
                "Check camera permissions or change camera_index."
            )
        return self.camera

    @staticmethod
    def _classify_landmarks(landmarks) -> Optional[str]:
        """Classify a single hand from MediaPipe's 21 normalized landmarks.

        ``landmarks`` is the list of landmarks returned by the Tasks API
        (``result.hand_landmarks[0]``). The legacy object with a
        ``.landmark`` attribute is also accepted.

        This lightweight rule-based classifier intentionally recognizes only
        a small set of distinct poses; ambiguous poses are rejected.
        """
        points = getattr(landmarks, "landmark", landmarks)
        thumb_tip, thumb_ip, thumb_mcp = points[4], points[3], points[2]
        finger_pairs = ((8, 6), (12, 10), (16, 14), (20, 18))
        extended = [points[tip].y < points[pip].y - 0.015
                    for tip, pip in finger_pairs]
        curled = [points[tip].y > points[pip].y + 0.015
                  for tip, pip in finger_pairs]

        if all(extended):
            return "open_palm"

        # Check thumb direction before classifying a fully curled hand as a fist.
        # For a thumbs-up/down, the four non-thumb fingers should be curled.
        if sum(curled) >= 3:
            if thumb_tip.y < thumb_ip.y - 0.04:
                return "thumbs_up"
            if thumb_tip.y > thumb_ip.y + 0.04:
                return "thumbs_down"

        if all(curled):
            return "fist"

        # Detect thumbs-up/down even if one curled finger is borderline.
        if sum(curled) >= 3:
            thumb_vertical = thumb_tip.y - thumb_ip.y
            thumb_outward = abs(thumb_tip.x - thumb_mcp.x) > 0.04
            if thumb_outward and thumb_vertical < -0.06:
                return "thumbs_up"
            if thumb_outward and thumb_vertical > 0.06:
                return "thumbs_down"

        return None

    def _next_timestamp_ms(self) -> int:
        """Return a strictly increasing timestamp, as VIDEO mode requires."""
        timestamp = int(time.monotonic() * 1000)
        if timestamp <= self._last_timestamp_ms:
            timestamp = self._last_timestamp_ms + 1
        self._last_timestamp_ms = timestamp
        return timestamp

    def recognize_gesture(self, frame) -> Optional[str]:
        """Return a stable gesture once; return ``None`` for uncertain frames."""
        if self.hands is None:
            raise RuntimeError("Call start_camera() before recognize_gesture().")

        import cv2
        import mediapipe as mp

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = self.hands.detect_for_video(image, self._next_timestamp_ms())
        detected = None
        if result.hand_landmarks:
            detected = self._classify_landmarks(result.hand_landmarks[0])

        if detected is None:
            self._candidate = None
            self._candidate_count = 0
            self._gesture_latched = False
            return None

        if detected == self._candidate:
            self._candidate_count += 1
        else:
            self._candidate = detected
            self._candidate_count = 1

        if self._candidate_count < self.stable_frames or self._gesture_latched:
            return None

        self._gesture_latched = True
        return detected

    def draw_feedback(self, frame, gesture: Optional[str] = None):
        """Draw simple status text on a frame; returns the annotated frame."""
        import cv2

        label = f"Gesture: {gesture.replace('_', ' ')}" if gesture else "Show a clear gesture"
        cv2.putText(frame, label, (12, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, "Press Q to close gesture window", (12, 58),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1,
                    cv2.LINE_AA)
        return frame

    def close(self) -> None:
        """Release camera and MediaPipe resources safely."""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
        if self.hands is not None:
            self.hands.close()
            self.hands = None
        try:
            import cv2
            cv2.destroyWindow("Gesture Controls")
        except Exception:
            # GUI cleanup can fail on headless systems; camera cleanup is done.
            pass
