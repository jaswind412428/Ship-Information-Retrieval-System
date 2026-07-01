"""
LLM 生成答案（RAG 的 "G"）。
根據檢索到的段落生成繁中答案，標來源頁碼，查無資料時 Fallback。

generate_answer_text：只回傳字串（給 API 用）
generate_answer：     回傳並印出（給命令列 main.py 用）
"""
from . import config
from openai import OpenAI

client = OpenAI(api_key=config.OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "你是一個造船工程知識助理。"
    "請只根據以下提供的參考資料回答問題，並在答案中標註引用的來源文件與頁碼。"
    "如果參考資料中沒有足夠資訊可以回答，就誠實說明「文件中查無相關資訊」，不要自行編造。"
    "請務必使用繁體中文回答，不可出現簡體字。"
)


def generate_answer_text(question, hits):
    """核心：根據檢索結果生成答案，只回傳字串（不印出）。"""
    context = "\n\n".join(
        [f"[資料{i+1}，來源 {h['source']} 第 {h['page']} 頁]\n{h['text']}"
         for i, h in enumerate(hits)]
    )
    user_prompt = f"參考資料：\n{context}\n\n問題：{question}"

    resp = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    return resp.choices[0].message.content


def generate_answer(question, hits):
    """命令列用：生成答案並印出。"""
    answer = generate_answer_text(question, hits)
    print("\n" + "─" * 60)
    print("🤖 LLM 生成答案：")
    print("─" * 60)
    print(answer)
    return answer
