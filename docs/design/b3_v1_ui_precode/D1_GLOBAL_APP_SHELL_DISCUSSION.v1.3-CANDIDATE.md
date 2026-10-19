# B3 V1 — D1 v1.3 投資總覽／共用 Shell：設計審查與回歸紀錄

- 記錄日期：2026-10-20（Asia/Taipei）；本輪 Human 圖片與回饋來自 2026-10-19。
- 類別：`PRE-CODING UI/UX DESIGN PROPOSAL`，`OWNER_REVIEW_PENDING`；**非正式機器治理狀態，非 Human Design Acceptance，非 Coding Authorization**。
- Accepted B3 V1 source pin：`9643bfc93a1631154be877536a1c91fc58df84be`。不改動正式 Architecture／Source Contract／19 個 UI Identity／PK11／MA10 U01–U06 或交易授權。
- 設計分支：`design/b3-v1-ui-precode-review-20261017`，保留前一輪的 `D1_GLOBAL_APP_SHELL_DISCUSSION.v0.2.md`～`v1.2-CANDIDATE.md` 與各版 HTML；不以 GPT 記憶作權威。
- 本版獨立、單檔 HTML：`docs/design/b3_v1_ui_precode/prototypes/B3_V1_D1_FullDashboard_Integrated_v1_3.html`。
- 本輪使用者提供 7 張標註截圖：快捷設定、ICON 下拉示意、資金與圖表空白、資產分類切換、左側面板、版型編輯及建立模組。僅作視覺設計依據，不引用第三方專有程式／資產。

## 1. 十二項回饋的處理

