"""Run voice commands and optional webcam gesture controls concurrently."""

import threading

from src.command_handler import CommandHandler
from src.feedback_service import FeedbackService
from src.gesture_control import GestureControl
from src.gesture_mapping import GestureMapping
from src.multimedia_controller import MultimediaController
from src.voice_input import VoiceInput


def run_assistant(voice_input, handler):
    """Process commands continuously until an exit command is received."""
    print("Voice Assistant — Voice + Gesture Controls")
    print("Speak a command, or say 'exit' to stop.")

    while True:
        command = voice_input.listen_for_command()
        if command is None:
            continue

        if command.strip().lower() in {"exit", "stop", "quit"}:
            print("Assistant stopped.")
            break

        print(f"Recognized command: {command}")
        try:
            handler.handle(command)
        except NotImplementedError:
            print("This command's media action is not implemented yet.")


def run_gesture_controls(handler, feedback, stop_event):
    """Read webcam frames and dispatch recognized gestures."""
    import cv2

    gesture_control = GestureControl(camera_index=1)
    gesture_mapping = GestureMapping()
    try:
        gesture_control.start_camera()
        feedback.say(
            "Gesture controls enabled. Press Q in the camera window to disable them."
        )
        while not stop_event.is_set():
            ok, frame = gesture_control.camera.read()
            if not ok:
                feedback.say("Unable to read from webcam; gesture controls stopped.")
                break

            frame = cv2.flip(frame, 1)
            gesture = gesture_control.recognize_gesture(frame)
            if gesture:
                command = gesture_mapping.map_gesture(gesture)
                if command:
                    feedback.say(
                        f"Gesture detected: {gesture.replace('_', ' ')} -> {command}"
                    )
                    try:
                        handler.handle(command)
                    except NotImplementedError:
                        feedback.say(
                            f"'{command}' is mapped, but its multimedia action "
                            "has not been implemented by the team yet."
                        )

            if gesture_control.show_window:
                preview = gesture_control.draw_feedback(frame, gesture)
                cv2.imshow("Gesture Controls", preview)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    except Exception as error:
        feedback.say(f"Gesture controls unavailable: {error}")
    finally:
        gesture_control.close()
        stop_event.set()


def main():
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
        print("Assistant stopped.")
    finally:
        stop_event.set()
        gesture_thread.join(timeout=2)


if __name__ == "__main__":
    main()
