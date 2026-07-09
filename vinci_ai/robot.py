from vinci_ai.llm.base import LLMProvider
from vinci_ai.prompts.system_prompt import SYSTEM_PROMPT


class Robot:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
        self.system_prompt = SYSTEM_PROMPT
        self.history = []
        self.max_turns = 10

    def chat(self, user_message: str) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.history,
            {"role": "user", "content": user_message},
        ]

        answer = self.llm.chat(messages)

        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": answer})

        # Keep last 10 conversation pairs = 20 messages
        self.history = self.history[-2 * self.max_turns:]

        return answer

    def reset_history(self):
        self.history = []
