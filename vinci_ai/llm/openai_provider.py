# vinci_ai/llm/openai_provider.py
from openai import OpenAI
from vinci_ai.llm.base import LLMProvider
from vinci_ai.config.settings import OPENAI_API_KEY, LLM_MODEL


class OpenAIProvider(LLMProvider):
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def chat(self, messages: list[dict]) -> str:
        response = self.client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
        )
        return response.choices[0].message.content