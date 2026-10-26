"""Device communication module — task owner: Shreedhar R."""


class DeviceCommunication:
    """Interface for communication with Raspberry Pi / ESP hardware."""

    def connect(self):
        """TODO (Shreedhar): implement connection setup for the agreed device."""
        raise NotImplementedError

    def send_command(self, command: str):
        """TODO (Shreedhar): implement command transmission to the device."""
        raise NotImplementedError
