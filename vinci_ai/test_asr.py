from vinci_ai.audio.recorder import AudioRecorder
from vinci_ai.asr.factory import create_asr_provider


def main():
    recorder = AudioRecorder(
        device="plughw:2,0",
        sample_rate=16000,
        channels=1,
    )

    audio_path = recorder.record_to_file(
        output_path="data/audio/test.wav",
        duration_seconds=5,
    )

    asr = create_asr_provider()

    text = asr.transcribe(audio_path)

    print()
    print("========== Transcription ==========")
    print(text)
    print("===================================")


if __name__ == "__main__":
    main()