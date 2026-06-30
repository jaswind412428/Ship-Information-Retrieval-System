# GitHub 最簡易用法

這份文件是給完全沒用過 Git / GitHub 的小組成員看的。

先記住一句話：

```text
Git = 程式碼存檔工具
GitHub = 大家共同放程式碼的雲端空間
```

## 1. 小組合作最簡單規則

如果大家都是新手，先不要用太複雜的 branch。

第一版建議：

```text
一個共同 GitHub repo
每個人只改自己的資料夾
每天開始前先 pull
做完後 commit + push
```

例如資料夾分工：

```text
src/
├─ LangChain/      LangChain 組
├─ LangGraph/      LangGraph 組
├─ Retriever/      向量檢索組
├─ Reranker/       排序組
├─ API/            後端 API 組
└─ UI/             前端組
```

最重要的原則：

```text
不要亂改別人的資料夾。
```

## 2. 先確認有沒有 Git

打開 PowerShell，輸入：

```powershell
git --version
```

如果看到類似：

```text
git version 2.xx.x
```

代表已經安裝 Git。

如果顯示找不到 git，就要先安裝 Git。

## 3. 第一次下載專案

由一位同學建立 GitHub repository 後，大家用：

```powershell
git clone GitHub網址
```

例如：

```powershell
git clone https://github.com/帳號/專案名稱.git
```

下載後進入資料夾：

```powershell
cd 專案名稱
```

## 4. 每次開始寫程式前

一定先更新：

```powershell
git pull
```

意思是：

```text
把 GitHub 上別人最新的改動抓下來。
```

這可以減少檔案衝突。

## 5. 看自己改了什麼

```powershell
git status
```

它會顯示哪些檔案被新增、修改或刪除。

## 6. 把改動加入準備存檔區

如果確定這些改動都要存：

```powershell
git add .
```

意思是：

```text
把目前資料夾裡所有改動加入準備存檔區。
```

如果只想加入某個檔案：

```powershell
git add 檔案路徑
```

例如：

```powershell
git add src/LangGraph/router.py
```

## 7. 建立存檔點

```powershell
git commit -m "簡短描述這次做了什麼"
```

例如：

```powershell
git commit -m "新增 LangGraph router"
```

commit 可以想成：

```text
建立一個正式存檔點。
```

## 8. 上傳到 GitHub

```powershell
git push
```

意思是：

```text
把自己的 commit 上傳到 GitHub。
```

## 9. 最常用的完整流程

每次做事大概照這樣：

```powershell
git pull
git status
git add .
git commit -m "這次完成的內容"
git push
```

例如：

```powershell
git pull
git status
git add .
git commit -m "完成 rerank 節點紀錄"
git push
```

## 10. 小組新手安全守則

1. 每次開始前一定先 `git pull`。
2. 每個人只改自己負責的資料夾。
3. 不要直接刪別人的檔案。
4. 每完成一小段就 commit。
5. commit message 要寫人看得懂的內容。
6. push 前先 `git status` 看一下。
7. 如果出現 conflict，不要亂按，先問組員或助教。

## 11. 常見問題

### 問題 1：我可以直接把檔案丟給組長嗎？

可以，但不建議。

因為組長會很痛苦，而且很容易覆蓋別人的程式。

比較好的方式是：

```text
大家都用 GitHub 上傳自己的改動。
```

### 問題 2：我不小心改到別人的檔案怎麼辦？

先不要 push。

輸入：

```powershell
git status
```

看你改了哪些檔案，再跟組員確認。

### 問題 3：什麼是 commit？

commit 就是一次存檔。

例如：

```text
完成 router
完成 rerank
修正 JSON 記錄
```

每個 commit 都是一個可以追蹤的版本。

### 問題 4：什麼是 push？

push 是把你的 commit 上傳到 GitHub。

### 問題 5：什麼是 pull？

pull 是把 GitHub 上別人的最新改動下載到你的電腦。

## 12. 一句話總結

```text
開始前 pull，
改完後 add、commit、push。
```

先學會這樣就夠用了。
