"""Track navigation module — owner: Shrinivas S J."""

import logging

logger = logging.getLogger(__name__)


class TrackNavigation:
    """Provide next/previous track navigation."""

    def __init__(self, controller):
        self.controller = controller

    def next_track(self) -> bool:
        """Request the next track through the shared controller."""
        try:
            self.controller.next_track()
            logger.info("Next track requested")
            return True
        except Exception:
            logger.exception("Failed to skip to next track")
            return False

    def previous_track(self) -> bool:
        """Request the previous track through the shared controller."""
        try:
            self.controller.previous_track()
            logger.info("Previous track requested")
            return True
        except Exception:
            logger.exception("Failed to go to previous track")
            return False