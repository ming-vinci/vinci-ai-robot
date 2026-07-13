from __future__ import annotations

import base64
import mimetypes
from pathlib import Path

from vinci_ai.prompts.system_prompt import SYSTEM_PROMPT
from vinci_ai.llm.base import LLMProvider
from vinci_ai.vision.camera import RaspberryPiCamera


class Robot:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
        self.system_prompt = SYSTEM_PROMPT
        self.history: list[dict] = []
        self.max_turns = 10
        self.camera = RaspberryPiCamera()

    def chat(self, user_message: str) -> str:
        """
        Send either a normal text request or a vision request.

        Vision is activated when the user's message contains one of
        the supported camera-related phrases.
        """
        if self.should_use_vision(user_message):
            messages = self.build_vision_messages(user_message)
        else:
            messages = self.build_text_messages(user_message)

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

        return answer

    def build_text_messages(
        self,
        user_message: str,
    ) -> list[dict]:
        """
        Build the normal text-only messages list.
        """
        return [
            {
                "role": "system",
                "content": self.system_prompt,
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

    def reset_history(self):
        self.history = []