# B3 D1 / D59 — 暫時版 UI Coding Handoff

**狀態：DESIGN_CANDIDATE / NOT_ACCEPTED / NO_RUNTIME_AUTHORIZATION**

## 唯一原型基準
`B3_V1_D1_D59_UI_DESIGN_CANDIDATE_20261023.html`，SHA256：`fe1d16a11f563d7f65968b9e9fd99da8c20c7e1ac88810edc40b4ee8439093f9`。
D55–D58 僅為歷史修正脈絡，**不作並列施工基準**；D59 本身亦非正式已驗收規格。

## 目的與安全邊界
D1 暫時版只實作 mock/offline UI，保留 19 UI、96 Unit、95 API 與既有 DTO/Schema/資料流語義；不可依外觀推導真實交易、資金、風險、後端 SQL、Shioaji 權限。React→ASP.NET BFF→Python API→Quant Core→Persistence 邊界不得改變。LAB/PAPER/LIVE 嚴格隔離；僅 mock data，不對券商或 DB 進行 I/O。

## D59 UI 必須保留
- 五色票：#1 背景、#2 側欄、#3 模組底、#4 強調/標題、#5 狀態；正文墨色自動選擇，且需逐表面確認對比。
- 參考樣本：背景 #2A0081，側欄 #B7E7FC，模組底 #FFD3F0，強調 #F5C700，狀態 #BA1650。**樣本只作驗證；不得將顏色硬編碼為唯一使用者配色**。
- 色輪下 icon 與色票下控制列：共同外框高度 54px、間距 8px；圖案目標佔框 66–80%；量測應以視覺 bounding box，不只 CSS font-size。
- 左側快捷圖示與其他帶框 icon 同比例且同功能 icon 映射。
- 全域頂列有資料情境（FRESH/PARTIAL/STALE/UNKNOWN）；次層不重複漂浮牌。此為來源品質狀態，不等同『啟動情境/工作區』設定。
- 三層分離：工作區編輯→模組編輯→資訊模組編輯；來源、圖表設定與版型分層持有。
- 不更改 19 UI 身份、API、交易權威。正式 source crosswalk 未驗證時列 SOURCE_GAP。

## 證據邊界與待辦
- 已有 Node 語法 PASS 與 Chromium/Playwright `set_content` 的狹義色彩連動、54px 框高、pageerror=0 測試紀錄。
- **未證明**：19 UI 全面回歸、所有 SVG 視覺包圍盒 66–80%、色盤存檔/還原、跨瀏覽器、正式契約符合性。
- 原 D59 是大型單檔分層補丁；正式暫時版施工前應抽取設計 tokens、共用 IconButton、ThemeStore、三層 editor boundary，避免繼續累加覆寫 CSS。

## 建議施工順序
1. 讀 AGENTS.md、CURRENT_STATE.md、CURRENT_WORK.md、B3_V1_ARCHITECTURE.md、MA10 10_WEB_UI_API.md、PK11 specs、UI contract/matrix；依實際 Git HEAD 核對。
2. 建立 UI contract/source crosswalk；列出原型對應、缺口與不可施工項目。
3. 在隔離分支製作 mock 暫時版，先做 tokens + icons + theme persistence，再建三層編輯器 shell。
4. D59 指定案例與一般主題各跑驗證：卡片背景、標題、文字對比、數值、工具列 54px、icon 視覺比、縮放、鍵盤、存取草稿還原。
5. 產出差異、證據、剩餘風險及 Owner review request；無授權不得 merge。

## 本資料包的發布
`Publish-D59-Handoff.ps1` 僅將文件提交至獨立 design handoff 分支；腳本不 merge、不動 master，不宣稱 WORK/CODEX Grant。
