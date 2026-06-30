"""
階段 3：查詢改寫（Multi-Query）。
用 GPT-5.5 把使用者問句改寫成 2~3 個不同角度的子查詢，
並特別要求包含英文版本，解決「中文查詢撈不到英文文件」的跨語言問題。
"""
import json
import config
from openai import OpenAI

client = OpenAI(api_key=config.OPENAI_API_KEY)


def rewrite(question, n=3):
    """把原始問句改寫成 n 個子查詢（含原文 + 中英文擴展）。

    回傳 list，第一個一定是原始問句，後面是改寫的子查詢。
    若改寫失敗，至少回傳原始問句，不影響檢索。
    """
    system_prompt = (
        "你是一個檢索查詢改寫器。使用者的文件庫是中英文混合的造船工程資料"
        "（含英文教科書與中文法規）。請把使用者的問題改寫成數個不同角度的檢索子查詢，"
        "以擴大召回範圍。要求：\n"
        "1. 一定要同時包含中文與英文版本的查詢（因為文件有中英文兩種語言）。\n"
        "2. 使用該領域的專業術語（例如把『功能原理』對應到 work-energy principle）。\n"
        "3. 只輸出一個 JSON 陣列，格式如 [\"查詢1\", \"查詢2\", \"查詢3\"]，不要任何其他文字。"
    )
    user_prompt = f"請把這個問題改寫成 {n} 個檢索子查詢：{question}"

    try:
        resp = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        raw = resp.choices[0].message.content.strip()
        # 去掉可能的 ```json ``` 包裹
        raw = raw.replace("```json", "").replace("```", "").strip()
        subqueries = json.loads(raw)
        if not isinstance(subqueries, list):
            raise ValueError("改寫結果不是陣列")
    except Exception as e:
        print(f"  ⚠ 查詢改寫失敗（{e}），改用原始問句")
        return [question]

    # 確保原始問句也在裡面（去重）
    queries = [question] + [q for q in subqueries if q != question]
    print(f"  ✓ 查詢改寫：{queries}")
    return queries
