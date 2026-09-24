from __future__ import annotations

import os
import tempfile
import wave

import pygame
import sounddevice as sd
import pyttsx3
from pydub import AudioSegment


def save_audio_to_wav(audio, samplerate: int, filename: str) -> None:
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio.tobytes())


def record_audio(duration: float, samplerate: int = 16000):
    print("Listening to You Boss...")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype="int16")
    sd.wait()
    return recording.flatten()


def play_audio_file(file_path: str) -> None:
    if os.path.isfile(file_path):
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    else:
        print(f"Audio file not found: {file_path}")


def text_to_speech(text: str, filename: str) -> None:
    engine = pyttsx3.init()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_filename = temp_file.name
    engine.save_to_file(text, temp_filename)
    engine.runAndWait()
    audio = AudioSegment.from_wav(temp_filename)
    audio.export(filename, format="wav")
    os.remove(temp_filename)


def speak_and_play(prompt: str, temp_dir: str = "temp") -> None:
    os.makedirs(temp_dir, exist_ok=True)
    unique_filename = os.path.join(temp_dir, f"{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}_summary.wav")
    text_to_speech(prompt, unique_filename)
    play_audio_file(unique_filename)
