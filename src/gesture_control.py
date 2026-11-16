"""Webcam-based hand gesture recognition using MediaPipe's Hand Landmarker.

Recognized gestures are emitted once per gesture hold. A short temporal vote
smooths noisy frames, while a multi-frame neutral/no-hand period is required
before a new command can trigger. Pose rules use 3D joint geometry rather than
mostly image-space y-coordinate comparisons.

Note: this uses the MediaPipe *Tasks* API (``HandLandmarker``). The older
``mediapipe.solutions`` API was removed in recent MediaPipe releases, which
is what caused "module 'mediapipe' has no attribute 'solutions'".
"""

from __future__ import annotations

import time
import urllib.request
from collections import Counter, deque
from math import acos, degrees, sqrt
from pathlib import Path
from typing import Deque, Optional

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
    ``thumbs_up`` or ``thumbs_down`` after enough votes in a short frame
    window. It returns ``None`` otherwise and requires a neutral interval to
    re-arm after a command.
    """

    def __init__(
        self,
        camera_index: int = 0,
        min_detection_confidence: float = 0.75,
        min_tracking_confidence: float = 0.70,
        stable_frames: int = 5,
        release_frames: int = 5,
        show_window: bool = True,
        model_path: Optional[str] = None,
    ) -> None:
        if stable_frames < 1:
            raise ValueError("stable_frames must be at least 1")
        if release_frames < 1:
            raise ValueError("release_frames must be at least 1")
        self.camera_index = camera_index
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.stable_frames = stable_frames
        self.release_frames = release_frames
        self.show_window = show_window
        self.model_path = Path(model_path) if model_path else DEFAULT_MODEL_PATH
        self.camera = None
        self.hands = None  # HandLandmarker instance
        # Vote over a short temporal window to smooth single-frame landmark noise.
        self._history: Deque[Optional[str]] = deque(maxlen=stable_frames + 2)
        self._gesture_latched = False
        self._neutral_count = 0
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

        # Reset temporal state if the same controller is started again.
        self._history.clear()
        self._gesture_latched = False
        self._neutral_count = 0

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
    def _point_xyz(point, aspect_ratio: float = 1.0):
        """Read a landmark in height-normalized 3D coordinates.

        MediaPipe normalizes x and y by different frame dimensions. Scaling x
        and z by width/height keeps joint geometry consistent on 4:3 and 16:9
        webcams rather than distorting angles on non-square frames.
        """
        return (
            float(point.x) * aspect_ratio,
            float(point.y),
            float(getattr(point, "z", 0.0)) * aspect_ratio,
        )

    @classmethod
    def _distance(cls, first, second, aspect_ratio: float = 1.0) -> float:
        """Euclidean distance between two aspect-corrected 3D landmarks."""
        a = cls._point_xyz(first, aspect_ratio)
        b = cls._point_xyz(second, aspect_ratio)
        return sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))

    @classmethod
    def _joint_angle(cls, first, joint, last, aspect_ratio: float = 1.0) -> float:
        """Angle at ``joint`` in degrees, computed from 3D landmarks."""
        a = cls._point_xyz(first, aspect_ratio)
        b = cls._point_xyz(joint, aspect_ratio)
        c = cls._point_xyz(last, aspect_ratio)
        ba = tuple(a[i] - b[i] for i in range(3))
        bc = tuple(c[i] - b[i] for i in range(3))
        ba_len = sqrt(sum(value * value for value in ba))
        bc_len = sqrt(sum(value * value for value in bc))
        if ba_len < 1e-8 or bc_len < 1e-8:
            return 0.0
        cosine = sum(ba[i] * bc[i] for i in range(3)) / (ba_len * bc_len)
        # Floating-point rounding can otherwise put acos just outside [-1, 1].
        cosine = max(-1.0, min(1.0, cosine))
        return degrees(acos(cosine))

    @classmethod
    def _finger_state(cls, points, mcp, pip, dip, tip, aspect_ratio: float = 1.0) -> str:
        """Classify a non-thumb finger using joint angles and relative reach.

        Joint angles are less sensitive to hand rotation than comparing tip and
        joint y-coordinates. The wrist-relative distance acts as a second check
        so a nearly straight but folded finger is not treated as extended.
        """
        pip_angle = cls._joint_angle(
            points[mcp], points[pip], points[dip], aspect_ratio
        )
        dip_angle = cls._joint_angle(
            points[pip], points[dip], points[tip], aspect_ratio
        )
        wrist_to_pip = cls._distance(points[0], points[pip], aspect_ratio)
        wrist_to_tip = cls._distance(points[0], points[tip], aspect_ratio)
        reach_ratio = wrist_to_tip / max(wrist_to_pip, 1e-6)

        if pip_angle >= 150 and dip_angle >= 140 and reach_ratio >= 1.05:
            return "extended"
        if pip_angle <= 135 and (dip_angle <= 155 or reach_ratio < 0.98):
            return "curled"
        # In a tight fist, one joint can remain nearly straight while the distal
        # joint folds sharply. Requiring a short wrist-to-tip reach guards this
        # fallback against treating an isolated bent fingertip as a closed fist.
        if pip_angle <= 145 and (dip_angle <= 125 or reach_ratio < 0.95):
            return "curled"
        if dip_angle <= 115 and reach_ratio <= 1.15:
            return "curled"
        return "ambiguous"

    @classmethod
    def _classify_landmarks(cls, landmarks, aspect_ratio: float = 1.0) -> Optional[str]:
        """Classify a hand pose from MediaPipe's 21 normalized landmarks.

        Uses 3D joint angles, wrist-relative reach and scale-normalized thumb
        geometry instead of relying mainly on image-space y-coordinate checks.
        Ambiguous or very small detections are ignored to favor precision over
        issuing an unintended multimedia command.
        """
        points = getattr(landmarks, "landmark", landmarks)
        if points is None or len(points) < 21:
            return None

        # Reject tiny detections, whose joint angles are often dominated by
        # pixel/landmark noise. Either dimension may be larger for rotated hands.
        if aspect_ratio <= 0:
            return None
        xs = [float(point.x) * aspect_ratio for point in points]
        ys = [float(point.y) for point in points]
        if max(max(xs) - min(xs), max(ys) - min(ys)) < 0.075:
            return None

        finger_specs = (
            (5, 6, 7, 8),   # index
            (9, 10, 11, 12),  # middle
            (13, 14, 15, 16),  # ring
            (17, 18, 19, 20),  # pinky
        )
        states = [
            cls._finger_state(points, *spec, aspect_ratio=aspect_ratio)
            for spec in finger_specs
        ]
        extended_count = states.count("extended")
        curled_count = states.count("curled")

        thumb_tip = points[4]
        thumb_ip = points[3]
        thumb_mcp = points[2]
        index_mcp = points[5]
        pinky_mcp = points[17]
        palm_width = cls._distance(index_mcp, pinky_mcp, aspect_ratio)
        if palm_width < 1e-6:
            return None

        thumb_ip_angle = cls._joint_angle(
            thumb_mcp, thumb_ip, thumb_tip, aspect_ratio
        )
        thumb_spread = cls._distance(thumb_tip, index_mcp, aspect_ratio) / palm_width
        thumb_extended = thumb_ip_angle >= 130 and thumb_spread >= 0.55

        # Open palm requires every long finger to be clearly extended and the
        # thumb to be separated from the palm, reducing false plays from waves.
        if extended_count == 4 and thumb_extended:
            return "open_palm"

        # Four curled fingers plus a clearly extended, vertically oriented thumb
        # distinguish thumbs-up/down from a fist. Normalize by palm width so the
        # threshold works at different camera distances.
        if curled_count >= 3 and extended_count <= 1 and thumb_extended:
            thumb_vertical = float(thumb_tip.y) - float(thumb_mcp.y)
            vertical_ratio = thumb_vertical / palm_width
            if vertical_ratio <= -0.45:
                return "thumbs_up"
            if vertical_ratio >= 0.45:
                return "thumbs_down"

        if curled_count == 4 and not thumb_extended:
            return "fist"

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
            frame_aspect_ratio = frame.shape[1] / max(frame.shape[0], 1)
            detected = self._classify_landmarks(
                result.hand_landmarks[0], aspect_ratio=frame_aspect_ratio
            )

        return self._stabilize_detection(detected)

    def _stabilize_detection(self, detected: Optional[str]) -> Optional[str]:
        """Smooth frame noise and emit one command per deliberate pose."""
        self._history.append(detected)

        # A brief missed frame must not re-arm a held gesture. Require several
        # consecutive neutral frames before allowing the next command.
        if self._gesture_latched:
            if detected is None:
                self._neutral_count += 1
            else:
                self._neutral_count = 0
            if self._neutral_count >= self.release_frames:
                self._gesture_latched = False
                self._neutral_count = 0
                self._history.clear()
            return None

        counts = Counter(item for item in self._history if item is not None)
        if not counts:
            return None
        candidate, votes = counts.most_common(1)[0]
        if votes < self.stable_frames:
            return None

        self._gesture_latched = True
        self._neutral_count = 0
        return candidate

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
