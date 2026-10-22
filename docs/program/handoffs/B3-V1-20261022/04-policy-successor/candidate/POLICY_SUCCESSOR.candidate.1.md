# B3 V1 有界連續施工政策補充 — successor.1（候選）

Subject: B3-V1-CONTINUOUS-POLICY-SUCCESSOR-01/candidate.1
狀態：CANDIDATE_PENDING_FRESH_NARROW_REVIEW_AND_EXACT_OWNER_ADOPTION。
本文件是既有 WORK／CODEX 的政策附件候選；不是 Machine Policy 啟用、Current State、Compiler、Controller、Grant 或 Qualification Receipt。原 addendum.v1、原 119 檔及全部接受／審查證據不變。來源 raw Hash 見 SOURCE_BINDINGS.json。RAW SHA256 與原既有 CANONICAL_JSON_SHA256 各依原用途使用，不互換。

## 0. 問題、約束、方案與選擇

原審 F-01／F-02／F-03 只影響「新增政策可否採納」，不推翻 B3、U01、96 Unit 規格或原始 DAG。方案一是建立全面 pending-review 例外及候選串接；方案二是先精確規定額外 advisory 彙總、有限逐項 Owner 決策容器，維持候選串接禁止。本 successor 選方案二：降低權威擴張及返工風險；不削減完整 B3 功能範圍。

所有 MAY 都必須先有現行制度允許的 exact Authority、適用 Qualification 及 Grant；本候選不使任何實際工作 READY。UNKNOWN、缺件、矛盾或無可信來源皆 HOLD 受影響用途。不得從模型名稱、NEXT、queue 順序、Worktree、離線 PoC、Review PASS 推導執行權。

## 1. F-01：Review 類型、可延後範圍與 parked 充分條件

### 1.1 分類及優先規則

| 類型（衍生分析標籤） | 來源與要求 | 可否延後 |
|---|---|---|
| 原 mandatory Unit／Wave／獨立 Review／Result Intake／Integration／Human Acceptance | exact WO、accepted Source、原 Kernel／Policy／Receipt 規定 | 不可越過原 required-before Gate |
| Source／Context／Executor／Identity／Continuity／Result／Intake 使用資格，安全／權威／受保護架構決策 | 精確適用 Source 與使用範圍 | 不可越過原使用 Gate |
| 額外 advisory 高階 Stage 彙總 | 必須有具名、固定 Hash 的來源及 Owner 分類，證明只是額外彙總，未取代任一原義務 | 僅符合 1.2 才可記錄為 PENDING observation |
| UNKNOWN／分類衝突／只因稱為 Stage、R0–R3、Ultra review | 無充分權威證據 | HOLD；不可推定 advisory |
| Provider 中斷成本回顧 | 原 execution_cost_contract.v2 的精確特例 | 只能沿原特例；不可泛化至產品或語義 Review |

R0–R3 是原交接的 test aggregation，原表內所有 required qualification、Unit cases、Wave/full regression 與 Human Gate 均保留。沒有任何一個 R0–R3 標籤在此被概括列為可延後。尚未明確分類的現有 Stage 請求預設 UNKNOWN；新增額外彙總須明列 advisory 的來源、範圍及 deadline 才能適用。

### 1.2 全部必要條件（非任一條件）

記錄可延後 observation 前，WORK 必須以實際 durable 證據同時證明：

