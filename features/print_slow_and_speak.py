import time
import threading
from features.speak_and_play import speak_and_play


def print_slow_and_speak(message, delay=0.1):
    def print_slow(text, delay):
        print(text, flush=True)

    try:
        speech_thread = threading.Thread(target=speak_and_play, args=(message,), daemon=True)
        speech_thread.start()
    except Exception as exc:
        print(f"Voice playback failed for '{message}': {exc}", flush=True)

    print_slow(message, delay)
