# B3 V1 — D1 v1.0 Candidate：投資總覽與共用 Shell 視覺設計規格

> **Status:** `PROPOSAL / OWNER_REVIEW_PENDING`；非 Human Design Acceptance，非 Architecture 修改，非 WO/Grant，非 Coding Authorization。討論分類不等於 B3 正式機器狀態。  
> **Date:** 2026-10-19（Asia/Taipei）  
> **Accepted source pin:** `9643bfc93a1631154be877536a1c91fc58df84be`  
> **Git design branch:** `design/b3-v1-ui-precode-review-20261017`  
> **Prior evidence:** `D1_GLOBAL_APP_SHELL_DISCUSSION.v0.2.md` ～ `v0.9.md`  
> **Companion:** `B3_V1_D1_Template_Studio_v1_0.html` — standalone **design visualization**, mock only; v0.9 full overview remains separate and preserved.

## 0. 來源/身分錨點與邊界

| B3 identity | 固定來源/正式功能 | D1 對應 | 分類 |
|---|---|---|---|
| UI01 Dashboard `/dashboard` | `getDashboard`, `getAccountCapital`, `getHealth`; MA10-U01/U02 | 投資總覽起始頁、概要/資金/健康摘要 | SOURCE_CONFIRMED (來源身份)，目前視覺呈現 PROPOSAL |
| UI08 Portfolio `/portfolio` | `getPortfolios`, `listGroups`, `queryAttribution`, budget proposals/confirmation; MA10-U02, and U04/U06 dependencies | 資產與策略群組詳情；UI01 總覽卡片可 *連結* UI08 | SOURCE_CONFIRMED identity; 不將 UI08 資本決策放入 UI01 前端 |
| UI02 Chart, UI03 Market, UI04 Strategy Builder, UI05 Research, UI06 Comparison | 各自契約保持原 ID | 導覽/快捷連結/工作台切換 | SOURCE_CONFIRMED identity, PROPOSAL 導航 |
| UI16 Automation/Progress `/engineering/work` | `getEngineeringStatus`, `proposePlanning` | 工程排程/進度入口；**不等於**定時回測引擎 | SOURCE_CONFIRMED, scheduler UNVERIFIED |
| UI17 Settings `/settings` | `getConfig`, `saveConfigCandidate`, etc. | 全域設定入口；視覺偏好是否有正式保存 DTO **尚未驗證** | SOURCE_CONFIRMED identity, persistence UNVERIFIED |
| MA10/PK11 | 12-column Desktop shell; LAB/PAPER/LIVE scope; UNKNOWN, STALE, PARTIAL, Snapshot/Source/Cut/Quality; U01..U06; 19 UI Contracts | 所有模組讀取/狀態/快捷規格不得繞過正式 API/BFF/Authority | SOURCE_CONFIRMED 約束 |

**不變事項：** UI 編號永久固定；固定來源並非畫面已施工；React→ASP.NET BFF→Python API、risk/capital/order/server authority 不受視覺或模板控制。新聞資料源、跨裝置布局同步、定時研究、圖表授權與第三方圖示載入均不宣稱既有 API。

## 1. Grid / 模板計量：先決定「能放什麼」再決定卡片大小

**共同標準候選（需在 D1 Human review 批准）**

- Desktop 採來源 MA10 的 **12-column grid**；最低邏輯切割 **2 columns**（最多六個最小 KPI 模組橫排），但小模板另需實際內容寬度至少 **190 CSS px**；若不足，自動改為較寬版型或折行，不擠壓文字。
- 格線間距候選 12px；內容留白 S:10px, M:12px, L:16px；字體分組/語系依 UI 設定，不得打破最低可讀密度；Desktop 高度為模板所需高度而非資料量動態高度。
- `S/M/L/XL` 是 **尺寸族**，不是 4 個任意百分比：S=2/12、M=3～4/12、L=6～8/12、XL=12/12；每個資料模組只允許表中指定的一組 `(grid-span, fixed-height, capacity)`。
- **禁止透過內部垂直捲軸來容納標準資料筆數。** 少於 capacity：保留 skeleton-free 留白/空位；超過 capacity：在 header 位置顯示 `<` `>`，切換時所有 header/body/footer/frame bbox 保持不變；資料缺少不可用假 0 填空。
- 自訂字體、窄視窗及高對比：使用可驗證的 responsive profile，允許變為不同模板，但同 profile **不會因單頁資料數量**改變卡片大小。若任一模板容不下完整安全資訊則顯示不可選、提供相容尺寸；顯示口徑不能裁切。研究/資金權威 warning 與環境文字不可隱藏。
- 各尺寸層的 `capacity` 是視覺規格候選，**不是 API pageSize**。真正讀取時必須由 snapshot/cursor/coverage/page permission 定義，不能把 `array.length < 6` 視為已完整覆蓋。

