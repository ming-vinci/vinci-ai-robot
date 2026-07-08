import time
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
        print("\n=== VoiceAssistant listen_once profiling ===")
        total_start = time.perf_counter()

        start = time.perf_counter()
        audio_path = self.recorder.record_to_file(
            output_path="data/audio/input.wav",
            duration_seconds=duration_seconds,
        )
        record_time = time.perf_counter() - start
        print(f"Record audio: {record_time:.2f}s")

        start = time.perf_counter()
        user_text = self.asr.transcribe(audio_path)
        asr_time = time.perf_counter() - start
        print(f"ASR transcribe: {asr_time:.2f}s")

        total_time = time.perf_counter() - total_start
        print(f"Total listen_once time: {total_time:.2f}s")
        print(f"User said: {user_text}")

        return user_text

    def respond_once(self, duration_seconds: int = 5) -> str:
        print("\n=== VoiceAssistant respond_once profiling ===")
        total_start = time.perf_counter()

        start = time.perf_counter()
        audio_input_path = self.recorder.record_to_file(
            output_path="data/audio/input.wav",
            duration_seconds=duration_seconds,
        )
        record_time = time.perf_counter() - start
        print(f"Record audio: {record_time:.2f}s")

        start = time.perf_counter()
        user_text = self.asr.transcribe(audio_input_path)
        asr_time = time.perf_counter() - start
        print(f"ASR transcribe: {asr_time:.2f}s")
        print(f"User said: {user_text}")

        start = time.perf_counter()
        answer = self.robot.chat(user_text)
        llm_time = time.perf_counter() - start
        print(f"Robot / LLM chat: {llm_time:.2f}s")
        print(f"Robot answer: {answer}")

        start = time.perf_counter()
        audio_output_path = self.tts.synthesize(
            answer,
            "data/audio/output.wav",
        )
        tts_time = time.perf_counter() - start
        print(f"TTS synthesize: {tts_time:.2f}s")

        start = time.perf_counter()
        self.player.play(audio_output_path)
        play_time = time.perf_counter() - start
        print(f"Play audio: {play_time:.2f}s")

        total_time = time.perf_counter() - total_start
        print(f"Total respond_once time: {total_time:.2f}s")

        return answer