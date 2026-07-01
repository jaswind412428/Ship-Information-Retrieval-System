r"""專案最終整合測試入口。

執行流程：

使用者輸入問題
→ Router 讀取短期記憶並判斷是否使用記憶
→ LangGraph：retrieve → rerank → generate
→ retrieve / generate 會呼叫 hsu RAG
→ 結果寫入 memory/chat_records.json

執行：

    C:\Users\User\miniconda3\python.exe main.py

單次測試：

    C:\Users\User\miniconda3\python.exe main.py --question "什麼是角動量守恆"
"""

from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
import io
import logging
import os
from pathlib import Path
import sys
from typing import Any
import warnings

from dotenv import load_dotenv


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")

warnings.filterwarnings("ignore")
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

load_dotenv(PROJECT_ROOT / ".env")


def is_verbose_output() -> bool:
    """從 .env 讀取 CLI 輸出模式。"""

    return os.getenv("VERBOSE_OUTPUT", "false").strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
        "on",
    }


def _get_node_record(state: dict[str, Any], node_name: str) -> dict[str, Any] | None:
    for record in state.get("node_records", []):
        if isinstance(record, dict) and record.get("node") == node_name:
            return record
    return None


def print_result(state: dict[str, Any]) -> None:
    """印出適合 demo / debug 的結果。"""

    from LangGraph.rag_adapter import format_sources

    docs = state.get("reranked_docs") or state.get("retrieved_docs") or []
    if not isinstance(docs, list):
        docs = []

    print()
    print("=" * 70)
    print("整合流程完成")
    print("=" * 70)
    print(f"id：{state.get('id')}")
    print(f"user_id：{state.get('user_id')}")
    print(f"thread_id：{state.get('thread_id')}")
    print(f"status：{state.get('status')}")
    print(f"原始問題：{state.get('original_question')}")
    print(f"送入 RAG 問題：{state.get('rag_question') or state.get('rewritten_question', '')}")
    print(f"是否使用記憶：{state.get('use_memory', '')}")

    print()
    print("[節點順序]")
    for index, record in enumerate(state.get("node_records", []), start=1):
        if not isinstance(record, dict):
            continue
        data = record.get("data") or {}
        message = data.get("message", "") if isinstance(data, dict) else ""
        print(f"{index}. {record.get('node')} / {record.get('status')}")
        if message:
            print(f"   {message}")

    print()
    print(f"[RAG docs 數量] {len(docs)}")
    sources = format_sources(docs)
    for index, source in enumerate(sources[:5], start=1):
        score = source.get("score")
        if isinstance(score, (int, float)):
            score_text = f"，score：{score:.4f}"
        else:
            score_text = ""
        print(f"{index}. {source.get('file')} 第 {source.get('page')} 頁{score_text}")

    retrieve_record = _get_node_record(state, "retrieve")
    if retrieve_record:
        data = retrieve_record.get("data") or {}
        if isinstance(data, dict) and data.get("error"):
            print()
            print("[Retrieve 錯誤]")
            print(data["error"])

    print()
    print("[AI 回答]")
    print(state.get("ai_answer", ""))
    print("=" * 70)
    print()


def print_simple_result(state: dict[str, Any]) -> None:
    """印出最簡化展示用結果。"""

    print()
    print("回覆：")
    print(state.get("ai_answer", ""))
    print()


def run_once(question: str, user_id: str, thread_id: str) -> None:
    verbose_output = is_verbose_output()

    if not verbose_output:
        console = sys.__stdout__

        def show_progress(event: str, payload: dict[str, Any] | None) -> None:
            if event == "router_end" and payload:
                print(f"重寫問題：{payload.get('rag_question') or payload.get('rewritten_question', '')}", file=console)
            elif event == "retrieve_start":
                print("查詢中...", file=console)
            elif event == "rerank_start":
                print("排序中...", file=console)
            elif event == "generate_start":
                print("生成中...", file=console)

        print(f"問題：{question}")
        hidden_output = io.StringIO()
        with redirect_stdout(hidden_output), redirect_stderr(hidden_output):
            from LangGraph.flow import run_chat_flow

            state = run_chat_flow(
                question=question,
                user_id=user_id,
                thread_id=thread_id,
                progress_callback=show_progress,
            )
        print_simple_result(state)
        return

    from LangGraph.flow import run_chat_flow

    state = run_chat_flow(
        question=question,
        user_id=user_id,
        thread_id=thread_id,
    )

    print_result(state)


def run_interactive(user_id: str, thread_id: str) -> None:
    verbose_output = is_verbose_output()
    print("Marine RAG + LangGraph 已啟動。")
    if verbose_output:
        print("輸出模式：詳細")
        print("流程：router → retrieve(hsu) → rerank → generate(hsu)")
    else:
        print("輸出模式：簡化")
    print("輸入問題後按 Enter；輸入 exit 或 quit 結束。")
    print()

    while True:
        question = input("你：").strip()
        if question.lower() in {"exit", "quit"}:
            print("結束整合測試。")
            break
        if not question:
            print("請先輸入問題。")
            continue

        run_once(question, user_id=user_id, thread_id=thread_id)


def main() -> None:
    parser = argparse.ArgumentParser(description="Marine RAG + LangGraph 整合測試。")
    parser.add_argument("--question", help="單次測試問題；不填則進入互動模式。")
    parser.add_argument("--user-id", default="demo-user", help="使用者 ID。")
    parser.add_argument("--thread-id", default="demo-thread", help="對話 ID。")
    args = parser.parse_args()

    if args.question:
        run_once(args.question, user_id=args.user_id, thread_id=args.thread_id)
    else:
        run_interactive(user_id=args.user_id, thread_id=args.thread_id)


if __name__ == "__main__":
    main()