1. Exact WO／Execution／Source readset／Result ref／完整 body Hash／原 Review Subject 已固定，能實際讀回；ref、正文、schema/revision/hash 一致。
2. 原 Execution 已依原生命週期完成、終止或合法封存；不存在未完工、Invocation UNKNOWN、待 resume、競爭 Writer、Writer release UNKNOWN。
3. Writer 已有 durable release；沒有未解 safety／authority／source-currentness 矛盾。不能僅以程序已退出推論 lock 已安全釋放。
4. 本筆只是額外 advisory。所有目前已到期的 mandatory Review／Intake／Acceptance／使用資格，均已有適用正式證據；尚未到期者保留原 Gate，不能假稱完成。
5. Ledger 明列 review_type、分類 Source/Hash/selector、Scope、WO/Execution/Grant refs、Result/Commit/Hash、source/readset、upstream assumptions、direct/transitive Consumers、mandatory 原規則、required_before、Owner、原因、優先序與 revalidation。
6. 最遲補審為本 advisory 對應的 Stage 結論／promotion／integration／正式 dependency use／Human Acceptance 決策之前，或原來源更早的門檻，取較早者。未到期不表示相關原 mandatory Gate 可略過。到期未審阻擋該用途。
7. 原生 routing 仍由現行 entry policy 重新解析。若解析為 SAFETY_GOVERNANCE、RESUMABLE_UNFINISHED_EXECUTION 或 PENDING_RESULT_REVIEW_INTEGRATION，必須先處理原 route／STOP；不得將該項改名 parked 後從 evaluator 隱藏。

「parked」只描述衍生 Ledger，不是新 Machine enum，也不解除 native pending Review。上述全部成立也只代表可記錄 advisory PENDING；不產生 eligibility PASS、Accepted、Progress credit 或下一張 Grant。

### 1.3 可繼續與不可繼續

只有原生路由已合法解析為 AUTHORIZED_NEW_WORK，且下一 Unit 的所有來源、已接受依賴、適用資格、獨立授權、成本與單 Writer Gate 都通過時，才能依原流程開始一個新的合法 run。每個 autonomous run 至多一個 mainline Package，結果固定後保留原 Review Barrier；不能在同一已完成 Invocation 直接 NEXT。

若只有 advisory 欠審而原生 evaluator 尚無支持的 continuation route，保持 HOLD，準備 exact Owner／policy integration decision，不強行宣稱已可連續施工。這不建立「任何 pending 永久阻擋所有不相干工作」的新規則；每次均以原適用 route 證據判定。

## 2. F-02：有限批次 Owner 決策與逐 Unit 原生授權

### 2.1 容器定位與 exact 成員

Bounded Batch Approval 在本版只表示 Human 一次精確批准有限的逐項決策集合。Envelope 是決策證據容器／索引，不是可反覆消耗的 native Grant，也不是新的 Authority、Registry 或 Controller。

Owner 決策前必須固定：
- envelope ID、revision、raw Hash、有效起訖時間／時區、Owner 決策證據、最大有限成員數及完整具名集合、集合 digest、共享停止條件。
- 每個 member 的原永久 Unit ID／plan revision／Feature、受支持的 native Program/Package binding、exact WO ID/revision/raw Hash、獨立 Authorization ID/revision/exact binding、Source/Contract/Schema/DTO refs/hash/readset、允許及保護檔案／preimage、Executor/Profile/intended-use Qualification、Result/Review/Intake 路由及必要案例／修正上限。
- 成員依賴的 Accepted Result 或已合格 scoped reuse，含來源、scope/schema/profile/operation/cut 的適用證據。未來 Result 尚不存在不能被 envelope 宣告 satisfied。
- 逐項硬預算及總硬預算、維度／幣別／資源邊界、回收與撤權方式、Writer 與 Invocation 限制。實際限制取適用的較嚴者。

不得使用 wildcard、整個 queue、隱含後繼 Unit 或自動加項。相同 Unit/WO/Auth 重複、同 ref 不同正文、無法唯一比對成員集合或不受現有 native contract 支持的 Program/Package binding，皆拒絕該容器的執行用途。

若未來 WO、preimage、依賴結果、Profile 或預算仍 UNKNOWN，該項只能是規劃成員，沒有當前 native execution authorization。待完整後必須取得其精確 Owner 決策；不能默認已批准任意「最新」內容，也不能由 WORK 自簽新 child authority。本版不提供以晚填 Hash 自動生效的通用條件授權。

