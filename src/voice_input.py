
"""Microphone input and speech-to-text for US-01."""

import speech_recognition as sr


class VoiceInput:
    """Capture a spoken command and convert it to text."""

    def __init__(self, feedback=None):
     self.feedback = feedback
     self.recognizer = sr.Recognizer()
     self.microphone = sr.Microphone()

    def listen_for_command(self):
        """Listen once and return recognized text, or None if unclear."""
        try:
            with self.microphone as source:
                print("Adjusting for background noise...")
                self.recognizer.adjust_for_ambient_noise(
                    source, duration=0.5
                )
                print("Listening... speak a command.")
                audio = self.recognizer.listen(
                    source, timeout=5, phrase_time_limit=5
                )

            command = self.recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.strip().lower()

        except sr.WaitTimeoutError:
            print("No speech detected.")
        except sr.UnknownValueError:
            print("Speech was unclear.")
        except sr.RequestError:
            print("Speech recognition service unavailable.")
        except OSError as error:
            print(f"Microphone error: {error}")

        return None
