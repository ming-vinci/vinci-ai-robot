from vinci_ai.audio.recorder import AudioRecorder
from vinci_ai.asr.factory import create_asr_provider
from vinci_ai.llm.factory import create_llm_provider
from vinci_ai.robot import Robot


def main():
    recorder = AudioRecorder(
        device="plughw:2,0",
        sample_rate=16000,
        channels=1,
    )

    asr = create_asr_provider()
    llm = create_llm_provider()

    robot = Robot(llm)

    audio_path = recorder.record_to_file(
        output_path="data/audio/test.wav",
        duration_seconds=5,
    )

    user_text = asr.transcribe(audio_path)

    print()
    print(f"You: {user_text}")
    print()

    answer = robot.chat(user_text)

    print("Robot:")
    print(answer)
    print()


if __name__ == "__main__":
    main()