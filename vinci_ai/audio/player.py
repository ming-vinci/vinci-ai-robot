from pathlib import Path
import subprocess

from vinci_ai.config.settings import AUDIO_OUTPUT_DEVICE


class AudioPlayer:
    def __init__(self, device: str = AUDIO_OUTPUT_DEVICE):
        self.device = device

    def play(self, audio_path: str):
        path = Path(audio_path)

        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        command = [
            "aplay",
            "-D",
            self.device,
            str(path),
        ]

        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Audio playback failed: {e}") from e
        except FileNotFoundError as e:
            raise RuntimeError(
                "aplay was not found. Install ALSA utilities with: sudo apt install alsa-utils"
            ) from e