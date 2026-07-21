from __future__ import annotations

import base64
import json
import mimetypes
from pathlib import Path
from textwrap import dedent

from vinci_ai.config.settings import ENABLE_LONG_TERM_MEMORY_UPDATE
from vinci_ai.llm.base import LLMProvider
from vinci_ai.memory_store import MemoryStore
from vinci_ai.prompts.system_prompt import SYSTEM_PROMPT
from vinci_ai.vision.camera.base import CameraProvider
from vinci_ai.vision.camera.factory import create_camera_provider


class Robot:
    """
    Main conversational robot.

    The robot supports:

    - Normal text conversation
    - Capturing a new image
    - Reusing the most recently captured image for follow-up questions
    - Short-term conversation history
    - Long-term user memory

    An LLM router decides whether each user message should be handled as:

    - text_only
    - capture_new_image
    - reuse_previous_image
    """

    ROUTE_TEXT_ONLY = "text_only"
    ROUTE_CAPTURE_NEW_IMAGE = "capture_new_image"
    ROUTE_REUSE_PREVIOUS_IMAGE = "reuse_previous_image"

    VALID_ROUTES = {
        ROUTE_TEXT_ONLY,
        ROUTE_CAPTURE_NEW_IMAGE,
        ROUTE_REUSE_PREVIOUS_IMAGE,
    }

    def __init__(
        self,
        llm_provider: LLMProvider,
        camera_provider: CameraProvider | None = None,
    ):
        self.llm = llm_provider
        self.system_prompt = SYSTEM_PROMPT

        # Use the supplied camera provider for testing or dependency
        # injection. Otherwise, create the configured camera provider
        # through the factory.
        self.camera = camera_provider or create_camera_provider()

        # Short-term conversation memory.
        self.history: list[dict] = []

        # The main answer request receives the last 10 conversation pairs.
        self.max_turns = 10

        # The router only needs the last 2 conversation pairs.
        self.router_turns = 2

        # Most recently captured image.
        #
        # This image can be sent to the LLM again when the user asks a
        # follow-up question about something the robot previously saw.
        self.latest_image_path: str | None = None

        # Long-term user memory.
        self.memory_store = MemoryStore()

    def chat(self, user_message: str) -> str:
        """
        Process one user message.

        The workflow is:

        1. Route the request.
        2. Build either a text request or multimodal request.
        3. Ask the main LLM for an answer.
        4. Store the text conversation in short-term history.
        5. Optionally update long-term memory.
        """
        user_message = user_message.strip()

        if not user_message:
            return "I didn't hear a question. Please try again."

        memory_text = self.memory_store.format_for_prompt()

        route = self.route_request(user_message)

        print(f"\n===== Request route: {route} =====")

        if route == self.ROUTE_CAPTURE_NEW_IMAGE:
            messages = self.build_new_image_messages(
                user_message=user_message,
                memory_text=memory_text,
            )

        elif route == self.ROUTE_REUSE_PREVIOUS_IMAGE:
            messages = self.build_previous_image_messages(
                user_message=user_message,
                memory_text=memory_text,
            )

        else:
            messages = self.build_text_messages(
                user_message=user_message,
                memory_text=memory_text,
            )

        answer = self.llm.chat(messages).strip()

        if not answer:
            answer = "I'm sorry, but I couldn't generate a response."

        self.add_to_history(
            user_message=user_message,
            assistant_answer=answer,
        )

        if ENABLE_LONG_TERM_MEMORY_UPDATE:
            self.update_long_term_memory(
                user_message=user_message,
                assistant_answer=answer,
            )

        return answer

    def route_request(self, user_message: str) -> str:
        """
        Use the LLM to decide how the current request should be handled.

        The router receives:

        - Whether a previous image is available
        - The most recent two conversation pairs
        - The current user message

        The router does not receive the image itself.
        """

        if (
            self.has_latest_image()
            and self.has_explicit_previous_image_reference(user_message)
        ):
            print(
                "Explicit previous-image reference detected. "
                "Forcing route: reuse_previous_image"
            )
            return self.ROUTE_REUSE_PREVIOUS_IMAGE

        if self.is_explicit_new_image_request(user_message):
            print(
                "Explicit current-vision request detected. "
                "Forcing route: capture_new_image"
            )
            return self.ROUTE_CAPTURE_NEW_IMAGE

        latest_image_available = self.has_latest_image()

        recent_history = self.history[
            -2 * self.router_turns :
        ]

        router_system_prompt = dedent("""
    You are a request router for an AI robot with a camera.

    Choose exactly one action:

    1. "text_only"
       Use for ordinary conversation that does not require visual
       information.

    2. "capture_new_image"
       Use when the user asks the robot to inspect what is currently
       in front of the camera.

       Examples:
       - "What do you see?"
       - "Look at this."
       - "What is in front of you?"
       - "Read this."
       - "Look again."
       - "Describe what you see now."

    3. "reuse_previous_image"
       Use when the user asks about the most recently captured image,
       including details that were not mentioned in the previous answer.

       Explicit previous-image references always require
       "reuse_previous_image".

       Examples:
       - "What is the environment in that image?"
       - "What else is in the picture?"
       - "What was behind the animal?"
       - "What color was it?"
       - "What did you see on the left?"
       - "Tell me more about that photo."
       - "Was there anything beside the walrus?"
       - "What was the background like?"

    Priority rules:

    - If the user explicitly refers to "that image", "the image",
      "that picture", "the picture", "that photo", "the photo",
      "what you saw", or another previously captured visual scene,
      choose "reuse_previous_image".

    - An explicit previous-image reference has priority over a general
      request to inspect visual details.

    - If the user asks "What do you see?", choose
      "capture_new_image", because this asks the robot to look now.

    - Use "reuse_previous_image" for follow-up questions whose meaning
      depends on the previous image or the previous visual answer.

    - Only prefer "capture_new_image" when the request is genuinely
      ambiguous and does not refer to the previous image.

    - Never choose "reuse_previous_image" when no previous image is
      available.

    - Do not answer the user's question.

    - Return valid JSON only, without markdown or explanation.

    Required response format:

    {
      "action": "reuse_previous_image"
    }
""").strip()

        router_messages: list[dict] = [
            {
                "role": "system",
                "content": router_system_prompt,
            },
            {
                "role": "system",
                "content": (
                    "A previously captured image is currently "
                    f"{'available' if latest_image_available else 'not available'}."
                ),
            },
            *recent_history,
            {
                "role": "user",
                "content": user_message,
            },
        ]

        try:
            raw_result = self.llm.chat(router_messages)

            route = self.parse_route_result(raw_result)

            if (
                route == self.ROUTE_REUSE_PREVIOUS_IMAGE
                and not latest_image_available
            ):
                print(
                    "Router requested the previous image, but no valid "
                    "previous image exists. Falling back to text_only."
                )
                return self.ROUTE_TEXT_ONLY

            return route

        except Exception as error:
            print(f"Request routing failed: {error}")
            print("Falling back to text_only.")

            return self.ROUTE_TEXT_ONLY

    def is_explicit_new_image_request(self, user_message: str) -> bool:
        normalized = user_message.strip().lower().rstrip("?!.")

        explicit_requests = {
            "what do you see",
            "what can you see",
            "look at this",
            "look again",
            "take another look",
            "describe what you see",
            "what is in front of you",
            "can you read this",
            "read this",
        }

        return normalized in explicit_requests
    
    def has_explicit_previous_image_reference(
        self,
        user_message: str,
    ) -> bool:
        message = user_message.lower()

        previous_image_references = (
            "that image",
            "the image",
            "that picture",
            "the picture",
            "that photo",
            "the photo",
            "previous image",
            "previous picture",
            "previous photo",
            "last image",
            "last picture",
            "last photo",
            "what you saw",
            "what did you see",
            "in the background",
        )

        return any(
            reference in message
            for reference in previous_image_references
        )

    def parse_route_result(self, raw_result: str) -> str:
        """
        Parse the router response and return one valid route.

        The preferred response is JSON:

        {
            "action": "capture_new_image"
        }

        A small amount of formatting tolerance is included in case the model
        wraps the JSON in a markdown code block or returns only the action name.
        """
        cleaned_result = raw_result.strip()

        if cleaned_result.startswith("```"):
            cleaned_result = self.remove_code_fence(cleaned_result)

        try:
            parsed_result = json.loads(cleaned_result)

            if not isinstance(parsed_result, dict):
                raise ValueError(
                    "Router response must be a JSON object."
                )

            action = str(
                parsed_result.get("action", "")
            ).strip().lower()

            if action not in self.VALID_ROUTES:
                raise ValueError(
                    f"Unknown router action: {action}"
                )

            return action

        except (json.JSONDecodeError, TypeError, ValueError) as error:
            # Tolerate a model returning only an action string instead
            # of the requested JSON object.
            normalized_result = cleaned_result.strip(
                "\"' \n\t"
            ).lower()

            if normalized_result in self.VALID_ROUTES:
                return normalized_result

            # Also tolerate short explanatory output containing exactly
            # one valid action name.
            matched_routes = [
                route
                for route in self.VALID_ROUTES
                if route in normalized_result
            ]

            if len(matched_routes) == 1:
                return matched_routes[0]

            raise ValueError(
                "Could not determine a valid route from the router "
                f"response: {raw_result!r}"
            ) from error

    @staticmethod
    def remove_code_fence(text: str) -> str:
        """
        Remove a simple Markdown code fence from model output.
        """
        lines = text.strip().splitlines()

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        return "\n".join(lines).strip()

    def build_text_messages(
        self,
        user_message: str,
        memory_text: str,
    ) -> list[dict]:
        """
        Build a normal text-only request for the main LLM.
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

    def build_new_image_messages(
        self,
        user_message: str,
        memory_text: str,
    ) -> list[dict]:
        """
        Capture a new image and build a multimodal request.

        The new image replaces the previously remembered image.
        """
        print("New visual request detected.")
        print("Capturing a new image...")

        image_path = self.camera.capture("latest.jpg")

        self.latest_image_path = str(image_path)

        print(f"Image captured: {self.latest_image_path}")
        print("Preparing image for analysis...")

        return self.build_messages_with_image(
            user_message=user_message,
            memory_text=memory_text,
            image_path=self.latest_image_path,
        )

    def build_previous_image_messages(
        self,
        user_message: str,
        memory_text: str,
    ) -> list[dict]:
        """
        Build a multimodal request using the most recently captured image.

        No new image is captured. The original image is sent to the LLM again
        together with the user's new follow-up question.
        """
        if not self.has_latest_image():
            print(
                "Previous-image route selected, but the image is "
                "not available. Using a text-only request."
            )

            self.latest_image_path = None

            return self.build_text_messages(
                user_message=user_message,
                memory_text=memory_text,
            )

        print("Visual follow-up detected.")
        print(
            "Reusing the most recently captured image: "
            f"{self.latest_image_path}"
        )

        return self.build_messages_with_image(
            user_message=user_message,
            memory_text=memory_text,
            image_path=self.latest_image_path,
        )

    def build_messages_with_image(
        self,
        user_message: str,
        memory_text: str,
        image_path: str | Path,
    ) -> list[dict]:
        """
        Build a multimodal request using an existing image file.

        The full conversation history remains text-only. The image is attached
        only to the current user message, preventing large Base64 image data
        from being stored and repeatedly duplicated in history.
        """
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

    def has_latest_image(self) -> bool:
        """
        Return True when the stored latest image path points to a valid,
        non-empty file.
        """
        if not self.latest_image_path:
            return False

        image_file = Path(self.latest_image_path)

        return (
            image_file.exists()
            and image_file.is_file()
            and image_file.stat().st_size > 0
        )

    def add_to_history(
        self,
        user_message: str,
        assistant_answer: str,
    ) -> None:
        """
        Store one text-only conversation pair in short-term memory.

        Base64 image data is never stored in history.
        """
        self.history.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        self.history.append(
            {
                "role": "assistant",
                "content": assistant_answer,
            }
        )

        # Keep the last 10 conversation pairs = 20 messages.
        self.history = self.history[
            -2 * self.max_turns :
        ]

    @staticmethod
    def image_to_data_url(image_path: str | Path) -> str:
        """
        Convert a local image file to a Base64 data URL.
        """
        image_file = Path(image_path)

        if not image_file.exists():
            raise FileNotFoundError(
                f"Image file does not exist: {image_file}"
            )

        if not image_file.is_file():
            raise ValueError(
                f"Image path is not a file: {image_file}"
            )

        if image_file.stat().st_size == 0:
            raise ValueError(
                f"Image file is empty: {image_file}"
            )

        mime_type, _ = mimetypes.guess_type(image_file.name)

        if mime_type is None:
            mime_type = "image/jpeg"

        encoded_image = base64.b64encode(
            image_file.read_bytes()
        ).decode("utf-8")

        return f"data:{mime_type};base64,{encoded_image}"

    def update_long_term_memory(
        self,
        user_message: str,
        assistant_answer: str,
    ) -> None:
        """
        Ask the LLM to update the user's stable long-term memories.
        """
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
- Examples include the user's name, preferences, favorite things,
  work context, long-term projects, and communication preferences.
- Remove duplicates.
- If the latest conversation updates or corrects an old memory,
  keep the newer information.
- Do not store temporary facts, one-time questions, visual scene details,
  or random conversation details.
- Do not store information about an image unless it reveals a stable,
  useful fact about the user.
- Do not store the assistant's own response unless it reveals something
  important about the user.
- Return valid JSON only.
- Do not include markdown.

Required format:

{
  "memories": [
    "The user's name is Ming."
  ]
}

If nothing should be remembered, return the current memories unchanged.
                """.strip(),
            },
            {
                "role": "user",
                "content": f"""
Current long-term memories:

{json.dumps(
    current_memories,
    ensure_ascii=False,
    indent=2,
)}

Latest user message:

{user_message}

Assistant response:

{assistant_answer}
                """.strip(),
            },
        ]

        try:
            raw_result = self.llm.chat(
                memory_update_messages
            )

            parsed = json.loads(raw_result)

            updated_memories = parsed.get(
                "memories",
                [],
            )

            if not isinstance(updated_memories, list):
                raise ValueError(
                    "The memory update response must contain a "
                    "'memories' list."
                )

            cleaned_memories = [
                str(memory).strip()
                for memory in updated_memories
                if str(memory).strip()
            ]

            self.memory_store.save(cleaned_memories)

            print(
                "\n===== Long-term memory updated ====="
            )

            for memory in cleaned_memories:
                print(f"- {memory}")

        except (
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ) as error:
            print(
                "Long-term memory update returned an invalid "
                f"response: {error}"
            )

        except Exception as error:
            print(
                f"Long-term memory update failed: {error}"
            )

    def reset_history(self) -> None:
        """
        Clear short-term conversation history and forget the most
        recently captured image.

        Long-term memory is not deleted.
        """
        self.history = []
        self.latest_image_path = None

        print(
            "Short-term conversation and visual history cleared."
        )