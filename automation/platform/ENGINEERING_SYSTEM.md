# Reuse、Evaluation 與 Measurement 契約

狀態：`CANDIDATE_AUTHORED / NOT_INDEPENDENTLY_ACCEPTED`。本文件集中承擔 OWNER-084 的24–30、38–39、43十項設計交付，並回應 owner第36–44、49–50、67–68、73–75節。Machine index 是 `engineering_system.v1.json`；event shape 是 `engineering_observation.schema.v1.json`；golden result shape 是 `golden_evaluation.schema.v1.json`。這些候選不取代既有 lifecycle、cost accounting、compiler、progress或current owner。

## 1. Template strategy

Template 是型別、來源與必填責任的起點。填表不創造 semantics、authority、PASS、receipt 或 acceptance。所有預填 status 為候選，未知值保留 null／NOT_AVAILABLE；missing public semantics 必須由既有 compiler 回報 PACKAGE_NOT_READY。每個 instance保留 template ID/version、parent source hash、填寫者 role、package/subject SHA，schema拒絕多餘欄位。模板變更先評估受影響 instance與compatibility，不回填舊 execution。

| Template | 唯一 reuse owner／起點 | 必填內容與驗證 |
|---|---|---|
| package | `docs/work/WORK_PACKAGE_TEMPLATE.md` + `package.schema.v1.json` | identity、authority、exact/protected scope、contracts、transactions、examples、impact tests、independent review、stops；沿用p00_compile |
| architecture decision | accepted ADR-001/002的decision結構 | context、alternatives、decision、owner、source、invariants、migration、failure、compatibility、review；status僅PROPOSED，不複製舊ACCEPTED |
| API contract | V1_CONTRACTS + p00_build_contracts | request/response、permission、idempotency、revision、error、retry、pagination；由single contract owner生成OpenAPI，不在template重定義 |
| state machine | V1_STATE_MACHINES | legal transition、authority、side effect、retry、crash、unknown、terminal/audit；沒有合法transition就停止 |
| migration plan | ADR-001第16/17節與V1_INCREMENTAL_PERSISTENCE | old/new owner、bounded adapter、data/DDL scope、rollback、compatibility、actual environment；migration execution另授權 |
| review | 已有focused review request | exact subject/file blobs/bundle、questions、counterexamples、limits、independent reviewer、disposition；draft不填PASS |
| incident | 本文件第6節 | symptoms、source、blast radius、cause或UNKNOWN、detection、resolution proposal、regression；治理/環境問題不改名成implementation RF |
| release | V1_PROGRAM六旅程 + program_baseline journeys | release SHA/manifest、六條同版本evidence、environment、limitations、operator/runbook、independent acceptance；缺一條不領取release credit |
| execution result | accepted CODEX kernel與cost contract | actual subject/scope/commands/environment、PASS/FAIL/NOT_RUN/BLOCKED、corrections、source-bound actual cost；模板不填execution ID或claim |
| handoff | 已有handoff.schema與p00_compile | fresh baseline、package/role/state、authority、completed/evidence/findings、next/stops；沒有next role grant只能planning handoff |

文檔模板共用此欄位規則，不複製十套提示詞。已有machine schema的種類以既有schema為準；其餘doc模板依上表獨立審查，不宣稱已machine qualified。

## 2. Generator strategy

先由Architect決定public semantics並固定來源，generator只處理格式、引用、closure、hash與重複欄位。輸入綁exact Git snapshot/contract revision/配置hash，輸出具generator revision、source hashes、deterministic content hash。相同inputs必須得到相同semantic output；換行transport不充作新語意。更新先dry check，再exact paths；不得自動改accepted current、grant、claim、review disposition、database或external service。

