from vinci_ai.audio.recorder import AudioRecorder
from vinci_ai.audio.player import AudioPlayer

from vinci_ai.asr.factory import create_asr_provider
from vinci_ai.llm.factory import create_llm_provider
from vinci_ai.tts.factory import create_tts_provider

from vinci_ai.robot import Robot
from vinci_ai.voice_assistant import VoiceAssistant


def main():

    recorder = AudioRecorder(
        device="plughw:2,0",
        input_device_index=1,
        sample_rate=48000,
    )

    player = AudioPlayer()

    asr = create_asr_provider()

    llm = create_llm_provider()

    tts = create_tts_provider()

    robot = Robot(llm)

    assistant = VoiceAssistant(
        recorder=recorder,
        player=player,
        asr_provider=asr,
        tts_provider=tts,
        robot=robot,
    )

    assistant.run_forever()


if __name__ == "__main__":
    main()