### 1.1 Template registry — 初版可審核列表

| Template key | 資料類型／UI | S (span / h / 容量) | M | L | XL | 固定必顯 | 可隱藏 / 連結 |
|---|---|---|---|---|---|---|---|
| T-KPI-OV | 概要 UI01 | `2 / 156 / 1 KPI` | `3 / 226 / 1 KPI+Δ` | `6 / 320 / 3 比較值` | 不提供 | 來源有效的主數值、幣別/單位必要縮寫、指標期間、品質狀態 | 說明、其他比較，詳情至 UI08 |
| T-KPI-CASH | 資金 UI01 | 不提供 | `3 / 260 / 主值+1段期間` | `6 / 326 / 主值+4期間+spark` | `12 / 410 / 帳戶組合拆解` | Source/Cut、可用額與資本不同口徑、區間與 Δ額/Δ率 | 非必要註解、示意折線，詳情至 UI08/UI12 |
| T-LIST-STRATEGY | 策略績效 UI01/UI05 | 不提供 | `3 / 256 / 3列` | `6 / 354 / 6列` | `12 / 442 / 12列(雙欄)` | 每列策略名稱、有效回報/UNKNOWN、期間口徑 | 分組細節，連結 UI05/UI08 |
| T-NEWS | 投資相關新聞候選 | 不提供 | `3 / 236 / 1則` | `6 / 350 / 3則` | 不提供 | NEWS DEMO/來源不明標示、來源/時間/授權，未證實則 no-live badge | 預覽摘要；詳情 link 待核，無 UI20 |
| T-CHART-PORT | 組合表現 UI01 | 不提供 | 不提供 | `8 / 470 / 1大圖+主值+Δ` | `12 / 550 / 多系列/比較` | 組合、幣別、時間切片、單位、主值、相較前期的金額/百分比、Source/Cut/Quality | 圖例拆解、附註；各序列不跨 snapshot 任意相加 |
| T-DONUT-ASSET | 資產分布 UI08→UI01摘要 | 不提供 | `4 / 356 / 1 donut+3列` | `6 / 420 / 1 donut+6列` | `12 / 470 / 1 donut+完整分類頁` | 分類與金額／比例一致 Cut、無缺值假佔比 | 詳細分頁；UI08 詳情 |
| T-GRID-ASSET | 資產類別卡 UI08 | 不提供 | `4 / 310 / 3卡` | `8 / 458 / 6卡(3×2)` | `12 / 550 / 9卡(3×3)` | 各卡類別/金額/投報有效性/幣別/spark 與提示 | 篩選/排序/總覽 checkbox，切分頁時留空位 |
| T-TABLE-HOLDING | 持有資產 UI08 | 不提供 | `4 / 342 / 3列` | `8 / 466 / 6列` | `12 / 610 / 12列` | Symbol+Venue identity、數量單位、金額、回報狀態/來源 | 表格與簡易卡切換；不能編造已對帳實倉 |
| T-STATUS-SCHED | 研究排程摘要 UI05/16 候選 | `2 / 156 / 1狀態` | `4 / 260 / 3筆` | `8 / 440 / 6筆` | 不提供 | **排程未實作**，必須清楚標示 proposal，不執行任務 | 任務詳情/結果連結 UI05、治理連結 UI16 |
| T-ALERT-RISK | 風險快照 UI11 | `2 / 156 / 1狀態` | `4 / 264 / 3條` | `8 / 420 / 6條` | 不提供 | 環境/範圍/Unknown、風險警示不可隱藏 | 詳情 UI11；不提供前端風控認可 |
| T-WATCH | 觀察清單 UI02/03 | 不提供 | `4 / 264 / 3標的` | `8 / 434 / 6標的` | 不提供 | 商品/市場歧義、資料新鮮度 | 詳細 UI02/03 |

> **尺寸單位：** `span` = 12欄網格中的欄數，`h` = CSS px（候選桌面 profile）；S/M/L/XL 不必等於固定欄數而必須與模板 registry 綁定。

