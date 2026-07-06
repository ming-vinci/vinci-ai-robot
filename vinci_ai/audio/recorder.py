from pathlib import Path
import subprocess


class AudioRecorder:
    def __init__(
        self,
        device: str = "plughw:2,0",
        sample_rate: int = 16000,
        channels: int = 1,
        audio_format: str = "S16_LE",
    ):
        self.device = device
        self.sample_rate = sample_rate
        self.channels = channels
        self.audio_format = audio_format

    def record_to_file(self, output_path: str, duration_seconds: int = 5) -> str:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        command = [
            "arecord",
            "-D", self.device,
            "-f", self.audio_format,
            "-r", str(self.sample_rate),
            "-c", str(self.channels),
            "-d", str(duration_seconds),
            str(output),
        ]

        print(f"Recording for {duration_seconds} seconds...")
        print("Please speak now.")

        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Audio recording failed: {e}") from e
        except FileNotFoundError as e:
            raise RuntimeError(
                "arecord was not found. Please install ALSA utilities with: "
                "sudo apt install alsa-utils"
            ) from e

        print(f"Saved recording to {output}")
        return str(output)

    def list_devices(self):
        subprocess.run(["arecord", "-l"], check=True)