| Artifact | 既有reuse component | 本次處置 |
|---|---|---|
| package/handoff/context | p00_compile、p00_context、existing schemas | 保留唯一編譯者；不建立第二個compiler |
| OpenAPI/shared DTO | p00_build_contracts | 保留single contract source與--check；不手寫第二份DTO |
| reading pack／source index | p00_context_pack、p00_requirements | 保留source closure與reading obligations；index不免除read receipt |
| progress report | p00_progress | 保留空gate/fail-closed intake；generator不製造credit |
| test/review matrix | package verification/examples及本registry golden requirements | 先產生候選matrix；oracle與impact由engineer/reviewer決定 |
| migration checklist | migration template／package scope | 只列清單，不生成可執行DDL或自動migration |
| current projection | accepted current owner，candidate current-intake契約 | 等A2完整registry/read/CAS整合受審，沒有新current writer |
| TS/C# client | shared OpenAPI + P02 lock gate | deferred tooling qualification；不下載／安裝或浮動版本codegen |

生成器驗收檢查 determinism、negative inputs、source/hash/ref closure、--check drift、allowed/protected paths與one-owner。這些檢查不是生成後產品的compile/runtime/API acceptance。

## 3. Pattern／reference strategy

Pattern記錄責任、步驟、invariants、反例、source reference、相容版本與test impact。Pattern ID不等於已驗證product feature；只能在同一contract/transaction/authority context重用。變更先查既有capability/Skill，再parameterize→compose→extend；不因新package複製一個Skill。Machine registry列出少量bounded reference slices：

- Dataset import／list：P01 identity/quality fixtures與P02 query DTO。保留immutable version、duplicate/conflict與coverage；未實作完整importer或browser slice。
- Research submit／poll／result：P02候選API與P03 durable job設計。idempotency/lease/cancel/artifact boundary明確；test-host fixture不可冒充durable worker。
- Simulation command／audit query：V1 API/DTO/currentness設計。Python是economic owner，ASP.NET只授權與workflow，React投影；command需final cut/permission witness。
- Recovery／migration：既有accepted GAP08 closure + R01 outer-cut設計。保留expected/actual、unknown≠flat與writer fence；isolated舊PG evidence不涵蓋新jobs/decision tables。
- Review fix／incident：exact subject findings→bounded correction→targeted impact→fresh independent re-review。新semantics返回Architect，consumed execution不redispatch。

每次使用記錄 pattern ID/revision、參照subject、適用判斷、偏差及驗證。Reference分為 `ACCEPTED_EXISTING_SCOPE`、`CANDIDATE_DESIGN`、`OFFLINE_SPEC_ORACLE`、`UNIMPLEMENTED_PRODUCT_SLICE`，不得由存在性提升級別。

## 4. Evaluation／Golden-task framework

每個golden task固定task family/fixture hash、source snapshot、contract/oracle revision、environment、允許scope、expected semantic outcome、counterexamples、required review及cost coverage。Baseline與candidate可以有不同implementation/model/tool版本，但input/oracle/environment應相同；不同者先分cohort並列confounders，不能直接宣稱improvement。至少包含以下九類：

| ID | Task family | 正向oracle／必要反例 | Actual qualification gate |
|---|---|---|---|
| G01 | architecture comprehension | 正確single owner／next route；stale current、candidate冒充grant | fresh isolated semantic review |
| G02 | small feature | exact bounded delta與tests；scope擴張、unknown behavior | independently accepted implementation |
| G03 | cross-layer feature | schema/permission/DTO一致；browser直連DB、第二economic owner | actual Python/BFF/browser integration |
| G04 | bug fix | 可重現cause及最小修正；測試只鏡射patch、將新semantics藏成bug | original failing fixture + targeted independent review |
| G05 | migration | bounded compatibility/rollback；wrong schema、unfenced writer、crash | disposable actual PG/crash tests under separate grant |
| G06 | review fix | bound finding/subject與budget；stale PASS、consumed redispatch | fresh narrow independent re-review |
| G07 | recovery issue |完整cut/currentness/unknown；same revision new evidence、ABA、missing coverage | actual durable/concurrency/crash evidence |
| G08 | API change |request/error/retry/idempotency/revision；wire/domain混用 | contract + cross-language runtime acceptance |
| G09 | frontend change |user journey/error/accessibility/projection；UIeconomic authority、loading當success | actual browser/user journey on fixed release |

