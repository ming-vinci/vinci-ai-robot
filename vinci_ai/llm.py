from openai import OpenAI
from vinci_ai.config.settings import OPENAI_API_KEY, OPENAI_MODEL


class OpenAIClient:

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def chat(self, messages):
        response = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages
        )

        return response.choices[0].message.content