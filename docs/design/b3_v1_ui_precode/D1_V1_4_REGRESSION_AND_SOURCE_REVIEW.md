# B3 V1 D1 v1.4｜完整修正與互動驗收紀錄

**Status:** `DESIGN_CANDIDATE / OWNER_REVIEW_PENDING`; 與正式 Architecture / Runtime / WO / Coding Grant 完全分離。  
**日期：** 2026-10-20（Asia/Taipei）。  
**Pin：** accepted B3 source commit `9643bfc93a1631154be877536a1c91fc58df84be`。  
**迭代：** v1.3 完整版 → v1.4 一致性修正；保留 19 UI permanent IDs 與 MA10-U01~U06。  
**可操作原型：** `prototypes/B3_V1_D1_FullDashboard_Integrated_v1_4_CANDIDATE.html`。  
**原型 SHA-256：** `c829673122071acd1415d8023e64a183f7c0023eaa4ae56a1d7580fd3604bd1b`。

## 0. Human 確認與設計邊界

Human 明確選擇 **A：單一自訂模組只能綁定同一資料主體（DataSubjectRef），不同格子可以展示不同資料欄位／圖表方式**。本次以此建設一份獨立、無外部腳本／行情／Broker 連線的離線 HTML/JS 可互動設計原型。這份 HTML 是 Design Preview，不是產品 React/ASP.NET/Python 原始碼，也未授權任何正式持久化、服務端報表、跨帳戶聚合、策略/交易/風險下單。

## 1. D1-R14-01～10 acceptance matrix（瀏覽器原型範圍）

| 案例 | 結果 | 實際檢查內容 |
|---|---|---|
| D1-R14-01 | PASS | eight modules and no internal overflow |
| D1-R14-02 | PASS | asset height and six-slot pagination |
| D1-R14-03 | PASS | translucent flyout and Escape |
| D1-R14-04 | PASS | 24 icon picker and cancellation |
| D1-R14-05 | PASS | free-space workbench occupancy |
| D1-R14-06 | PASS | theme role colors and cancellation |
| D1-R14-07 | PASS | NxM region editor with >4 slots |
| D1-R14-08 | PASS | subject A, metric inspector appears on + |
| D1-R14-09 | PASS | layout draft Save/Cancel returns to settings |
| D1-R14-10 | PASS | data truth and type scale |
| D1-UX14-01 | PASS | financial chart breakdown tooltip |

**額外**：Playwright Chromium 無 uncaught JS 錯誤。Python 測試程式存於本輪工作區 `d1_v14_work/regression.py` 與 `extended.py`；機器化檢查詳細資料另存 Git JSON。原型測試通過不代表已驗證 B3 真實 DTO/API、權限、資料時點、Renderer License 或 Broker I/O。

## 2. 不同字體及 viewport 的視覺檢查

| Viewport / 字體 | DOM 驗收 | 檢查內容 |
|---|---|---|
| 1920x900_100% | PASS | 模組內溢出=False、整頁水平溢出=False、JS errors=0 |
| 1440x900_150% | PASS | 模組內溢出=False、整頁水平溢出=False、JS errors=0 |
| 1100x900_200% | PASS | 模組內溢出=False、整頁水平溢出=False、JS errors=0 |
| 840x900_150% | PASS | 模組內溢出=False、整頁水平溢出=False、JS errors=0 |
| 600x900_150% | PASS | 模組內溢出=False、整頁水平溢出=False、JS errors=0 |

額外正反例：PNG local import preview/rail = PASS；淺色面板 = PASS；文字與背景對比不足時套用拒絕 = PASS；UNKNOWN 的資金及資產數值都隱藏 = PASS。預設預覽數字完全合成，不是任何真實帳戶、策略或新聞證據。

## 3. 根本原因與替換方案

