"""Interactive command-line Somali assistant."""

from __future__ import annotations

from .model import ModelConfigurationError, ModelRequestError, OpenAIResponsesAdapter
from .pipeline import ConversationSession, SomaliAssistant


def main() -> int:
    try:
        model = OpenAIResponsesAdapter.from_env()
    except ModelConfigurationError as exc:
        print(f"Configuration error: {exc}")
        return 2

    assistant = SomaliAssistant(model)
    session = ConversationSession(assistant)

    print("Somali AI v0.1 — qor fariin Somali ama English.")
    print("Commands: /clear, /quit")
    while True:
        try:
            user_text = input("\nAdiga> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        if not user_text:
            continue
        if user_text in {"/quit", "/exit"}:
            return 0
        if user_text == "/clear":
            session.clear()
            print("Wadahadalkii waa la nadiifiyey.")
            continue

        try:
            result = session.ask(user_text)
        except (ModelRequestError, RuntimeError, ValueError) as exc:
            print(f"Khalad: {exc}")
            continue

        print(f"AI> {result.text}")


if __name__ == "__main__":
    raise SystemExit(main())
