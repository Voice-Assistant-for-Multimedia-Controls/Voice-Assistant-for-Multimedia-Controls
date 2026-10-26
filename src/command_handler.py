"""Command handling module — task owner: Prajwal GT."""


class CommandHandler:
    """Map recognized commands to the appropriate project action."""

    def __init__(self, controller, feedback) -> None:
        self.controller = controller
        self.feedback = feedback

    @staticmethod
    def normalize(command: str) -> str:
        """Normalize command text before matching."""
        return " ".join(command.lower().strip().split())

    def handle(self, command: str):
        """TODO (Prajwal): implement predefined command recognition/routing.

        Coordinate command names with teammates so each command maps to one
        implementation. Handle unsupported or unclear commands safely.
        """
        raise NotImplementedError("Command handling has not been implemented yet.")
