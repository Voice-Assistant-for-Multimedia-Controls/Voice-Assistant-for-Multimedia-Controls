
import speech_recognition as sr

recognizer = sr.Recognizer()

try:
    with sr.Microphone() as source:
        print("Adjusting for background noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)

        print("Speak now: say 'play music'.")
        audio = recognizer.listen(source, timeout=8, phrase_time_limit=5)

    print("Audio captured. Recognizing speech...")
    command = recognizer.recognize_google(audio)
    print("Recognized command:", command)

except sr.WaitTimeoutError:
    print("No speech detected. Check your microphone.")
except sr.UnknownValueError:
    print("Speech captured, but speech was unclear.")
except sr.RequestError as error:
    print("Speech recognition service error:", error)
except Exception as error:
    print("Microphone test failed:", error)
