from vinci_ai.audio.recorder import AudioRecorder
from vinci_ai.asr.factory import create_asr_provider
from vinci_ai.llm.factory import create_llm_provider
from vinci_ai.robot import Robot
from vinci_ai.voice_assistant import VoiceAssistant


def main():
    recorder = AudioRecorder(
        device="plughw:2,0",
        sample_rate=16000,
        channels=1,
    )

    asr_provider = create_asr_provider()
    llm_provider = create_llm_provider()

    robot = Robot(llm_provider)

    assistant = VoiceAssistant(
        recorder=recorder,
        asr_provider=asr_provider,
        robot=robot,
    )

    assistant.respond_once(duration_seconds=5)


if __name__ == "__main__":
    main()