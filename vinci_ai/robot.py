from __future__ import annotations

import base64
import json
import mimetypes
from pathlib import Path

from vinci_ai.config.settings import ENABLE_LONG_TERM_MEMORY_UPDATE
from vinci_ai.prompts.system_prompt import SYSTEM_PROMPT
from vinci_ai.llm.base import LLMProvider
from vinci_ai.memory_store import MemoryStore
from vinci_ai.vision.camera import RaspberryPiCamera


class Robot:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
        self.system_prompt = SYSTEM_PROMPT
        self.camera = RaspberryPiCamera()

        # Short-term memory
        self.history: list[dict] = []
        self.max_turns = 10
        
        # Long-term memory
        self.memory_store = MemoryStore()

    def chat(self, user_message: str) -> str:
        """
        Send either a normal text request or a vision request.

        Vision is activated when the user's message contains one of
        the supported camera-related phrases.
        """
        memory_text = self.memory_store.format_for_prompt()

        if self.should_use_vision(user_message):
            messages = self.build_vision_messages(user_message, memory_text)
        else:
            messages = self.build_text_messages(user_message, memory_text)

        answer = self.llm.chat(messages)

        # Store text only in history.
        # Do not store the Base64 image because it is large and should
        # not be sent again in future requests.
        self.history.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        self.history.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        # Keep last 10 conversation pairs = 20 messages.
        self.history = self.history[-2 * self.max_turns:]

        if ENABLE_LONG_TERM_MEMORY_UPDATE:        
            self.update_long_term_memory(user_message, answer)

        return answer

    def build_text_messages(
        self,
        user_message: str,
        memory_text: str,
    ) -> list[dict]:
        """
        Build the normal text-only messages list.
        """
        return [
            {
                "role": "system",
                "content": self.system_prompt,
            },
            {
                "role": "system",
                "content": memory_text,
            },
            *self.history,
            {
                "role": "user",
                "content": user_message,
            },
        ]

    def build_vision_messages(
        self,
        user_message: str,
        memory_text: str,
    ) -> list[dict]:
        """
        Capture an image and build a multimodal messages list.
        """
        print("Vision request detected.")
        print("Capturing image...")

        image_path = self.camera.capture("latest.jpg")

        print(f"Image captured: {image_path}")
        print("Preparing image for analysis...")

        image_data_url = self.image_to_data_url(image_path)

        return [
            {
                "role": "system",
                "content": self.system_prompt,
            },
            {
                "role": "system",
                "content": memory_text,
            },
            *self.history,
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_message,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data_url,
                            "detail": "low",
                        },
                    },
                ],
            },
        ]

    @staticmethod
    def should_use_vision(user_message: str) -> bool:
        """
        Decide whether the user is asking the robot to use its camera.
        """
        normalized_message = user_message.lower().strip()

        vision_phrases = (
            "what do you see",
            "what can you see",
            "what did you see",
            "what have you seen",
            "tell me what you see",
            "tell me what you saw",
            "can you see",
            "look at this",
            "look at me",
            "look around",
            "take a picture",
            "take a photo",
            "use your camera",
            "describe this",
            "describe what you see",
            "describe what you saw",
            "what is this",
            "what's this",
            "what is in front of you",
            "what's in front of you",
            "who is in front of you",
            "read this",
        )

        return any(
            phrase in normalized_message
            for phrase in vision_phrases
        )

    @staticmethod
    def image_to_data_url(image_path: str) -> str:
        """
        Convert a local image file to a Base64 data URL.
        """
        image_file = Path(image_path)

        if not image_file.exists():
            raise FileNotFoundError(
                f"Image file does not exist: {image_path}"
            )

        if image_file.stat().st_size == 0:
            raise ValueError(
                f"Image file is empty: {image_path}"
            )

        mime_type, _ = mimetypes.guess_type(image_file.name)

        if mime_type is None:
            mime_type = "image/jpeg"

        encoded_image = base64.b64encode(
            image_file.read_bytes()
        ).decode("utf-8")

        return f"data:{mime_type};base64,{encoded_image}"

    def update_long_term_memory(self, user_message: str, assistant_answer: str) -> None:
        current_memories = self.memory_store.load()

        memory_update_messages = [
            {
                "role": "system",
                "content": """
                            You are responsible for maintaining long-term memory for a personal AI robot assistant.

                            You will receive:
                            1. The current long-term memories.
                            2. The latest user message.
                            3. The assistant's latest response.

                            Your job is to return the complete updated long-term memory list.

                            Rules:
                            - Keep stable, useful facts about the user.
                            - Examples: name, preferences, favorite things, work context, long-term projects, communication preferences.
                            - Remove duplicates.
                            - If the latest conversation updates or corrects an old memory, keep the newer information.
                            - Do not store temporary facts, one-time questions, or random conversation details.
                            - Do not store the assistant's own response unless it reveals something important about the user.
                            - Return valid JSON only.
                            - Do not include markdown.

                            Required format:
                            {
                            "memories": [
                                "The user's name is Ming."
                            ]
                            }

                            If nothing should be remembered, return the current memories unchanged.
                            """,
            },
            {
                "role": "user",
                "content": f"""
                            Current long-term memories:
                            {json.dumps(current_memories, ensure_ascii=False, indent=2)}

                            Latest user message:
                            {user_message}

                            Assistant response:
                            {assistant_answer}
                            """,
            },
        ]

        try:
            raw_result = self.llm.chat(memory_update_messages)
            parsed = json.loads(raw_result)

            updated_memories = parsed.get("memories", [])

            if isinstance(updated_memories, list):
                cleaned_memories = [
                    str(memory).strip()
                    for memory in updated_memories
                    if str(memory).strip()
                ]

                self.memory_store.save(cleaned_memories)

                print("\n===== Long-term memory updated =====")
                for memory in cleaned_memories:
                    print(f"- {memory}")

        except Exception as e:
            print(f"Long-term memory update failed: {e}")

    def reset_history(self):
        self.history = []
