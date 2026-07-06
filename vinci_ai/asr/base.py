from abc import ABC, abstractmethod


class ASRProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        pass