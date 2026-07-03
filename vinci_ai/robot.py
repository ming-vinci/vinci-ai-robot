from vinci_ai.llm import OpenAIClient
from vinci_ai.prompts.system_prompt import SYSTEM_PROMPT


class Robot:
    def __init__(self):
        self.llm = OpenAIClient()
        self.system_prompt = SYSTEM_PROMPT
        self.history = []

    def chat(self, user_message: str) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.history,
            {"role": "user", "content": user_message},
        ]

        answer = self.llm.chat(messages)

        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": answer})

        return answer

    def reset_history(self):
        self.history = []