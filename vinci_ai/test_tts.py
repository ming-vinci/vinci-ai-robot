from vinci_ai.audio.player import AudioPlayer
from vinci_ai.tts.factory import create_tts_provider


def main():
    tts = create_tts_provider()
    player = AudioPlayer()

    text = "Hello Ming. This is Vinci AI Robot speaking through the Raspberry Pi."

    audio_path = tts.synthesize(
        text=text,
        output_path="data/audio/tts_test.wav",
    )

    print(f"Saved speech to: {audio_path}")

    player.play(audio_path)


if __name__ == "__main__":
    main()