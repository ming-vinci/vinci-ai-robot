import wave
import time
import pyaudio
from pathlib import Path
import subprocess
import struct
import math


def rms_16bit_mono(data: bytes) -> float:
    sample_count = len(data) // 2
    if sample_count == 0:
        return 0.0

    samples = struct.unpack("<" + "h" * sample_count, data)
    square_sum = sum(sample * sample for sample in samples)
    return math.sqrt(square_sum / sample_count)


class AudioRecorder:
    def __init__(
        self,
        device: str = "plughw:2,0",
        input_device_index: int | None = None,
        sample_rate: int = 48000,
        channels: int = 1,
        audio_format: str = "S16_LE",
    ):
        self.device = device
        self.input_device_index = input_device_index
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

    def record_until_silence(
        self,
        output_path: str,
        silence_threshold: int = 500,
        silence_duration: float = 1.0,
        max_record_seconds: float = 10.0,
        sample_rate: int = 16000,
        chunk_size: int = 1024,
    ) -> str:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        audio = pyaudio.PyAudio()

        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            input_device_index=self.input_device_index,
            frames_per_buffer=chunk_size,
        )

        print("Listening... speak now.")

        frames = []
        silence_start = None
        start_time = time.perf_counter()
        has_spoken = False

        try:
            while True:
                data = stream.read(chunk_size, exception_on_overflow=False)
                frames.append(data)

                volume = rms_16bit_mono(data)

                if volume > silence_threshold:
                    has_spoken = True
                    silence_start = None
                else:
                    if has_spoken:
                        if silence_start is None:
                            silence_start = time.perf_counter()

                        silence_time = time.perf_counter() - silence_start
                        if silence_time >= silence_duration:
                            print("Detected silence. Stop recording.")
                            break

                elapsed = time.perf_counter() - start_time
                if elapsed >= max_record_seconds:
                    print("Max recording time reached.")
                    break

        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()

        with wave.open(str(output), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b"".join(frames))

        print(f"Saved recording to {output}")
        return str(output)