"""hsu 檢索模組設定說明。

目前設定範本已移到專案根目錄：

    config.example.py

請不要在這個資料夾內另外維護一份不同的設定，避免組員之間版本不一致。

使用 hsu 模組前，請在專案根目錄執行：

    Copy-Item config.example.py src/hsu/config.py

然後把 API Key、Token、Qdrant URL 等秘密資料填在根目錄 `.env`。

注意：

- `src/hsu/config.py` 是每個人自己的本機設定，已被 `.gitignore` 排除。
- `config.example.py` 放公開參數，例如模型名稱、TOP_K、chunk size。
- `.env` 放秘密資料，例如 OPENAI_API_KEY、QDRANT_API_KEY。
"""
