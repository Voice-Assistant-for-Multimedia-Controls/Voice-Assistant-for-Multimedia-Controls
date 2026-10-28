
"""Main entry point for the voice multimedia assistant."""

from src.command_handler import CommandHandler
from src.multimedia_controller import MultimediaController
from src.feedback_service import FeedbackService
from src.voice_input import VoiceInput


def main():
    feedback = FeedbackService()
    controller = MultimediaController()
    handler = CommandHandler(controller, feedback)
    voice_input = VoiceInput(feedback)

    print("\n=== Voice Multimedia Assistant ===")
    print("Commands: play music, resume, pause")
    print("Say 'exit' or 'quit' to stop.\n")

    while True:
        try:
            command = voice_input.listen_for_command()

            if command is None:
                continue

            command = command.strip().lower()

            if command in {"exit", "stop","quit"}:
                feedback.say("Assistant stopped.")
                break

            print(f"Recognized command: {command}")
            handler.handle(command)

        except KeyboardInterrupt:
            print("\nAssistant stopped.")
            break
        except NotImplementedError as error:
            feedback.say(f"This feature is not implemented yet: {error}")
        except Exception as error:
            feedback.say(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
