from pathlib import Path

from openai import OpenAI

from vinci_ai.config.settings import OPENAI_API_KEY, TTS_MODEL, TTS_STYLE, TTS_VOICE
from vinci_ai.tts.base import TTSProvider


class OpenAITTSProvider(TTSProvider):
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = TTS_MODEL
        self.voice = TTS_VOICE

    def synthesize(self, text: str, output_path: str) -> str:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with self.client.audio.speech.with_streaming_response.create(
            model=self.model,
            voice=self.voice,
            input=text,
            instructions=TTS_STYLE,
            response_format="wav",
        ) as response:
            response.stream_to_file(str(output))

        return str(output)