本次只有registry/schema/specification oracle checks，九類的實際model/task qualification一律 `NOT_RUN`。完整platform單元測試不是九類golden成果，也不能證明新模型更快。未提供environment的task為BLOCKED_ENVIRONMENT，tool失敗為TOOL_FAILURE，缺public semantics為DESIGN_INCOMPLETENESS；三者不算semantic PASS或implementation RF。

每trial保存artifact hashes、raw judgment、pass/fail/not-run/blocked、classified findings、coverage與review status。單task改善不能覆蓋critical counterexample failure。有限mandatory fixtures全PASS且fresh independent reviewer確認exact subject後，只取得該task/cohort/risk範圍的資格；不自動提升整個Agent/Skill、grant dispatch或LIVE。

新model/tool流程：same golden baseline→cost/first-pass/semantic comparison→shadow→bounded adoption→independent promotion。平台registry更新有version/compatibility/rollback；重用測試evidence另需SHA/environment/dependencies/inputs/impact proof，不能靠名稱相同。

## 5. KPI 與 telemetry semantics

Telemetry的forecast由WORK提出、actual由實際producer記錄、acceptance由獨立review/intake owner提供。三者來源分開。Append-only event identity + canonical payload hash：相同ID/內容是replay，不重算；相同ID/不同內容是conflict。每event綁task/package revision/attempt/actor/subject/contract/environment/recorded_at/source refs。Later correction/invalidation追加新event與supersedes，不覆寫。Actor identity與source/hash的shape檢查不證明可信producer；真正collector、durable store、receipt/coverage/CAS integration屬後續A2/R05 implementation。

Measurements保留 OBSERVED／ESTIMATED／NOT_AVAILABLE／NOT_APPLICABLE，value使用非負finite decimal string或null。Unknown不是0。tokens另列input/cached/output/total與coverage，不混用其中一項或不同actor window。Account quota只能以SHARED_ACCOUNT_PROXY的percent保存，不能推導actor tokens／task cost。Time另列wall elapsed、active engineering、test耗時、review wait、Owner wait、external wait；不同clock/overlap不直接相加。Bytes不冒充tokens；差值/比率用Decimal，display才round。

| KPI | population／公式 | 缺資料／限制 |
|---|---|---|
| accepted work/token | same frozen revision、qualified accepted weight / complete actor-window total tokens | 未完成trusted acceptance intake或tokens coverage→UNKNOWN；不能用127候選權重或quota |
| accepted work/execution | 同scope accepted weight / completed eligible invocations | 不能用commit/package/file數；architect drafts另列 |
| first-pass acceptance | first independent review PASS的cohesive packages / 有first review disposition packages | 未review不當FAIL；後續RF PASS不回填first-pass |
| findings/package | 同review scope分類finding數 / 已review packages | classification各列；withdrawn/duplicate不重計 |
| architecture RF rate | 因缺/衝突semantics而回Architect的review outcomes / reviewed outcomes | 不把tool/context/fragmentation全部算RF |
| context size／reuse | 實際讀取bytes/tokens；proved reusable content /同cohort required content | source closure/receipt欠缺時reuse=UNKNOWN，不因cache命中就qualified |
| correction count | implementation/RF scope-internal cycles分別count | tool/environment retry另列；不reset inherited budgets |
| human intervention | 需要human decision的eligible attempts / 已知完整attempt population | 自動review拒絕與human答覆分開，unknown population不估rate |
| forecast accuracy | matched unit/scope forecast與actual的absolute error；relative error=abs(actual-forecast)/actual | actual0且error>0時relative undefined；unknown/estimated actual不當0 |
| lead／cycle time | request→acceptance；first eligible execution→acceptance | wall elapsed含wait，active work另列；未accept是censored，不當0duration |
| escaped defect rate | acceptance後發現的獨立確認defect / qualified accepted population | observation window/version一致；沒有完整追蹤不能宣稱0 |
| repeated defect rate | same validated root-cause family重現 / 已classified confirmed defects | 不能只用相同error text分類；unknown root cause另外列 |
| Skill invocations/success/failure | exact skill revision、task/cohort、qualified outcome人口 | shadow/schema PASS不是qualified success |
| Skill token/time saving | paired same-input/oracle/env accepted outcome的baseline-candidate差值 | absence、model changes、different scope有confounders→UNKNOWN |
| Agent first-pass/correction/context/handoff | exact logical role/model/provider/contract與eligible handoffs | role registry存在不等於agent invocation；沒授權不生成agent/effect event |

