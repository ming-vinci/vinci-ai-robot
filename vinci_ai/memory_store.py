import json
from pathlib import Path


class MemoryStore:
    def __init__(self, memory_path: str = "data/memory/memory.json"):
        self.memory_path = Path(memory_path)
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.memory_path.exists():
            self.save([])

    def load(self) -> list[str]:
        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            return data.get("memories", [])

        except Exception:
            return []

    def save(self, memories: list[str]) -> None:
        data = {
            "memories": memories
        }

        with open(self.memory_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def format_for_prompt(self) -> str:
        memories = self.load()

        if not memories:
            return "No long-term memories yet."

        lines = ["Long-term memories about the user:"]
        for memory in memories:
            lines.append(f"- {memory}")

        return "\n".join(lines)
