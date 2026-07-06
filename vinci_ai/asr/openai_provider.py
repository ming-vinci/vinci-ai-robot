from openai import OpenAI

from vinci_ai.asr.base import ASRProvider
from vinci_ai.config.settings import ASR_LANGUAGE, OPENAI_API_KEY


class OpenAIASRProvider(ASRProvider):
    def __init__(self, model: str = "gpt-4o-mini-transcribe"):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = model

    def transcribe(self, audio_path: str) -> str:
        with open(audio_path, "rb") as audio_file:
            result = self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                language=ASR_LANGUAGE,
            )

        return result.text