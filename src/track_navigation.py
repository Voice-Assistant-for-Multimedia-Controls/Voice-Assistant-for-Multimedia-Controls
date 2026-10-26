
"""Track navigation module — owner: Shrinivas S J."""


class TrackNavigation:
    """Provide next/previous track navigation."""

    def __init__(self, controller):
        self.controller = controller

    def next_track(self) -> bool:
        """Request the next track through the shared controller."""
        try:
            self.controller.next_track()
            return True
        except Exception:
            return False

    def previous_track(self) -> bool:
        """Request the previous track through the shared controller."""
        try:
            self.controller.previous_track()
            return True
        except Exception:
            return False
