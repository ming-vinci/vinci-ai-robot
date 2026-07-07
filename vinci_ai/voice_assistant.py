from vinci_ai.audio.recorder import AudioRecorder
from vinci_ai.audio.player import AudioPlayer
from vinci_ai.asr.base import ASRProvider
from vinci_ai.tts.base import TTSProvider
from vinci_ai.robot import Robot


class VoiceAssistant:

    def __init__(
        self,
        recorder: AudioRecorder,
        player: AudioPlayer,
        asr_provider: ASRProvider,
        tts_provider: TTSProvider,
        robot: Robot,
    ):
        self.recorder = recorder
        self.player = player
        self.asr = asr_provider
        self.tts = tts_provider
        self.robot = robot

    def listen_once(self, duration_seconds: int = 5) -> str:
        audio_path = self.recorder.record_to_file(
            output_path="data/audio/input.wav",
            duration_seconds=duration_seconds,
        )

        user_text = self.asr.transcribe(audio_path)
        return user_text

    def respond_once(self, duration_seconds: int = 5) -> str:
        user_text = self.listen_once()

        answer = self.robot.chat(user_text)

        audio_path = self.tts.synthesize(
            answer,
            "data/audio/output.wav"
        )

        self.player.play(audio_path)