- **v1.3 四區塊上限**：改為 NxM 單元，允許每個有效 1×1 格建構獨立展示區塊；以 x/y/w/h 確認非重疊，在 6×2 建立 12 區塊通過。暫限制上限 12×6 以維持編輯器可用性與效能；這是 UX 範圍限制，不是原來四格寫死。
- **工作台缺空位操作**：改用 module instances 的實體位置 x/y/w/h、顯式佔用檢查和空格＋；刪除、移動、空格新增，需由使用者確認位置，不暗中 auto pack。
- **固定模組高度/空位**：使用共享 Module Card chrome、12-column grid row unit、每種資訊穩定的 slot capacity；資產和持倉 6 格/頁，不足以安全 placeholder 補齊，超過分頁。同尺寸頁籤切換不變高度。數值縮放 100/125/150/200%，大字於小視窗時 reflow 而非內層 scrolling。
- **自訂模組 Builder**：單一類別/主體、NxM 大小、按＋才出現右側資料/數字或圖形類型、合法區塊拖放及擴大。用類別到模組建立，再到工作台放置；不要求先選 S～XL。
- **快捷**：選中的 UI/子功能依類別歸組，半透明浮層不推擠主頁、Esc 關閉；內建 24 圖示並有＋本機 PNG/WebP 匯入（原始 SVG/外部 URI 無授權而拒絕）。設計與安全考量另列。
- **配色**：具角色色塊、調色輪及 HEX 編輯，滑鼠懸停才標示色碼（進入角色編輯顯示輸入欄），主體文字對比門檻 4.5:1。取消設定要能恢復。

## 4. 明確未完成 / 限制

| ID | 實際狀態 | 後續 Gate |
|---|---|---|
| GAP14-A | 原有八張模組共享**格線外框、標準容量、視覺狀態規範**；但各類金融展示依然由專用 presenter 畫圖，尚未證明全部已由一份 schema 驅動且可自由組合其所有顯示區塊 | built-in renderer→typed slot binding crosswalk：D1 設計審核＋正式 API/DTO mapping；不虛報已完成全平台通用模組引擎 |
| GAP14-B | 部分資料歷史折線/報酬比較、新聞、多帳戶與跨裝置保存僅以 synthetic data 表示；source/producer/revision/cut 未實際綁定 | source-bound schema & formal review if new contract |
| GAP14-C | 文字 4.5:1 的三組主要角色對比已加阻擋，但鍵盤 Focus/ARIA、色覺辨識、全主題和 200% 極端長標題的人工輔助技術 QA 尚未完整驗證 | D1/D2 Visual & Accessibility Gate |
| GAP14-D | 暫僅支援本機 PNG/WebP 150KB 以內匯入，匯入未寫入 Git、正式資料庫或伺服器；原始 SVG 未允許 | Security/CSP/SVG Sanitization + persistence review |
| GAP14-E | JSON 版型/模組定義僅為原型匯出；未具版本 CAS、跨螢幕同步或 Authority/Session 持久化 | MA10-U01/U06 & Auth/Session architecture formal review |
| GAP14-F | 預覽中 UI01 Dashboard 和 UI08 Portfolio 仍保持各自正式擁有的資料及操作契約；現階段只核對概念連結 | D9 19 UI + 64 findings crosswalk 與 PK11 qualified source review |

## 5. Gate decision

- 本紀錄的 10/10 **只代表被測試的離線 UI 原型互動**；不可等價成正式 19 UI 的 Source/Runtime/Accessibility Acceptance。
- Visual Design Reviewer 的獨立視覺審核記錄在 `D1_V1_4_VISUAL_DESIGN_REVIEW.md`，與功能 PASS 互不替代。
- 狀態仍為 `PROPOSAL / HUMAN_REVIEW_PENDING`；下一輪先由 Owner 操作 v1.4，指出問題或明確同意 D1 設計，然後才能組裝 D1 Design Handoff 候選。Human UI Design Acceptance ≠ Coding Authorization。