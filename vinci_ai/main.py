from vinci_ai.robot import Robot
from vinci_ai.llm.openai_provider import OpenAIProvider


def main():
    llm_provider = OpenAIProvider()
    robot = Robot(llm_provider)

    print("=== Vinci AI Robot ===")
    print("Type 'quit' or 'exit' to stop.")
    print("Type 'reset' to clear conversation history.")
    print()

    while True:
        text = input("You: ").strip()

        if text.lower() in ["quit", "exit"]:
            print("Goodbye!")
            break

        if text.lower() == "reset":
            robot.reset_history()
            print("Robot: Conversation history cleared.")
            print()
            continue

        if not text:
            continue

        answer = robot.chat(text)

        print("\nRobot:")
        print(answer)
        print()


if __name__ == "__main__":
    main()