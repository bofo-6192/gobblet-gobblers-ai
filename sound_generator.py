"""
Generate simple sound effects for the Gobblet Gobblers game.

This script creates basic WAV audio files using sine waves.
It avoids the need to download external audio files and ensures
the project remains self-contained.
"""

import wave
import math
import struct
import os


def create_sound(filename: str, frequency: int, duration: float) -> None:
    """
    Generate a simple sine wave sound and save it as a WAV file.

    Parameters:
    - filename: output file path
    - frequency: tone frequency in Hz
    - duration: length of the sound in seconds
    """
    sample_rate = 44100
    volume = 0.4
    frames = []

    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        value = volume * math.sin(2 * math.pi * frequency * t)
        frames.append(struct.pack("<h", int(value * 32767)))

    with wave.open(filename, "w") as file:
        file.setnchannels(1)      # mono audio
        file.setsampwidth(2)      # 16-bit audio
        file.setframerate(sample_rate)
        file.writeframes(b"".join(frames))


def main() -> None:
    """
    Create all required game sound effects.
    """
    os.makedirs("sounds", exist_ok=True)

    create_sound("sounds/click.wav", 800, 0.05)
    create_sound("sounds/place.wav", 400, 0.1)
    create_sound("sounds/win.wav", 600, 0.3)

    print("Sound files generated successfully!")


if __name__ == "__main__":
    main()