### 1.2 自動模板配置與防止「畫面跳動」驗收

1. 如果 `availableRecords <= capacity`，固定 slots 總數；空 slot 使用不帶金額/負數的視覺留白，未驗證空結果需保留 UNKNOWN。  
2. 如果 `availableRecords > capacity`，預先計算頁數，且頁碼 `i/n` 在相同 header 固定位置；頁切換只換 slot 內容，不變更 card rect。  
3. 選模板時先核對 `supportedType`, `fontProfile`, `minReadableWidth`, `requiredSafetyFields`；不合格的按鈕 disabled，並提供原因和更大的合法模板。  
4. 對同一筆資產的不同資產曝險類別/商品型態，不得二次累加；數值排序先問：`UNKNOWN`、異幣別、Snapshot drift、不同計算期間。  
5. 系統不因市場行情變動或用戶縮放字體，偷偷修改卡片高度；必要時在下一個 breakpoint 重新排版並顯示一次性提醒。

## 2. 首頁模組清單與重要/可選分類

| 模組 | 首頁預設 | 來源/注意 | Template default | 互動／跳轉 |
|---|---|---|---|---|
| 概要、總值（UI01） | 核心預設 | `getDashboard`, Account Context；權威資本分子待核 | T-KPI-OV M | 組合切換/釘選→UI08 |
| 資金與區間變化（UI01） | 核心預設 | `getAccountCapital`; 不可前端算可用資金 | T-KPI-CASH M | 日/週/雙週/月，Δ元/Δ率→UI08/UI12 |
| 策略績效（UI01） | 核心預設 | KPI 名稱需 producer/snapshot/strategy attribution 驗證 | T-LIST-STRATEGY M | 策略分頁→UI05/UI08 |
| 組合表現（UI01） | 核心預設 | 分期總值和區間 Δ；不跨幣種混算 | T-CHART-PORT L | 天/週/雙週/月/季/半年/年；比較分解 |
| 資產分布（UI08 摘要） | 核心預設 | UI08 owns portfolio detail; 本卡唯讀 | T-DONUT-ASSET M | 資產/商品型態切換→UI08 |
| 資產清單（UI08） | 核心預設 | 有效持有範圍/虛擬倉/一致 Cut；自訂模板顯示 | T-TABLE-HOLDING L | 類別、排序、3/6/12固定容量；詳情 |
| 資產卡（UI08） | **建議預設，但允許關閉** | 若資料重複可與「資產清單」擇一或都留 | T-GRID-ASSET L | 分類卡分頁/hover；到 UI08 |
| 新聞 | 可選，**現有原型暫顯示** | Provider/license/source/entitlement UNVERIFIED | T-NEWS M | 多則轮播，不視為已提供即時新聞 |
| 排程摘要 | 可選／**左側排程快捷預設開啟** | 定時研究需要新 schema / scheduler，不可由 UI browser 執行 | T-STATUS-SCHED S | UI05 規劃，UI16 治理查看 |
| Watchlist／Risk／Cashflow | 可選 | respective UI02/03, UI11, UI12 contract boundaries | T-WATCH M / T-ALERT-RISK M / T-KPI-CASH L | 只讀跳轉，不影響交易權威 |

**「核心預設」不是不能移除**：首頁模板內固定推薦放置以利初期 UX，一般用戶可調整；不可刪掉/隱藏的只有環境/帳戶權限提示、資料品質、安全警示與來源查證入口。

## 3. Navigation / Setting 責任界線：精簡後的最終候選

### 3.1 Top Bar（仍為 PROPOSAL）

`[B3 品牌] [投資組合 ▾] [市場 ▾] [實驗室 ▾] [工具 ▾] [交易 ▾] [新聞 ▾ (最後)]  … [搜尋頁面/功能] [LAB/PAPER/LIVE] [帳戶▾] [≡]`

- `投資組合`：UI01、UI08、UI12、UI11 狀態/詳情（依 Scope 可見）。
- `市場`：UI03 資產/交易所/股票/債券/ETF/期貨等、UI02 Chart/Watchlist；商品型態與曝險類別不同維度。
- `實驗室`：UI04 Builder、UI05 Research、UI06 Comparison、UI13 Bond/Rate Lab；研究排程屬 **候選**，不與 Engineering dispatch 混用。
- `工具`：試算（合成，不具 broker authority）、研究/圖表輔助工具；新增 Calculator API 先查責任歸屬。
- `交易`：UI07 PAPER Simulation、UI09 Orders、UI10 Positions、UI11 Risk；保持 Permission Scope，不可藉導覽讓 LAB 下單。
- `新聞`：末端，供應商/API/rights 待查，不新增 UI20；`更多` 移除。
- 搜尋固定帳戶側，支援 19 UI＋Function Registry keyword，不以別名冒用授權。界面 ICON 預設無白框、單色；Active/Focus 用色塊/底線及文字提示。