| # | Human 指正 | D1 v1.3 具體設計修正 | Status／注意 |
|---|---|---|---|
| 1 | 左邊紅框只留外觀下拉，不要說明 | 快捷外觀三擇一：`ICON / ICON＋文字 / 文字`；刪掉額外說明與原相容控制的可見性 | `PROPOSAL`；僅原型視覺 |
| 2 | ICON 改為類別＋圖形兩種選取，圖形選單應為圖案 | `類別` 文字選單＋**實際 SVG 圖形格狀下拉**（內建 24 個示意 ICON）；更換暫存在快捷編輯草稿，按「儲存」與選取快捷一起套用；取消不影響原選擇 | `PROPOSAL`；ICON 外部匯入仍要做安全／授權審查 |
| 3 | 同尺寸卡不能大半留白 | 將頂排概要／資金／策略／新聞模板統一為固定 275px 級距；概要補本期變化與組合帳面資訊、策略補迷你比較進度、新聞補來源候選資訊、資金補區間走勢及變化。資料是合成 DEMO，非權威績效 | `PROPOSAL`；不同字體及窄螢幕仍需逐模板驗證 |
| 4 | 組合表現須有各組合／策略的分類金額條圖及多欄位 hover | 主線表示總額，四類堆疊長條代表股票／核心、債券／收益、期貨／趨勢、現金／其他。hover 顯示同一期總額、總額較前期變化，以及**每類的金額與前期變化**；拆分合計與 DEMO 總值一致 | `PROPOSAL`。拆分比例是合成視覺模型，不是 Source-accepted attribution；正式需要 UI01/UI08/API/DTO 核對 |
| 5 | 總覽／單類資產頁籤不應改變版型大小 | 資產卡每頁 6 格、固定 520px。若單類只對應 1 張資產卡，其餘使用**同資產的資訊切面**補足（不虛構額外持倉）；分類切換不改卡框高，正式保留頁內 › 翻頁與來源明示 | `PROPOSAL`；小字放大／多市場長名稱完整驗證未完成 |
| 6 | 左側快捷彈層遮住主頁、ICON 過多雜亂 | 選取某類僅顯示該類快捷，分類 ICON 立於固定左列；展開時**主工作區右移讓出彈層空間**，避免永久遮住模組。另修正文字模式 ICON 被彈層攔截點擊的實際 bug，按鈕層級分開 | Browser verified at 1550px；手機／窄螢幕需另定遮罩／抽屜式模式 |
| 7 | 面板缺少增加資訊模組 | 「工作台版型」的獨立編輯器左側有功能索引／模組庫，按「＋」可新增整張模組；「建立模組」內的虛線空格按「＋」可加既有資料欄位。**模組實例與區塊內容是兩個不同層級** | `PROPOSAL`；只綁定既有或待核實資料來源 |
| 8 | 工作台版型即進入版型調整；JSON 放同處；不要全螢幕控制 | 全域設定的「工作台版型」只留「進入工作台版型調整」主入口；獨立編輯器底部增加**匯出版型 JSON**、儲存／取消；移除原本該區醒目的 JSON 與全螢幕控制 | `PROPOSAL`；匯出設計草稿不是伺服器保存 |
| 9 | 建立模組與模組版型分開；用 NxM 格數，S/M/L/XL 只是大小分類 | 全域設定獨立分頁：**模組版型**（2、3、4、6、8、12 水平單元 × 1–4 垂直單元，A/B/C 起始構圖，最多 4 個區塊，重疊/越界阻擋，命名儲存及再載入）；**建立模組**（頁面類別、資料類別、S/M/L/XL、從版型庫挑 NxM 構圖）。建立時不因資料類別把尺寸反灰；將來放進工作台選資料時仍須檢核最低可讀面積 | `PROPOSAL`。NxM 是視覺容量而非 API page size；建模版型尚非正式後端 schema |
| 10 | 模組只可編名稱，右側屬性不應先存在，點 + 後顯示資料、表示形式、細項圖文 | 自訂模組預設**僅左側表單與中央空白構圖**；點區塊「＋」才顯示右側；右側只留 `資料`、`表示形式（圖文）`、`細項圖文形式／功能`，隱藏原區塊標題／自由文字編輯 | `PROPOSAL`。資料來源、頁內功能仍是設計綁定，非任意執行指令 |
| 11 | 子設定按取消／確定要回原設定頁 | 工作台版型編輯器 Save、Cancel、Esc 均回「設定中心 → 工作台版型」；建立模組 Save、Cancel、Esc 均回「設定中心 → 建立模組」，設定視窗固定高度；不再退出到首頁迫使重新開設定 | Chromium verified |
| 12 | 更新與排程放左側功能，而非設定小項 | 全域設定的「更新與排程」頁籤隱藏；左側新增預選「更新／排程」分類 ICON 及 `研究排程（UI05 候選）`、`更新／監控（UI16 候選）` 快捷，選取可打開說明／來源未授權訊息 | 兩功能 **未驗證正式 scheduler/update API**；不得讓 Browser/Mock 背景自動工作或委託交易 |

## 2. 正式 UI/Unit/Authority 對照

- **UI01 Dashboard** `/dashboard`：正式來源 `getDashboard`、`getAccountCapital`、`getHealth`；首頁金融欄位呈現需按供應端快照、Cut、Coverage、Quality 定義，不依樣板自算權威現金或可用額度。
- **UI08 Portfolio** `/portfolio`：持倉、群組、分布、配置與歸因等詳細管理的獨立 Identity；首頁可連向 UI08，不轉移 API/Authority。
- **UI05 Research** `/lab/research`：Research Run/Snapshot 有正式來源；**定時執行 Scheduler** 仍是擴充候選，研究排程本輪只有視覺入口。
- **UI16 Automation/Progress** `/engineering/work`：已有工程治理進度與 Planning proposal 範圍；不可因「更新」快捷而推斷正式行情輪詢／計時排程存在。
- **UI17 Settings** `/settings`：視覺原型設定中心是候選資訊架構，不能假設具有 Browser→BFF→Python 的通用個人版型持久化 API。
- 導航功能索引沿用正式 UI01～UI19；`自訂模組`、`模組版型` 與 `更新排程` 不新增官方 `UI20`，也不修改 Runtime Permission／LIVE／Risk／Order／Broker Authority。

