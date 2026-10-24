"""第1回: 素のLLMに会話履歴を保ちながら質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 講座に固有の既定質問から開始

質問を続けると、同じチャットの会話履歴を使って回答する。終了するには exit または quit を入力する。
ツールを持たない「素の」呼び出し。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai import errors
from google.genai.chats import Chat
from google.genai.types import GenerateContentResponse

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def print_usage(response: GenerateContentResponse) -> None:
    usage = response.usage_metadata
    if usage is None:
        print("[usage] token counts unavailable")
    else:
        print(
            f"[usage] input_tokens={usage.prompt_token_count} "
            f"output_tokens={usage.candidates_token_count}"
        )


def ask(chat: Chat, question: str) -> str:
    response = chat.send_message(question)
    print_usage(response)
    return response.text


def main() -> None:
    parser = argparse.ArgumentParser(description="会話履歴を保ちながら素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    print(f"[質問] {args.question}\n")
    try:
        client = genai.Client(api_key=get_api_key())
        chat = client.chats.create(model=MODEL)
        print(ask(chat, args.question))
        print("\n続けて質問できます。終了するには exit または quit を入力してください。")
        while True:
            try:
                question = input("\n質問: ").strip()
            except EOFError:
                print()
                break
            if question.lower() in {"exit", "quit"}:
                break
            if not question:
                continue
            print(f"[質問] {question}\n")
            print(ask(chat, question))
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
