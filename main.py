
from src.command_handler import CommandHandler
from src.multimedia_controller import MultimediaController
from src.feedback_service import FeedbackService
from src.voice_input import VoiceInput


def main():
    feedback = FeedbackService()
    controller = MultimediaController()
    handler = CommandHandler(controller, feedback)
    voice_input = VoiceInput(feedback)

    print("Voice Assistant — US-01 Test")
    print("Speak a command, or say 'exit' to stop.")

    while True:
        command = voice_input.listen_for_command()

        if command is None:
            continue

        if command.strip().lower() in {"exit", "stop","quit"}:
            print("Assistant stopped.")
            break

        print(f"Recognized command: {command}")

        try:
            handler.handle(command)
        except NotImplementedError:
            print("This command's media action is not implemented yet.")


if __name__ == "__main__":
    main()