## 3. 功能性驗證紀錄（瀏覽器單檔概念原型）

- Chromium headless / Playwright，透過 `set_content` 載入本機 HTML；先前沙箱對 `file://` 的限制仍存在。
- 首頁初始八張正式 UI 規劃模組保留，額外建立模板加入後增加為第九張，未覆蓋原先卡片。
- 快捷視圖三模式切換；24 個圖案可視選擇；Cancel 不套用，Save 套用；左側 ICON 可重複點擊收合，不受快捷彈層攔截。
- 固定大小設定中心七個可見分頁切換高度一致（測試 820px），單類資產分頁切換外框高度 520px 不變，固定顯示 6 個同規格資產資訊卡／切面卡。
- 工作台草稿按 ＋ 新增到 9 張後，按取消仍保留首頁原先 8 張；Esc 亦會捨棄草稿並返回原設定分頁。
- 模組版型 6×2 / C 四區可存入個人設計庫，建立模組能選取該版型，點虛線＋才出現右側屬性；取消返回模組建立的設定分頁；保存自訂模組後可加入首頁成第 9 張。
- 圖表 Tooltip 同步顯示總額 + 股票／債券／期貨／現金四類的金額與前期變化，僅合成數據；UNKNOWN 時金額不被呈現為可信數值。
- 以上回歸未發現 uncaught JavaScript errors。**這不是正式 B3 Runtime、E2E、財務核算、授權、資訊來源或多螢幕分離測試。**

## 4. 重要保留及反例

1. `D1-GAP-13-01`：自訂 NxM 版型現上限四個區塊，資料區合併、拖曳內部分割及任意 12×N 切割尚未定案；本輪只支持最少可維護的組構方式。
2. `D1-GAP-13-02`：字體 150%／200%、長中文/英文名稱、超寬螢幕、窄視窗與卡片完整容量尚需全型測試；任何無法容納重要數值的配置應禁止儲存而不是以內部 scrollbar 消化。
3. `D1-GAP-13-03`：所有資料類別到 B3 DTO/API/Provider/Cut/Currency 的精確欄位尚待核實；自訂版型與正式查詢模板的 schema/持久化／跨裝置同步需 `FORMAL_REVIEW_REQUIRED`。
4. `D1-GAP-13-04`：研究排程、新聞內容及投資工具的新服務仍是 `UNVERIFIED`，在各所屬頁面逐項審查，不在 D1 偷渡 API。
5. `D1-GAP-13-05`：個別模組釘選與多窗口不同 Account/Environment 的隔離、重連和持續資料品質，仍需 Auth/Permission/State 正式語義審查。
6. `D1-GAP-13-06`：目前個人模組與版型可能存在當前瀏覽器 `localStorage`，但不能推論已寫入 B3 的資料庫、Git 或跨裝置同步。每次 Human 修改後，需透過 JSON 回傳後在設計分支另外提交，可追溯版本才成立。
7. `D1-GAP-13-07`：模組建立器選尺寸階段全部可選；正式**投放工作台**時，要根據實際資料內容與讀取密度再禁用不相容尺寸，並指出不相容原因。這個強校驗仍屬未完成設計。
8. `D1-GAP-13-08`：用戶期望「全部頁面可共用模組 Registry」仍需要 UI01–UI19 的功能索引、Producer、Permission、版本與 64 findings crosswalk 完整確認，不因這個 DOM mock 達成。

## 5. Human 設計 Gate 與後續合法工作

- 本版僅 `D1 v1.3 Candidate / Human Review Pending`；不是 D1 final closure。
- 待 Human 實際檢查全頁、快捷 ICON、模組版型 NxM、自訂模組建立、分類圖表與返回設定流後，再提出下一輪修正。
- D1 議題不需在本輪直接送 WO/Coding。後續 D1 收斂並結合 19 UI、6 MA10 Unit、API/DTO、Source/Cut/Quality、64 finding crosswalk，才形成 `B3_V1_UI_UX_DESIGN_REVIEW_PACKAGE` 候選。