### 2.2 與現有資料形狀的對接

不新增 AuthorizationRecord、WorkPackageRecord top-level 欄位，不修改 closed Pxx package schema，不把 MA/PK alias 直接塞入不支援欄位。只能使用原制度已接受且適用的 bridge／manual binding，固定合法 native records。Envelope 可附於既有 decision_evidence 可承載的精確來源參照；若 loader/validator/Intake 對用途不支持，HOLD，須另獲精確 integration 授權，不以 FrozenSection 可容 nested data 推定語義已獲准。

每個 member 必須在 Human exact 決策下物化自己的 native AUTH／WO；本版不建立任何實際 AUTH。容器不被用作 reservation／dispatch／Invocation 的 authorization_id。衍生 member ledger 只讀原生 durable records，不得回寫或與其競爭。

### 2.3 消耗、中斷、撤權與成本

每 Unit 分別依 authorization_lifecycle.v1_1 的十步 dispatch 順序執行：
FRESH_AUTHORITY_RESOLUTION → FRESH_ELIGIBILITY_EVALUATION → ACQUIRE_GLOBAL_RUNTIME_WRITER_LOCK → ALLOCATE_EXECUTION_ID → DURABLY_CREATE_EXECUTION_RESERVATION → STATE_TO_RESERVED → RECHECK_LOCK_HEAD_AND_BINDING → MARK_DISPATCH_COMMITTED → STATE_TO_CONSUMED → INVOKE_EXECUTOR。

- A 的 AUTH 被消耗不表示 B 已消耗、已執行或已接受，也不授權 B；A 的 consumed AUTH 不可供 B 使用。Envelope 自身永不被當成可重派的 Invocation Grant。
- 部分完成保留各 native 狀態；剩餘 member 不自動 READY。下一次 run 必須 fresh resolve 原 priority／Review Barrier、依賴與成本。
- 只有已 invoked 且證據完整的同 Execution 能在原身份／scope／Grant／budget 下依法 resume。不得新建 Execution、reservation、dispatch 或補預算；Invocation 缺件是 STOP_NO_BACKFILL。
- Owner 撤銷 envelope，未啟動項全部停止；既有 consumed/running 項按原 safe-stop/revocation policy 處理，不抹除已發生事實。只撤單一 member 則停止該項及依賴其無效輸出的用途；共享權威／安全／envelope 完整性問題停止整批。
- Source／preimage／Revision／Profile／Qualification／Authority 漂移或過期、缺失／UNKNOWN 結果、Writer 衝突、成本超限，停止受影響 member 及其 Consumer；不可重算局部 hash 後沿用舊決策。
- 每項及整批硬限制均須有限（時間／修正次數／API 金額或其他適用可量測維度），外部 API 0 就永遠不得支用。Forecast 可 UNKNOWN＋原因；硬預算若需 UNKNOWN 特例，必須 Owner 精確接受並仍有其他有限安全界線，不能等同無限授權。
- 逐項開始前保守預留可量測的剩餘上限；總餘額不足則 HOLD，不超賣總額。若無法可靠限制共享資源，停止該資源用途，不以 Provider 百分比假裝精確 Token。
- correction、review-fix、tool retry、provider pause／resume 分開；不得跨 member 挪用未用額度或重設次數。原具名 WO 的 capacity2.2 conditional review-fix 權不轉授為一般 Batch。
- WORK Forecast、Executor Actual、Variance、Provider proxy 與 billable cost 分開，無可靠數據為 UNKNOWN。回顧／Review 不能創造新的 authority。

### 2.4 必須通過的有限集合例子

