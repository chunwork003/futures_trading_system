# Minimum Useful Automation / Adaptive Control — P00 候選

狀態：DEFINED_CANDIDATE / NOT_ACCEPTED；不啟用controller、不改既有policy/Program/authorization。

## 決策

`PAUSE_AUTO_IMP_003_AND_REPLAN`。Fresh master 的003 Rev2仍 NOT_AUTHORIZED；本決策是候選規劃，不建立或撤銷既有grant。先完成P00並使產品包可review/authorize，人工指示的產品工程不需要再先做任何automation包。自動化與V1 vertical slices交錯，只有移除已觀察blocker才排優先。

| 原包 | 候選處置 | 保留責任 |
|---|---|---|
| 003 Rev2 | A1保留cohesive、fresh recompile | exact authority、transition guard、first invocation/resume、禁止重派 |
| 004 | 移除重複quota實作；A1補差异tests | 用accepted Capacity2.2，不以舊V1 P90覆蓋manual P75/unknown watch |
| 005 | 合併至各責任包測試 | CE/REENTRY/TEL全部保留，非另造框架前置工程 |
| 006 | 全量campaign延後；A2先納必要歷史反例 | 歷史grant不可執行、review不等於acceptance；不刪歷史需求 |
| 007 | A3合併shadow比較 | old/new一致部分parity；policy差异明示審核，不能強迫舊錯誤route一致 |
| 008 | A2保留intake core並整合WORK流程 | exact execution/result binding、不可偽造telemetry、existing compatibility |
| 009 | A3合併read-only CLI | machine result、one writer、no invocation；此包原本沒有active dispatch |

逐項source acceptance text、Git blob及destination見 automation_mapping.v1.json。舊package forecasting numbers不是本proposal的新estimate。003 LOW_PROVISIONAL數百萬tokens與舊數萬tokens估值不具相同校準，不直接加總或用數字逼迫拆包。

## 三組增量與先後

A1：accepted snapshot/contracts/orchestration/capacity之上的pure authority/transition guard及必要反例。復用既有route owner，不引入第二套capacity或queue authority。可與產品包穿插；不自動擴003四檔scope。任何scope改變以successor重新compile，不原地覆寫舊authorization。

A2：result intake、execution identity、telemetry、review request與integration/acceptance proposal的同一交付鏈。真正review/acceptance actor grant是額外需求，不能以008來源包存在宣稱已授權。Input exact candidate/review findings，output immutable intake與有待授權的progression。Golden：duplicate result、錯execution、manual fabricated tokens、PASS後source drift、integrated不等於accepted。

A3：read-only preflight／shadow comparator／adaptive ranking及wake proposal。只有通過accepted promotion、measurable executor channel與explicit effect authority後，另加durable scheduler/controller adapter；此active adapter不是原009範圍。Activation需獨立review，不能借shadow PASS直接啟用。

產品前置automation新增數=0；controlled-autonomy尚需A1/A2/A3三組成果，但精確package數由cohesion/scope編譯決定，不假裝3組必然3次執行。每完成一組重新比較accepted V1 weight/token與automation節省的實測值。初始產品effort目標>=80%，非grant或安全豁免。

## WORK control loop 與權責

Rehydrate exact master/current/manifest/active policies/result/STOP → accepted resolve_route → 處理safety／unfinished／result-review-integration → 掃描可規劃candidate → filter → rank → proposal → fresh pre-effect recheck → permitted action → intake/measure → reschedule。

上層route順序不可由score改變。已invoked的unfinished execution只在原identity完整且未撤權時resume；缺invocation只能reconciliation，不能新建fake resume。Consumed但尚未invoked走既有first-invocation gate。任何unfinished或pending intake/review/integration阻止不相關新work。

目前policy blocked_lane_head_prevents_skip=true、at most one executable identity。以下ranking只對規劃候選排序，不能建立多份executable grants，也不能跳過blocked head。External blocker可先完成獨立read-only planning；真正切換lane需accepted successor/delegation明示允許，不是WORK自行猜。

## Deterministic ranking v1

