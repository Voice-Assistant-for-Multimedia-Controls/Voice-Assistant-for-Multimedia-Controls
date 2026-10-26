"""Gesture recognition module — task owner: Sarang S Nair."""


class GestureControl:
    """Capture camera frames and recognize configured gestures."""

    def start_camera(self):
        """TODO (Sarang): initialize camera access."""
        raise NotImplementedError

    def recognize_gesture(self, frame):
        """TODO (Sarang): recognize gestures using the agreed MediaPipe setup."""
        raise NotImplementedError
