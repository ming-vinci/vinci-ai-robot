from vinci_ai.config.settings import TTS_PROVIDER
from vinci_ai.tts.openai_provider import OpenAITTSProvider


def create_tts_provider():
    if TTS_PROVIDER == "openai":
        return OpenAITTSProvider()

    raise ValueError(f"Unsupported TTS provider: {TTS_PROVIDER}")