每個候選：engineering_value、critical_path、context_reuse、correction_risk為整數0..1000，評分來源必記evidence/ref与版本；wait_age=min(1000,floor(ready_wait_seconds/604.8))。Cost inputs為該package forecast P75 total tokens及P75 seconds；normalizers固定1,000,000 tokens與28,800 seconds。Benefit=(4*critical_path+3*engineering_value+context_reuse+wait_age)/1000。Cost=tokens/1,000,000+seconds/28,800+2*correction_risk/1000。Score=Benefit/max(Cost,1/10)，以rational numerator/denominator比較，不依float。Tie：legal_ready_since最早，再package_id ordinal。

Hard filter：exact authority、dependencies、accepted lane policy、writer、provider、capacity route、external blocker、scope/readiness全須符合該dispatch mode。這些是boolean/enum veto，不是扣分。Forecast缺失時proposal=PREPARE_FORECAST，不用0假裝免費；這是ranking資料不足，不是把manual UNKNOWN available-capacity改成禁止。Capacity由accepted evaluator供應：manual UNKNOWN可ALLOW_WITH_WATCH；controlled-auto仍需promotion及P90。Weekly advisory、reset timestamp、queue/score均不能授權。

Ranking不是新canonical route；輸出僅 PROPOSE_PACKAGE/WAIT/REENTRY/REVIEW_FORECAST。實際dispatch前必重讀current evidence，使用既有authorization/lifecycle/CAS去建立唯一execution，不能憑snapshot score直接side effect。

## Wake、去重與未知 outcome

優先event-driven（result/review/provider/capacity/blocker變更）。Timer只觸發re-entry。背景unchanged blocker backoff序列5m、15m、1h、4h、12h；有meaningful evidence revision時reset。最大idle 24h；provider reset後加60s再取真provider evidence，不把clock當quota已reset。已知lease重新驗證期限可早於普通5m下限；到期事件立即停止新effect並re-entry，不用backoff延遲安全處理。

Wake取最早meaningful due event／lease deadline／max idle。UTC持久化，Asia/Taipei僅顯示；時間來源與觀測at/version明列。相同subject/relevant_revision/lifecycle_generation沿用accepted dedupe_key，重複timer coalesce。持久化schedule generation以CAS更新；兩個WORK不能各自schedule/dispatch。Provider adapter不支援所需精度時明示UNSUPPORTED，使用人工或已授權較粗wake；不得宣稱已自動排程。

Executor invoke是non-idempotent外部effect：先durable dispatch identity，再以平台支持的idempotency/lookup確認invocation。Timeout但無可靠receipt時OUTCOME_UNKNOWN → reconciliation，不能再invoke一次，也不能填造invocation evidence。新schedule不更動原execution lineage。Controller adapter的crash前後驗證是A3implementation acceptance。

## Bounded wave delegation 候選

Authority envelope須明示 owner decision/ref、program revision、exact package revisions/scopes/contracts hash、per-package correction budgets、expiry/revocation generation、allowed actors/roles、review/integration/acceptance權限及one-writer；無wildcard next-package或任意scope擴充。Wave可預先允許多個條件式工作，但任一時點最多一個可執行identity。WORK只在前包durable acceptance與dependency gate通過後materialize successor；reviewer不能接受自身candidate，executor不能自accept。

Review FAIL的scope-internal bug可在明示budget下修；public semantics／scope／authority變動回Architect。Quota/provider等待不消耗coding correction budget。耗盡budget只停止受影響包；若現行lane禁止skip，獨立新包只能提案，不暗自dispatch。

Human exception-only需：accepted baseline與bounded wave delegation、A1/A2/A3實證、measurable invocation/usage、獨立review資格、accepted promotion（含現行要求的5個manual成功樣本）、zero duplicate/fabricated resume/writer conflict、撤權/漂移/crash反例通過。這些目前未達；不得因本文件完成啟用。

## 驗收與R04 closure

每個原acceptance requirement都有mapping；政策差异明列；scheduler schema拒絕authority/effect升級；負例涵蓋safety/resume/result優先、illegal highscore、missing forecast、manual-vs-auto capacity、blocked head、重複wake、ambiguous invocation。P00只建立spec/offline oracle；controller effect、reviewer dispatch、排程工具設定不在本輪。R04 candidate可完成authoring，獨立review與整體P00 acceptance仍未完成。
