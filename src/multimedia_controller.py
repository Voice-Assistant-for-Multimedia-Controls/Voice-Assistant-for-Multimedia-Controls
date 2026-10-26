"""Shared multimedia controller interface.

Task owners should implement only their assigned methods and coordinate
interfaces before merging. This file intentionally contains no action logic.
"""


class MultimediaController:
    """Interface for multimedia actions."""

    def play(self):
        """TODO (Prajwal): implement play/resume behavior."""
        raise NotImplementedError

    def resume(self):
        """TODO (Prajwal): implement resume behavior."""
        raise NotImplementedError

    def pause(self):
        """TODO (Prajwal): implement pause behavior."""
        raise NotImplementedError

    def next_track(self):
        """TODO (Shrinivas): implement next-track behavior."""
        raise NotImplementedError

    def previous_track(self):
        """TODO (Shrinivas): implement previous-track behavior."""
        raise NotImplementedError

    def volume_up(self):
        """TODO (Shreedhar): implement volume-up behavior."""
        raise NotImplementedError

    def volume_down(self):
        """TODO (Shreedhar): implement volume-down behavior."""
        raise NotImplementedError
