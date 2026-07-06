from vinci_ai.config.settings import LLM_PROVIDER
from vinci_ai.llm.openai_provider import OpenAIProvider
# from vinci_ai.llm.gemini_provider import GeminiProvider


def create_llm_provider():
    if LLM_PROVIDER == "openai":
        return OpenAIProvider()

    # elif LLM_PROVIDER == "gemini":
    #     return GeminiProvider()

    raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")