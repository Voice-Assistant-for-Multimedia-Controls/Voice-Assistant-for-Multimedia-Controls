
from src.command_handler import CommandHandler
from src.feedback_service import FeedbackService
from src.multimedia_controller import MultimediaController
from src.voice_input import VoiceInput


class ReportingController:
    def __init__(self):
        self.real_controller = MultimediaController()

    def _run_test(self, action, label):
        result = action()
        print(f"\n{label} TEST: PASSED\n")
        return result

    def play(self):
        return self._run_test(
            self.real_controller.play, "PLAY MUSIC"
        )

    def previous_track(self):
        return self._run_test(
            self.real_controller.previous_track, "PREVIOUS SONG"
        )

    def next_track(self):
        return self._run_test(
            self.real_controller.next_track, "NEXT SONG"
        )

    def pause(self):
        return self._run_test(
            self.real_controller.pause, "PAUSE"
        )

    def resume(self):
        return self._run_test(
            self.real_controller.resume, "RESUME"
        )


def main():
    print("\n======================================")
    print("   LIVE MULTIMEDIA VOICE TEST")
    print("======================================")
    print("1. Play Music")
    print("2. Previous Song")
    print("3. Next Song")
    print("4. Pause")
    print("5. Resume")
    print("Say 'exit assistant' to stop.")
    print("======================================\n")

    feedback = FeedbackService()
    controller = ReportingController()
    handler = CommandHandler(controller, feedback)
    voice_input = VoiceInput(feedback)

    try:
        while True:
            command = voice_input.listen_for_command()

            if command is None:
                continue

            command = command.strip().lower()

            if command in {"exit", "exit assistant", "quit"}:
                print("\nLIVE TEST FINISHED.")
                break

            handler.handle(command)

    except KeyboardInterrupt:
        print("\nLive test stopped.")

    finally:
        print("\nLive multimedia testing ended.")


if __name__ == "__main__":
    main()