集合 {MA02-U01, MA02-U05} 只作政策反例名稱，沒有任何實際 Grant：
1. 若兩項都具已批准 exact native authority 且 A 可執行，A 只能消耗自己的 AUTH。
2. B 若尚無 A 的 Accepted Result/reuse proof 或 exact own binding，B 必須 HOLD；有 envelope 也不得執行。
3. A 完成不重設其 consumed 狀態；B 後續必須先滿足原 Review/Acceptance、依賴、自己的 qualification/native authority/currentness 及成本。
4. 若 B 的未來 result/preimage 尚不可能精確固定，本版只保留規劃項；完整後仍需新的精確批准，不偽造可提前全面授權。

## 3. F-03：明確維持 candidate-to-candidate 禁止

本版不開放「未審 candidate 供下游 candidate 實作」；採原 Reviewer 允許的縮限方案。

Lane A 和 Lane B 所需上游都必須有 exact Accepted Result＋外部 Acceptance，或原制度允許且已取得的 qualified scoped reuse。候選有 Hash、可讀版本、獨立 candidate Grant、隔離 Worktree、同一 Batch 或較低風險，都不能代替該條件。不可藉宣稱 input 是 Mock 而實際消費未驗證高風險商業語義。

可唯讀分析候選、列出 direct/transitive Consumer、準備規格；沒有明確實作授權仍不得寫產品。獨立且所有 required 上游合格的 Lane B 工作，仍須自身 candidate Grant、合格 Profile／Context、單 Writer、成本與禁止 promotion 條件。

上游失敗／新修訂：原始歷史 Receipt 不改寫；對該修訂的未來使用重新做影響閉包及資格判定；受影響下游 HOLD。候選永不自動 Accepted、合併正式主線或升 Authority。

若未來要開放候選串接，另需具名版本／用途授權／來源取用／傳播／失敗處置／promotion barrier 契約及 Fresh Review＋Owner Adoption。本次沒有此採納聲明，也不建立這類新能力。

## 4. Reviewer、補審、Kernel 與 Owner Gate

合格替代 Reviewer 可不是 Ultra，但須與作者／作者上下文隔離，固定 exact subject/source/readset，符合風險及原資格；工具名稱不代表合格。若無適用資格或工作階段不可用，維持 PENDING。作者符合性檢查不冒充獨立 Review。

補審使用原 Deferred Review Ledger／Review Dependency Impact 作衍生索引：優先最早未驗證共享前置及高風險 consumer，合併相容 review subjects；逐個保留 Verdict。只對受影響閉包重驗，不能取消原 mandatory full/Wave checks。Catch-up 產生的是 correction candidate，不自發修改產品或新 Grant。

Kernel 補充只有：重新讀原 Authority → 解析原 priority → 確認 advisory observation 是否依1.2完整 → 選擇已有 exact authority 的 Unit → 原 native流程 → Result固定 → STOP原Review Barrier。NEXT只觸發下一次re-entry，不是同Invocation自動dispatch。不得建立第二套Controller或狀態機。

本版本僅可依 fixed candidate manifest 提交 Fresh Narrow Review，之後供 Human 作 exact Owner Adoption；兩者不等於 source integration、policy activation、qualification或coding grant。若 native來源整合另需權限，保持原policy有效，不能單靠本文件被批准就直接跑新行為。

## 5. 驗收與不變事項

Finding Closure Proposal 中的 F-01／02／03 只能標 AUTHOR_FIXED_CANDIDATE，直到真正 Fresh Reviewer 判斷；本詞不是 Machine state。必審：
- 原三項反例與本政策每個必拒條件。
- 原 native routing、dispatch順序、單Writer、原Result hash／Intake／Review／Acceptance無變。
- 精確有限容器對 A消耗/B未授權、未知未來輸入、中斷、撤權、過期、總成本的處置。
- 候選串接明確禁止，沒有假造正向允許案例。
- 原96/95/19/364/578、H六檔、Q119檔、既有接受／審查來源 raw bytes全部保全。

政策表格／反例是設計 Oracle，不是產品測試或真實 Qualification。所有 Runtime、Host/C3/C5/C6/P00、SQL、Broker、Restore、Controller、Git發布及單Unit Coding仍依原適用正式Gate。

