from vinci_ai.config.settings import ASR_PROVIDER
from vinci_ai.asr.openai_provider import OpenAIASRProvider


def create_asr_provider():
    if ASR_PROVIDER == "openai":
        return OpenAIASRProvider()

    raise ValueError(f"Unsupported ASR provider: {ASR_PROVIDER}")