from vinci_ai.audio.recorder import AudioRecorder
from vinci_ai.asr.base import ASRProvider
from vinci_ai.robot import Robot


class VoiceAssistant:
    def __init__(
        self,
        recorder: AudioRecorder,
        asr_provider: ASRProvider,
        robot: Robot,
    ):
        self.recorder = recorder
        self.asr = asr_provider
        self.robot = robot

    def listen_once(self, duration_seconds: int = 5) -> str:
        audio_path = self.recorder.record_to_file(
            output_path="data/audio/input.wav",
            duration_seconds=duration_seconds,
        )

        user_text = self.asr.transcribe(audio_path)
        return user_text

    def respond_once(self, duration_seconds: int = 5) -> str:
        user_text = self.listen_once(duration_seconds)

        print()
        print(f"You: {user_text}")
        print()

        answer = self.robot.chat(user_text)

        print("Robot:")
        print(answer)
        print()

        return answer