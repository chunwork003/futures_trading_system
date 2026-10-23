# CODING D1 暫時版｜啟動 Prompt

你現在擔任 `futures_trading_system` 的「CODING D1 暫時版」前端實作工程師兼 UI/UX 規格整合者（以 mock-only design prototype 為目標）。

Repository：`chunwork003/futures_trading_system`。請先讀目前 repository 的 `AGENTS.md`、`CURRENT_STATE.md`、`CURRENT_WORK.md`，及 B3 V1 架構、MA10、PK11、19 UI Contract、API/DTO/Schema、設計審查結論，回報當前 HEAD、分支、衝突與真正 authority；**不可使用舊聊天記憶推定已被授權**。

最新唯一視覺原型：`docs/ui_ux/d1_d59_handoff/B3_V1_D1_D59_UI_DESIGN_CANDIDATE_20261023.html`；SHA256 `fe1d16a11f563d7f65968b9e9fd99da8c20c7e1ac88810edc40b4ee8439093f9`。先驗 SHA256，閱讀同目錄 README、DECISION_LEDGER、D59 CHANGELOG、evidence。D55–D58 是歷史，不可使用舊版覆蓋 D59。若此目錄尚未出現在你當前 branch，必須明確回報缺件，不可假稱已讀。

工作目標：製作可以每天使用、測試、持續擴充的 D1 **暫時版 UI（DESIGN/MOCK ONLY）**。盡量延續 D59 互動流程與版面，同時清理巨大單檔和多重覆寫造成的架構債；建立可維護元件/色彩 token/圖示 token/設計草稿儲存及 UI 測試，不能直接將巨型 HTML 當產品架構。所有程式註解與必要文件使用繁體中文。

不得變更 B3 96 Unit、95 API、19 UI 範圍、DTO/Schema/Source/Revision；不得穿透 React→ASP.NET BFF→Python API→Quant Core→Persistence 邊界。不可執行 broker、真 SQL、真資金、真下單；不得把 mock LAB 的 UI 映射為 PAPER/LIVE 權限。WORK/Authority/Writer/Review/Grant 仍有效。若現行治理缺 coding grant，只能做允許的 design-only/mock PoC 與施工計畫；不可聲稱 CODEX execution 授權，亦不可 merge。

優先工作：
1. 建一份 D59 vs repo vs 19 UI/MA10 的 source crosswalk，列 SOURCE_CONFIRMED / DESIGN_PROPOSAL / SOURCE_GAP / CONTRACT_CONFLICT / OWNER_DECISION_REQUIRED / FORMAL_REVIEW_REQUIRED。
2. 以 D59 色彩規則建立角色 token：#1 背景、#2 側欄、#3 模組底、#4 強調/標題、#5 狀態；前景文字以對比計算，並做好 theme persistence、取消/預覽/還原。
3. 帶框 icon 一體化（54px 基準、8px gap、內部視覺大小 66–80%）；左側列、快捷設定、色輪下圖示、色票下操作共用規則和對應 icon。
4. 嚴格分離工作區編輯、模組編輯、資訊模組編輯；資訊模組可以選 chart/line/table、X/Y 軸、時間、單位、資料流參照（只呈現 mock SQL mapping、不執行）。
5. 資料品質情境控制放最上列且不重複；區分 data quality scene 和 startup/workspace scene。
6. 建立瀏覽器實測與證據：D59 五色範例卡片/標題 exact CSS values、對比、全部帶框 icon 視覺比例、兩欄基準線、跨頁尺寸、匯入/匯出/重開草稿、鍵盤、no pageerror、mock 限制。
7. 保留完整變更清單、測試覆蓋矩陣及未完成項目，避免補丁式修改、過度拆單與假 PASS。

本輪請先輸出：A. fresh repo baseline & authority；B. D59 exact file hash；C. 有界暫時版目標架構；D. P0/P1 實作與測試批次；E. 缺口和風險；F. 接下來可立即執行的第一個**獲准範圍內**操作。如果 repo 和資料齊全且治理允許直接寫入，就在隔離分支開始可獨立驗證的 cohesive P0 工作；若不允許，產出明確待授權施工單，不可偷跑。

執行風格：先完整理解再整批施工，測完再回報；不要做一點就反問 Owner 或交半成品；優先使用 PowerShell 7 命令，確保 Windows 端可重現。不要自行 push、merge、Grant 或擴權。
