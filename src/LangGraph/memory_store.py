"""將 LangGraph State 寫入本機 JSON 紀錄檔。"""

from __future__ import annotations

import json
from pathlib import Path

from LangGraph.states import GraphState, GraphStatus, NodeName, NodeRecord


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MEMORY_FILE = PROJECT_ROOT / "memory" / "chat_records.json"


def load_chat_records(memory_file: Path = DEFAULT_MEMORY_FILE) -> list[GraphState]:
    """讀取 JSON 對話紀錄；如果檔案不存在就回傳空清單。"""

    if not memory_file.exists():
        return []

    content = memory_file.read_text(encoding="utf-8-sig").strip()
    if not content:
        return []

    records = json.loads(content)
    if not isinstance(records, list):
        raise ValueError(f"JSON 紀錄檔格式錯誤，應該是 list：{memory_file}")

    return records


def save_chat_records(
    records: list[GraphState],
    memory_file: Path = DEFAULT_MEMORY_FILE,
) -> None:
    """將對話紀錄寫回 JSON 檔案。"""

    memory_file.parent.mkdir(parents=True, exist_ok=True)
    memory_file.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def upsert_chat_record(
    state: GraphState,
    memory_file: Path = DEFAULT_MEMORY_FILE,
) -> None:
    """新增或更新同一筆對話紀錄。

    如果 JSON 裡已經有相同 id，就更新那筆紀錄。
    如果沒有，就新增一筆紀錄。
    """

    records = load_chat_records(memory_file)

    for index, record in enumerate(records):
        if record["id"] == state["id"]:
            records[index] = state
            save_chat_records(records, memory_file)
            return

    records.append(state)
    save_chat_records(records, memory_file)


def append_node_record(
    state: GraphState,
    node: NodeName,
    status: GraphStatus,
    data: dict[str, object],
) -> GraphState:
    """在 state 裡追加一筆節點紀錄。"""

    node_record: NodeRecord = {
        "node": node,
        "status": status,
        "data": data,
    }
    state.setdefault("node_records", []).append(node_record)
    return state
