import cv2
import speech_recognition as sr


def detect_cameras(max_index: int = 10) -> list[int]:
    detected = []
    for index in range(max_index):
        camera = cv2.VideoCapture(index)
        if camera.isOpened():
            detected.append(index)
            camera.release()
    return detected


def main() -> int:
    microphones = sr.Microphone.list_microphone_names()
    cameras = detect_cameras()

    if not microphones:
        raise SystemExit("No microphone devices detected on this self-hosted runner.")

    if not cameras:
        raise SystemExit("No webcam/camera devices detected on this self-hosted runner.")

    print(f"Microphones detected: {len(microphones)}")
    print(f"Cameras detected: {len(cameras)}")
    print("Hardware prerequisites for live validation are available.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
