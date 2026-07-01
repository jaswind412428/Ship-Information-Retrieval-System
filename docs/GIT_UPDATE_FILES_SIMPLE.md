# 如何修改檔案並更新到 GitHub

這份文件給完全新手使用。

你只要記住一個固定流程：

```text
改檔案
→ git status
→ git add
→ git commit
→ git push
```

## 1. 開始修改前，先更新專案

每次開始寫程式前，先執行：

```powershell
git pull
```

意思是：

```text
先把 GitHub 上最新的版本下載到你的電腦。
```

這樣比較不會跟同學的程式衝突。

## 2. 修改檔案

直接用 VS Code 修改檔案即可。

例如你改了：

```text
src/LangGraph/nodes.py
```

或新增了：

```text
src/hsu/.gitkeep
```

改完後不要只按儲存就結束，還要用 Git 上傳。

## 3. 查看目前改了什麼

```powershell
git status
```

如果你看到：

```text
modified: 檔案名稱
```

代表這個檔案被修改過。

如果你看到：

```text
Untracked files
```

代表這是新檔案，Git 還沒開始追蹤它。

## 4. 把改動加入 Git

如果你要把所有改動都加入：

```powershell
git add .
```

如果你只想加入某個檔案：

```powershell
git add 檔案路徑
```

例如：

```powershell
git add src/LangGraph/nodes.py
```

如果是新增資料夾，資料夾裡要有檔案 Git 才會上傳。

空資料夾不會被 Git 追蹤，所以通常放：

```text
.gitkeep
```

例如：

```powershell
git add src/hsu/.gitkeep
```

## 5. 建立 commit

```powershell
git commit -m "描述這次改了什麼"
```

例如：

```powershell
git commit -m "Add hsu folder"
```

或：

```powershell
git commit -m "Update LangGraph rerank node"
```

commit 可以想成：

```text
在自己的電腦建立一個正式存檔點。
```

## 6. 推上 GitHub

```powershell
git push
```

意思是：

```text
把剛剛的 commit 上傳到 GitHub。
```

如果成功，GitHub 網頁上就會看到你的更新。

## 7. 最常用完整流程

每次改檔案都照這樣：

```powershell
git pull
git status
git add .
git commit -m "描述這次改了什麼"
git push
```

## 8. 如果 git push 顯示 Everything up-to-date

如果你看到：

```text
Everything up-to-date
```

但 GitHub 上沒有更新，通常代表你還沒有 commit。

請檢查：

```powershell
git status
```

如果還有檔案沒加入，就做：

```powershell
git add .
git commit -m "描述這次改了什麼"
git push
```

## 9. 如果新資料夾沒有出現在 GitHub

Git 不會上傳空資料夾。

請在資料夾裡放一個 `.gitkeep`：

```powershell
New-Item src\你的資料夾\.gitkeep
git add src\你的資料夾\.gitkeep
git commit -m "Add folder"
git push
```

## 10. 不要上傳的東西

以下東西不要上傳：

```text
.env
__pycache__/
memory/chat_records.json
src/hsu/config.py
src/hsu/data/
src/hsu/db/
```

這些已經寫在 `.gitignore` 裡。

如果你看到它們沒有出現在 `git status`，那是正常的。

## 11. 一句話記法

```text
pull 先更新
status 看狀態
add 加入改動
commit 本地存檔
push 上傳 GitHub
```

最常用指令：

```powershell
git pull
git status
git add .
git commit -m "Update files"
git push
```