Population的完整性需要可信coverage frontier／positive empty-result proof。schema中的宣告旗標不能自證完整；本次offline oracle只用明標synthetic samples。Trusted progress/qualification intake尚未建立，因此accepted weight、effectiveness與promotion report保持UNKNOWN／NOT_QUALIFIED。Raw measurements、spec calculations與qualified KPIs使用不同status。缺資料分母、0分母和complete empty population都保留不同理由。

## 6. Optimization loop／backlog

Lifecycle：OBSERVED→CLASSIFIED→ROOT_CAUSE_PROPOSED→IMPROVEMENT_PROPOSED→SHADOW_EVAL→INDEPENDENT_REVIEW→BOUNDED_ADOPTION→VERSIONED_PROMOTION；unresolved oracle/environment停在NOT_RUN/BLOCKED，不跳到PROMOTED。這是提案流程，不是新的accepted controller state machine。

Backlog必填 observed problem/source、frequency與population、cost/coverage、root cause或UNKNOWN、improvement、expected gain/confidence、implementation cost/risk、measurement/oracle、affected contracts/skills/agents、version/compatibility/rollback、owner、scope/grant dependency。第二次同類錯誤須評估contract/fixture/test/generator/context/package seam；第三次僅加prompt提醒不能算系統修正。

ROI粗估 = expected per-use saving × justified reuse count × estimated error reduction / implementation cost；units與uncertainty分開，不把seconds/tokens/weight相加。缺baseline或cost保持UNKNOWN。優先處理產品critical path blocker、反覆correction且可重用的低risk改善；產品effort target≥80%只有實測後才可報。沒有metric的architecture美化不搶主線；有額外scope/effects需獨立package/grant。

Candidate例：current context packs超128KiB與complete intake UNKNOWN已有source evidence。改善方向是source-selected reading/receipt/CAS integration；expected token saving與actual ROI仍UNKNOWN，不放寬compiler gate、不因tool schema PASS啟動controller。

## 7. D0–D5 roadmap與交付驗收

| Phase | 產品相伴工作 | Exit evidence | 此刻狀態 |
|---|---|---|---|
| D0 inventory | P00復用既有core/skills/tools | fixed source inventory、duplicates、scope分類 | CANDIDATE_SOURCE_INDEXED，完整歷史語意仍缺 |
| D1 standardize | P00 contracts/bootstrap/templates | schema/fixtures、source closure、independent baseline review | CANDIDATE_AUTHORED_NOT_ACCEPTED |
| D2 reuse | 已授權P01/P02/P03 slices | compiler/context qualification、bounded reference equivalence | prototype components存在，產品slices未執行 |
| D3 automate | 結果intake/review/integration必要gate | durable producer closure/receipt/CAS、one writer、revocation/negative tests | NOT_IMPLEMENTED_NOT_ENABLED |
| D4 measure | accepted product deliveries提供samples | complete scoped telemetry、golden comparisons、forecast calibration | NOT_QUALIFIED，不將account quota當task cost |
| D5 optimize | measured reusable gains | no semantic regression、independent limited adoption/promotion | NOT_QUALIFIED；不可跳過D4 |

各plane/domain的phase獨立；不要求所有D5完成才交付V1。D0/D1 design不領取runtime maturity/工程credit。工程系統十項交付的candidate authoring驗收是：typed/semantic contract有owner/inputs/outputs/failure/compatibility、原始義務逐項source links、schema正反例、既有source reuse與保護範圍、remaining qualification明確。P00 ACCEPTED仍需fresh independent review；實際effectiveness、可信intake、migration、browser/DB/模型評估及controller activation未由本次授權。
