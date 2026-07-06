# vinci_ai/llm/base.py
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def chat(self, messages: list[dict]) -> str:
        pass