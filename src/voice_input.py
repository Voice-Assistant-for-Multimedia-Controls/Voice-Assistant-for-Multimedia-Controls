
"""Microphone input and speech-to-text for US-01."""

import logging

import speech_recognition as sr


logger = logging.getLogger(__name__)


class VoiceInput:
    """Capture spoken commands and convert them to text."""

    def __init__(self, feedback=None, device_index=1):
        self.feedback = feedback
        self.recognizer = sr.Recognizer()

        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 250
        self.recognizer.pause_threshold = 0.7
        self.recognizer.non_speaking_duration = 0.5

        self.microphone = sr.Microphone(
            device_index=device_index,
            sample_rate=44100
        )

        self.calibrated = False

    def _report_error(self, message):
        """Report errors without interrupting the listening loop."""
        if self.feedback and callable(
            getattr(self.feedback, "say", None)
        ):
            try:
                self.feedback.say(message)
                return
            except Exception:
                logger.exception("Feedback service failed")

        print(f"Assistant: {message}")

    def listen_for_command(self):
        """Listen once and return recognized text or None."""
        try:
            with self.microphone as source:

                if not self.calibrated:
                    print("Calibrating microphone. Please stay quiet...")

                    self.recognizer.adjust_for_ambient_noise(
                        source,
                        duration=1
                    )

                    self.calibrated = True

                print("Listening... speak a command.")

                audio = self.recognizer.listen(
                    source,
                    timeout=10,
                    phrase_time_limit=6
                )

            command = self.recognizer.recognize_google(
                audio,
                language="en-IN"
            )

            command = command.strip().lower()

            if not command:
                self._report_error(
                    "No command detected. Please try again."
                )
                return None

            print(f"You said: {command}")
            return command

        except sr.WaitTimeoutError:
            print("No speech detected. Listening again.")

        except sr.UnknownValueError:
            print("Speech unclear. Please speak clearly and try again.")

        except sr.RequestError as error:
            self._report_error(
                f"Speech recognition service unavailable: {error}"
            )

        except OSError as error:
            self._report_error(
                f"Microphone error: {error}"
            )

        except Exception as error:
            logger.exception("Unexpected voice input error")
            self._report_error(
                f"Voice input error: {error}"
            )

        return None
