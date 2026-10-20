# B3 V1 D1 v1.4｜Frontend Visual Design Reviewer（VDR）審核

**角色定位：** 專責 UI 美編／UX，一次 review 全頁而非局部美化；**為本輪設計審查角色／自評，尚非真正獨立的 Ultra/Independent Reviewer**。不得修改 B3 正式治理、資金或交易 Authority；缺陷優先記錄為設計候選與回歸項目。

## I. 參考模式及界線

- TradingView 官方 Layout / Supercharts UX：版型可命名保存、可多圖但必須明確決定要同步的 subject/interval，避免意外全域同步。來源：https://www.tradingview.com/support/solutions/43000746975-tradingview-layouts-a-quick-guide/ 。借鑑互動，不抄襲品牌／技術實作，也不把其 Trading Panel 當 B3 order authority。
- IBM Carbon 2x Grid / High-density patterns：格線與 type scale 一致、card 的同層級資訊需對齊，side panels 改變有效可用版面；來源：https://www.carbondesignsystem.com/building-blocks/foundations/2x-grid/guidelines 。此處**繼續使用 B3 正式 12-column 基線**，不是移植 Carbon 的 16-column 結構。
- IBM 資料視覺化：簡潔標題、清楚單位/刻度、避免 chart decoration 掩蓋數據；來源：https://www.ibm.com/design/language/data-visualization/design/basics/ 。

## II. 視覺審核要點（人工畫面審視 + DOM browser metrics）

| 維度 | v1.4 觀察 | 結論與改善 |
|---|---|---|
| Align／節奏 | 八卡使用相同 Module Head / Content / Border / Grid，四張頂部卡高一致。大圖及 Summary 位置相鄰。 | 對齊候選可接受；繼續以固定 12 欄、12px gap、保留高密度但不壓縮含義。 |
| Information hierarchy | 主金額、變化與小圖出現在同張卡；News 明確候選；策略卡用比較棒條而非純文字。 | 改善優於 v1.3；後續要釐清所有可比報酬率口徑、首要 KPI 的視覺優先級。 |
| Density & no-scroll | Asset grid 固定 6 格、Holdings 固定 6 行；不同資料量切換維持外框高。 | 被測 100/125/150/200% 實際情境沒有 inner vertical scroll；但實際文字很長、真實 i18n 仍需測。 |
| Colors / harmony | 預設深色、暖棕、墨綠、淺色使用角色 tokens；主文字與背景對比低於 4.5:1 的設定會拒絕。 | 配色候選可接受，圖表系列與漲跌訊號仍須有非顏色提示。 |
| Left rail / flyout | ICON only、半透明貼靠彈層、Esc、底部快捷設定；不推動 Dashboard。 | 數量多時需加入 viewport flip 與 screen-reader keyboard-only 路徑測試。 |
| Workspace empty areas | 可見空格輪廓，滑入／焦點顯示＋；工作台可插入與拖放至指定 (x,y)。 | 實務上大量空格可保留淡線避免密集＋符號；需再用真實使用者檢驗可發現性。 |
| Module builder | 主體／NxM／區塊綁定分成左／中／右；右側在按＋前不出現欄位表單。 | 建議補上 Undo/Redo、模板版本及出錯通知，等 UI 正式資料契約設計時再研議。 |
| Long-hours trading UX | 常駐 Environment + Source/Quality 標示；短路徑與標準 icon 導覽；沒有隨意一鍵下單。 | 符合方向；委託、風險、權限尚須正式工程 Gate。 |

## III. VDR 對下一輪最值得採取的 4 項建議

1. **模板內容真正 schema 化：** 用 SlotSchema 對應 UI01／UI08 等 source，讓標準內建模組與自訂模組在正式 Coding 前可以共享同一種資料欄位／展示能力聲明；現版已共用外框和尺寸規則，尚未全量 schema 化。
2. **統一語義與資訊密度：** 概要／資金／策略／新聞在高密度設定下使用同一套行距、數值 tabular alignment 和單位層級，重複小字預設隱藏；必要 Source/Cut/Quality 例外。
3. **可發現性：** 工作台的空格＋在滑鼠 hover / keyboard focus 顯示最明確；導入後支援「重設到可讀版型」提示，避免大量極小卡片排列破壞可讀性。
4. **驗證體系持續自動化：** 每輪對 8 預設＋自訂模組做 1/6/8/14 筆、主題 × 寬度 × 100～200% 字體、UNKNOWN/STALE/PARTIAL、Save/Cancel、Keyboard focus 的交叉測試；不得只更新一張示意截圖。

## IV. Review gate

VDR 目前給出 **`PASS_WITH_CONDITIONS`（純設計審查意見，非正式治理 verdict）**：對齊、固定容量與編輯器操作已顯著改善；SlotSchema 全面化、真實資料綁定、安全隔離、全部 19 頁一致性、無障礙全面測試仍需執行。D1 保留 OWNER_REVIEW_PENDING，絕不視為已交付生產程式。