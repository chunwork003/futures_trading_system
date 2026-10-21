# B3 V1 · D1 v1.9 — 三層編輯、啟動情境與資訊流設計審查紀錄

> 日期：2026-10-21 Asia/Taipei。狀態：**PROPOSAL / HUMAN_REVIEW_PENDING**（非正式機器治理狀態）。
> B3 Accepted source pin：`9643bfc93a1631154be877536a1c91fc58df84be`。
> 設計分支：`design/b3-v1-ui-precode-review-20261017`。
> 前一版本：`prototypes/B3_V1_D1_FullDashboard_v1_8_DESIGN_CANDIDATE.html`；原版本不覆寫。
> 範圍：**唯讀來源分析、獨立 HTML 設計原型、審查文件與設計分支保存**；不修改正式 React／ASP.NET／Python、Broker、API、SQL schema、runtime 或授權。

## Owner 本輪決策 — 已確認，不再重問

| Owner Decision | 內容 | 在 v1.9 中的位置 | 設計狀態 |
|---|---|---|---|
| `D19-OWN-A` | **A：分三層**，工作區編輯 → 模組編輯 → 資訊模組編輯 | 同一互動視窗上方四個可返回的工作標籤 | PROPOSAL / 已表達偏好 |
| `D19-OWN-B` | **A：預設啟動 + 指定情境**；延續既有「恢復上次工作區」候選 | 啟動頁：原預設、指定情境（可增分頁/視窗）、上次工作區 | PROPOSAL；真正跨次保存 UNVERIFIED |
| `D19-OWN-C` | **A：工作區右側選擇 A 功能類別 → B 呈現形式 → C 可用模組 → 加入** | 工作區右側篩選和單一「＋加入」控制 | PROPOSAL |
| `D19-OWN-EXTRA` | 資訊模組需能選 UI/資訊流、圖／折線、時間軸、資金變化、年月日、單位、精度等；即時預覽 | 第三層資訊模組編輯器：來源類型、UI 連結、欄位、軸、期間、聚合、單位、精度、字級、可見標籤、圖例 | PROPOSAL，歷史 producer / SQL 執行 UNVERIFIED |

## 不重建正式 UI Identity / 不編造 SQL

- `UI01 Dashboard` 仍是投資總覽呈現入口；`UI08 Portfolio` 仍是投資組合／持倉權責；`UI17 Settings` 管理偏好但不因此取得任意資料儲存 API。
- `DataSubjectRef` 模型：同一模組僅綁定**同一資料主體**（帳戶、環境、Portfolio、精確資料資源）所容許的多種視覺表示；外觀混用功能**只在自定義工作區**候選，沒有合併風險／資金權威的能力。
- `InfoQuerySpec` 是唯讀設計 JSON，典型欄位 `subject`, `field`, `axis`, `resolution`, `aggregate`, `unit`, `precision`, `query_binding_id: UNVERIFIED`, `sql_execution: NOT_AUTHORIZED`。此 HTML **不生成或執行 SQL**，不包含資料庫連線、不啟用任意查詢接口。
- 未驗證的「資金歷史時間序列」不能因為畫面出現折線圖就視為存在；正式查詢應由 BFF/API 透過核准的受控 producer 綁定、具備 Source / Cut / Quality / Dataset Snapshot / 權限與單位定義。
- 來源品質 `UNKNOWN / STALE / PARTIAL`、LAB/PAPER/LIVE、交易與資金授權保留原先 B3 Governance 邊界；本輪 mock chart 不作為市場／帳戶／交易證據。

## 工作區（第一層）

- 左：UI01～UI19 頁面／分類樹，統一模板勾選候選，頁面版型來源選擇；細項可展開；資料來源仍由頁面各自核對。
- 中：原始八張模組完整保存，12 欄 × 8 列示意格線，空格不顯示滿畫面＋，不再要求點空格新增。
- 右：A = 頁面類別（一般頁面鎖定；只有「自定義頁面」可選其他類別），B = 七種呈現類型，C = 可用模組；單一「＋加入模組」並自動尋找合法空位。
- 拖曳：整塊占用範圍預覽；落入占用區時嘗試最近合法格線位置；不可重疊；**尚待完整 drag-edge/collision matrix 驗證**。
- 右側模組預覽含受控資料的合成資訊示意，與可選尺寸標示；已有模組右上刪除控制。儲存／取消僅動草稿；JSON 匯出於左下角。

