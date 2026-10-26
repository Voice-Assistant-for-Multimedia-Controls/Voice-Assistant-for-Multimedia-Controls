"""Shared entry point for the Voice Assistant for Multimedia Controls project.

Team note:
- This is a starter scaffold, not a finished application.
- Each member should implement their assigned TODOs in their own branch.
- Keep module interfaces stable and coordinate changes through pull requests.
"""
from src.command_handler import CommandHandler
from src.multimedia_controller import MultimediaController
from src.feedback_service import FeedbackService
from src.voice_input import VoiceInput


def main() -> None:
    """Wire together the project modules. Feature implementation is left to owners."""
    feedback = FeedbackService()
    controller = MultimediaController()
    handler = CommandHandler(controller, feedback)
    voice_input = VoiceInput(feedback)

    print("Voice Assistant for Multimedia Controls — starter scaffold")
    print("Voice input and actions are not implemented yet.")
    print("Complete your assigned TODOs, then connect the modules here.")

    # TODO (Prajwal): implement the main loop after voice input and command
    # handling have been implemented and tested.
    # Example intended flow:
    # command = voice_input.listen_for_command()
    # handler.handle(command)


if __name__ == "__main__":
    main()
