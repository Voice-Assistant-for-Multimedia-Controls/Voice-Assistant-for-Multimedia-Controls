
"""Run voice commands and webcam gesture controls concurrently."""

import threading

from src.command_handler import CommandHandler
from src.feedback_service import FeedbackService
from src.gesture_control import GestureControl
from src.gesture_mapping import GestureMapping
from src.multimedia_controller import MultimediaController
from src.voice_input import VoiceInput


def run_assistant(voice_input, handler):
    """Listen continuously for voice commands."""
    print("\n=== Voice Assistant: Voice + Gesture Controls ===")
    print("Commands: play music, pause music, resume, next song")
    print("Say 'exit assistant' or 'quit' to stop.\n")

    while True:
        try:
            command = voice_input.listen_for_command()

            if command is None:
                continue

            command = command.strip().lower()

            # Stop the assistant only when explicitly requested.
            # 'stop music' should be handled as a media command.
            if command in {"exit", "exit assistant", "quit"}:
                print("Assistant stopped.")
                break

            print(f"Recognized command: {command}")
            handler.handle(command)

        except KeyboardInterrupt:
            print("\nAssistant stopped.")
            break
        except NotImplementedError as error:
            print(f"Media action not implemented: {error}")
        except Exception as error:
            print(f"An error occurred: {error}")


def run_gesture_controls(handler, feedback, stop_event):
    """Read webcam frames and dispatch recognized gestures."""
    gesture_control = None

    try:
        import cv2

        gesture_control = GestureControl(camera_index=1)
        gesture_mapping = GestureMapping()

        gesture_control.start_camera()

        feedback.say(
            "Gesture controls enabled. "
            "Press Q in the camera window to disable them."
        )

        while not stop_event.is_set():
            ok, frame = gesture_control.camera.read()

            if not ok:
                feedback.say(
                    "Unable to read from webcam. Gesture controls stopped."
                )
                break

            frame = cv2.flip(frame, 1)
            gesture = gesture_control.recognize_gesture(frame)

            if gesture:
                command = gesture_mapping.map_gesture(gesture)

                if command:
                    feedback.say(
                        f"Gesture detected: "
                        f"{gesture.replace('_', ' ')} -> {command}"
                    )

                    try:
                        handler.handle(command)
                    except NotImplementedError:
                        feedback.say(
                            f"'{command}' is mapped, but its media action "
                            "has not been implemented yet."
                        )
                    except Exception as error:
                        feedback.say(f"Gesture command error: {error}")

            if gesture_control.show_window:
                preview = gesture_control.draw_feedback(frame, gesture)
                cv2.imshow("Gesture Controls", preview)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    except Exception as error:
        feedback.say(f"Gesture controls unavailable: {error}")

    finally:
        if gesture_control is not None:
            try:
                gesture_control.close()
            except Exception as error:
                print(f"Error closing gesture controls: {error}")

        stop_event.set()


def main():
    """Initialize and run voice and gesture controls."""
    feedback = FeedbackService()
    controller = MultimediaController()
    handler = CommandHandler(controller, feedback)
    voice_input = VoiceInput(feedback)

    stop_event = threading.Event()

    gesture_thread = threading.Thread(
        target=run_gesture_controls,
        args=(handler, feedback, stop_event),
        name="gesture-controls",
        daemon=True,
    )

    gesture_thread.start()

    try:
        run_assistant(voice_input, handler)

    except KeyboardInterrupt:
        print("\nAssistant stopped.")

    finally:
        stop_event.set()
        gesture_thread.join(timeout=2)


if __name__ == "__main__":
    main()