### 3.2 Left shortcut：左下齒輪的責任

- 分類 ICON rail 固定、不隨主頁面滾動；依使用者已選功能類別顯示；右側 flyout **只顯示已選子功能**，依項目數量長高且半透明，最多視窗高度，過量才顯示軌道上下箭頭。
- 左下 ⚙ **只管快捷**：選取、搜尋、排序、拖曳、分類顯示、ICON、保存；不管理帳戶、不改畫面主題、不改投資資料。
- 預設 `排程` 快捷顯示於 `實驗室/研究` 類，UI05 路線標 `PROPOSED_SCHEDULER`, 永遠不在 UI01 直接執行排程。
- ICON 選擇器候選：至少 20 個內建單色圖示（Home、Portfolio、Chart、Market、List、Watchlist、Strategy、Research、Clock、Calendar、Orders、Positions、Risk、Cash、Settings、History、Automation、File、News、Tools、Bookmarks、Bell、Wallet、Compare）；可還原、下載配置 JSON；外部匯入 **先只收封閉安全格式**，SVG sanitization/XSS/CSP/上傳權限送安全審查。

### 3.3 Right ≡ 全域設定：不能與快捷混用

`面板（主題調色、字型/大小、圖示樣式、文字顯示） → 工作台（格線、模板、大小、模組放置/匯入匯出） → 啟動與視窗（原預設 UI01／自訂開啟頁集／上次工作區；多螢幕 layout） → 資料顯示與更新（單位、幣別、刷新策略/資料品質） → 帳戶與環境（權限查證，不是視覺設定） → 系統/幫助/Audit(UI18)`

`面板 → 顯示`：預設隱藏開發標籤/正式 UI 編號/示意註記；必要資料狀態保留文字（不能把 UNKNOWN/STALE/權限警告關掉）。幣別顯示可淡化但混合 USD/TWD、單位不一致或高風險操作時，必須完整顯示。

## 4. 模組資料同步 / 更新資訊語義

- `Follow Main` **預設**：頂部主組合由 1→2，所有未釘選 `UI01`/`UI08` 展示卡切換到 2，所有有來源權威數據重新查相同 Account/Environment/Portfolio scope；不因 UI 狀態造成權威值改變。
- 單卡 `Pin`：保留個別投資組合顯示，必須標示 `📌 組合 X`；如果原本 Account/Environment 失效或無權限，卡片自動轉 `PERMISSION_DENIED`、拒絕默默沿用舊資料；不得無提示跨帳戶相加。
- **組合表現主圖**：在折線上方顯示 `期末金額`、`相較上一對等期間金額 Δ`、`Δ%`；例如選「月」就是本月 vs 前月同政策值。對 0／未知分母不顯示造假的百分比。可選策略/資產拆解，但不能與整體重複加總。Y 軸依資料範圍取整合理刻度，應標明 `萬 TWD`，不以固定 0 起點扭曲視覺；資料單調不能任意誇大軸範圍。
- **Financial KPI 定義候選**：Portfolio Market Value、Equity、Available Cash、Margin、Capital Budget、Realized/Unrealized PnL、Total Return、Time-Weighted/Money-Weighted Return 必須各自指定 producer、currency, FX, valuation cut, numerator/denominator, timeframe, quality；不自行混同。這部分有界源對照：`UNVERIFIED / FORMAL_REVIEW_REQUIRED` 如有新 DTO。
- **刷新**：Dashboard 主動顯示情境候選 30–60s，離開頁面降頻；Chart 視源授權推送／缺口重取；Order/Risk 以 server receipt/event 為準；Research job 事件或 10–30s 查詢；News 依供應商發布/權利。這些是架構討論候選、不是正式可用 SLA。
- **啟動**：預設 UI01，目前規劃三種啟動策略：原預設 / 用戶指定頁集合 / 上次工作區；Multi-window session identity/Account/Env must be scoped and separately reviewed. Prototype 只能導出設計 JSON，**不代表**端到端啟動或跨裝置狀態已實作。

