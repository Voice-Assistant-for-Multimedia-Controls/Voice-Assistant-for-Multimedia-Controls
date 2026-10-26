
"""Microphone input and speech-to-text for US-01."""

import speech_recognition as sr


class VoiceInput:
    """Capture spoken commands and convert them to text."""

    def __init__(self, feedback=None):
        self.feedback = feedback
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.microphone = sr.Microphone()
        self.calibrated = False

    def listen_for_command(self):
        """Listen once and return recognized text, or None if unclear."""
        try:
            with self.microphone as source:
                if not self.calibrated:
                    print("Calibrating microphone. Please stay quiet...")
                    self.recognizer.adjust_for_ambient_noise(
                        source, duration=1
                    )
                    self.calibrated = True

                print("Listening... speak a command.")
                audio = self.recognizer.listen(
                    source,
                    timeout=7,
                    phrase_time_limit=5,
                )

            command = self.recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.strip().lower()

        except sr.WaitTimeoutError:
            print("No speech detected. Try again.")
        except sr.UnknownValueError:
            print("Speech unclear. Please try again.")
        except sr.RequestError:
            print("Speech recognition service unavailable.")
        except OSError as error:
            print(f"Microphone error: {error}")

        return None