## 模組（第二層）

- 可建立/複製/修改/刪除自訂模組，單一主體 NxM 格線與資料 slot ID（例如 S1、R1C1）。
- 右側 A～G：大類／細類鎖定，C 名稱可編，D 格內資訊類型，E 資訊來源，F 合成即時預覽，G 保存／另存。
- 既有模組改名、大小或資料時要求覆蓋／另存決策；另存撞名或仍採原名會阻止／要求改名。被工作區引用的模組刪除需指定同主體替代者，不能悄悄丟失引用。
- 原始內建模組權責仍不可藉由修改畫面直接改寫正式 B3 API／功能 ID。

## 資訊模組（第三層）

- `SourceKind`：受控資訊資料流／既有 UI 功能連結；UI 編號僅導覽標識，不授權前端資料存取。
- `Metric`：由目前模組所屬的單一 Subject 候選欄位篩選。
- `Visual`：折線、長條、面積、數值卡、表格、文字。
- `Temporal`：時間欄位、日／週／雙週／月／季／半年／年、期末／差額／平均／總和（正式聚合語義待核）。
- `Presentation`：TWD／萬元／%／點／筆、精度、數值字級、標籤與圖例開關，具合成 DEMO 視覺預覽。
- `SQL boundary`：只匯出 QuerySpec 候選，不直接拼接／執行 SQL；正式資料倉儲層會另行設計固定欄位白名單、資料權限、快照、錯誤及審計。

## 啟動與多視窗

- `DEFAULT`：預設首頁和候選視窗數。
- `CUSTOM`：新增情境／命名、選擇 UI 頁面、以新分頁或新視窗加入、刪除頁面；設計草稿儲存／取消可回復。
- `LAST`：恢復上次工作區候選；不自動恢復交易草稿、風險權威或任何登入憑證。
- 真正 Browser multi-window creation、跨視窗 Account／Environment／Portfolio Session scope、保存與衝突版本需正式 Auth/BFF/MA10 檢核；原型不會真的創建登入工作區。

## Functional Reviewer vs Visual UI Reviewer

- Functional／Contract Reviewer：確保 KEEP-01～15、D1-R14-01～10、十九個 UI/六個 MA10 Units、DTO/API/Authority 範圍沒有被視覺修改侵蝕；不准以 Mock 對應當正式 producer。
- Visual UI Reviewer：只提建議並檢查 8px 間距、標題層級、文字可讀性、框線/空白格、彈窗固定尺寸、數字對齊、鍵盤焦點、不同寬度與字體；不得直接刪改既有功能或 B3 治理。

## v1.9 有界瀏覽器結果（不是全面 D1 PASS）

請見 `qa/B3_D1_v1_9_REGRESSION_TEST.py` 與 `qa/B3_D1_v1_9_REGRESSION_REPORT.json`：

- **18/18 PASS**：包含原首頁八卡、三層入口、A/B/C 模組加入、取消草稿、一般頁面鎖定、自定義頁面選類別、模組 A～G、第三層欄位／時間與非 SQL 查詢規格、儲存返回、啟動情境加頁與取消還原、無 JS 錯誤、1500／1100px 對話框未越界。
- 功能與美編回歸「尚未驗證」：全部 19 頁具體模組 API、64 Findings crosswalk、同類統一模板跨頁保存/衝突、真正拖曳到被占格後的最近合法位置全情境、200% 字體、全面 WCAG 色板、跨裝置持久化、多視窗隔離與實際 SQL producer。
- 暫不將 `D1-R14-01～10` 或 `KEEP-01～15` 全數標 PASS。

## 下一輪建議 Gate

1. Human 實際操作同一份完整首頁下的「工作區 → 模組 → 資訊模組」，確認畫面布局、slot 點選與 A～G 合理性；可回傳圖片逐項標示。
2. 實施獨立 Visual UI Review 更完整的網格占用邊界與 150/200% 字級截圖審核；修復再做全域回歸。
3. 完成 UI01/UI08 資金／歷史金額的正式資料 producer+DTO+時間區間口徑差異清冊，以及其 API 契約審查 Gate。沒有來源不得隱含已可用。
4. D1 尚未 Human Design Acceptance；Human UI 確認 ≠ Coding Authorization。