## 5. Human 設計 Gate / QA 反例 / 尚未決議

| Checkpoint | 驗收條件與反例 | 狀態 |
|---|---|---|
| D1-GRID | 模組模板選項不合法應 disabled；S 最小不小於 190px；任意資料筆數/頁切換高度穩定，不用模組內捲軸；字放大和窄視窗要選相容模板 | **OWNER_DECISION_REQUIRED** on template numbers, **UNVERIFIED** all breakpoints |
| D1-CHART | 主圖含期末主值與本期/上期 Δ額+Δ率；短期/缺值/無比較不得顯示假百分比；同 Cut/幣別才可聚合 | **PROPOSAL** UX；金融指標資料口徑 **UNVERIFIED** |
| D1-CARD-LINKS | 任何卡片都具有 registry identity、route、permission、source；新增非正式功能須標 proposal；不改正式 UI01～19 ID | **SOURCE_CONFIRMED** page identities，subfeature registry **PROPOSAL** |
| D1-NAV | 頂部無「更多」、新聞最後、搜尋右側；左下只管快捷、右上只管全域設定；排程快捷預設有，但不能執行排程 | **OWNER preference received**, final visual acceptance pending |
| D1-COLOR | 主題色全 token 覆蓋，中文微軟正黑體/英數 Arial 預設，文字隨背景深淺調整，不能隱藏紅綠以外警示語義；ICON >=20 自訂安全邊界 | **PROPOSAL**；全組 WCAG check 未完成 |
| D1-PIN | 切換組合後未釘選卡一起切換、釘選卡顯示來源；切換帳戶時無權限釘選不能繼續顯示 | **OWNER direction**, formal scope review pending |
| D1-AUTH | LAB/PAPER/LIVE + account scopes visibly distinct，未知委託不可視為未送，前端不自行准入 | **SOURCE_CONFIRMED** security principle |
| D1-PERSIST | User/global/device/window config, CAS/last workspace/reset/import/export, restore-on-start 先定相容性再 Coding | **FORMAL_REVIEW_REQUIRED** if new persistence API |
| D1-NEWS/SCHED | News provider/rights & timed research scheduler (job, timezone, quota, permission, audit/reentry/receipt) 先 bounded architecture check | **UNVERIFIED / FORMAL_REVIEW_REQUIRED** |
| D1-FINAL | 人工逐頁/逐模板 visual walkthrough；大中小、資料 1/6/8、空/UNKNOWN/STALE、無效欄位、帳戶多螢幕視覺範例完整；當 Human 說「D1 無須再調整」才整理 Acceptance Candidate | **NOT YET ACCEPTED** |

### 5.1 本輪建議下一個 Human 只需看的三個問題

1. 對 **S/M/L/XL 格線與容量**（S 2欄、M 3/4、L 6/8、XL 12）的表格是否符合你要的統一感？若不合理，優先改單一模板族而非重改所有頁面。
2. **資產卡與持倉清單**要保留為兩個核心預設模組，還是二擇一預設、另一個列入可選？目前推薦「持倉清單核心、資產卡可關閉但預設顯示」。
3. **組合表現**主要比較指標選「權益／投資組合總值」哪一個做預設？在源定義驗證前，視覺樣板只用 `DEMO 示意組合價值` 並顯示語義不確定提示。

以上是 **有界設計審查**，而不是詢問每個瑣碎 UI 決策。其他自動可改善項繼續迭代；沒有 Human 回覆前，D1 不予正式 closure。

## 6. Coding handoff candidate（此刻不授權）

D1 在獲得 Human Design Acceptance 和必要獨立審查後才可彙入 `B3_V1_UI_UX_DESIGN_REVIEW_PACKAGE`，其中提供 `ui_id`, `template_key`, `size_variant`, `required_fields`, `optional_fields`, `capacity`, `source_operation_ids`, `producer`, `permission_scope`, `truth_states`, `responsive_profile`, `interaction_receipts`, `fixtures`, `negative_oracles`, `unverified`, `owner_decision_ref`。

U01 為共用 Shell/DesignSystem/FeatureRegistry/TemplateRegistry 候選；U02 為 UI01/UI08 資料顯示／Portfolio 首頁；U06 端到端 BFF/DTO/E2E review；新增偏好保存、跨視窗帳戶隔離、排程服務不因畫面表格而授權。