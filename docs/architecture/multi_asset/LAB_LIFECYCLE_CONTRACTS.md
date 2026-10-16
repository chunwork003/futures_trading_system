# LAB Lifecycle／Source Archive／Builder／Analyst／Observation Contract

Revision `candidate.4`；原 Owner E Feature/Strategy/Library、F Research、Artifact Provider、N/O Application/UI。本檔為 RCG03 的有界候選 companion，承接 PRODUCT-S4-01～06；不是新的執行、經濟、進度或 Acceptance Owner。所有實際操作均 **NOT_IMPLEMENTED_OR_NOT_VERIFIED_BY_THIS_CORRECTION**。

## 來源、責任及修訂邊界

固定前代為 `MA-ARCH-REVIEW-v3`，Bundle Manifest raw SHA256 `3111560aba66e5b3d8d92659c64b2b95b5dc6c034578c9bd8442cdc8af7c65b1`。Rev2 MD raw SHA256 `1dbbbe4205c74a21c068c9efced5b1452d5b0bdd6acccd2d7c69db1bf94da79e`：A1 四空間 13～16、STANDARD 53～58、不可 OFF／S001／AI／例外 68～78、模型 105～114、反例 139～143、Wave 147～158。Rev3 MD raw SHA256 `721fac6ef5398158ceb233b4c00c24289151d996331cfd6594c0419f2c9e01b2`：外來碼完整歸檔 25～46、Provider 48～53。私有原文由 Source Manifest／本機不可變 Capture 引用，不匯出到 Public Git。本輪原接受 R01／R03／R04／R05／R07、GAP08、原 LAB Wave 編碼及 S14/S15 Future 研究 lineage 均不改寫。

`MODEL_CATALOG`、`TYPE_VARIANTS`、`API_CATALOG`、`EVENT_CATALOG` 的 candidate.4 successors 為本契約的 named wire shape。舊 immutable revision 按原 schema 解讀；不能把 candidate.4 欄位無聲加到原 Review Subject。新的 `ContractRef` 保留 original Entity ID，Revision ID 改版，canonical hash 再計算。

所有 POST 使用 MA10 的 CommandEnvelope；認證得到 actor／scope，前端不得宣稱 actor 或權限。Receipt 先於副作用、同 scope/command ID/hash 重送同結果、同 ID 異 hash=409、stale generation=409、語義非法=422、未授權=403、原文缺失=404/MISSING_CONTENT、provider unavailable=503（可能有副作用時 UNKNOWN＋receipt）。GET 使用 snapshot/query/scope-bound cursor，續頁 query/scope/snapshot 不一致=409；私有檔案名稱、原 URL、作者／路徑透過權限化 metadata artifact 引用，不因 GET 暴露。

## C1 — SourceInbox → AST Analysis → Human Archive

### 輸入／輸出與唯一 Writer

- `SourceAnalysisRequest → SourceAnalysisReport`：E Research 提交原 `SourceInboxItem` 的 exact bytes、tool/budget/catalog refs。SourceAnalyzer 只 AST parse；保留函式、類別、參數、輸入輸出候選、依賴、line ranges、side-effect findings、多標籤分類及 duplicate/variant candidates。AI 摘要只是建議。從未 import、exec、安裝套件或接觸網路、正式資料庫、Secrets。
- `ArchivePlanRequest → ArchivePlan`：由同 E Research 提出分類、正規檔名、Provider、安全 locator、預計 COPY／MOVE／DUPLICATE／REJECT。只有預覽，沒有 filesystem 副作用。需顯示原檔 metadata、hash、bytes、來源／license state、安全分析、分類與目的位置、existing target 狀態、duplicate/conflict、是否保留 inbox 原檔。
- `ArchiveExecuteRequest → ArchiveOperationReceipt`：只接受覆蓋 exact plan、原 hash、target generation 的 Human decision receipt。Artifact Provider 依已授權儲存 policy 操作 bytes；E Research 保存 manifest/journal 與 receipt，不在 filesystem 另建 Feature truth。Archive 成功不等於 Feature qualified，更不等於 Library／PAPER／LIVE admission。

`UNKNOWN` license 有一份 explicit unknown source/licence record，原 `SourceInboxItem.licence_ref` 仍可引用它；不以空字串或缺省「允許」通過。可以人工隔離保存以保護原文，不能以 archive approval 取得重散布、執行或 Feature qualification。`FeatureDefinitionRevision.implementation_ref` 只能在 original E qualification adapter 驗證 exact implementation/security/licence scope 後接受。外來implementation以 `source_qualification_ref→FeatureSourceQualification` 綁exact archive receipt、bytes、qualification profile、licence/sandbox/review evidence；只 `QUALIFIED_EXACT_SCOPE`可作runnableLibrary，`NOT_QUALIFIED/UNKNOWN`不能執行。既有accepted feature仍按原receipt exactscope沿用，不從archive自簽新qualification。

### Plan／Effect state table

| 條件／狀態 | 允許動作 | 結果及恢復 |
|---|---|---|
| READY_FOR_HUMAN | Human 確認 exact plan | PREPARED journal；只使用 approved provider/category/filename |
| EXACT_DUPLICATE | Human 確認 duplicate relation | DUPLICATE_RECORDED；引用已驗證 immutable content，不合併 source identity／license |
| HASH_CONFLICT／INVALID_PATH／MISSING_CONTENT／QUARANTINE | 拒絕 archive effect | source 保留；不能以改名掩蓋同名異 hash conflict |
| PREPARED | 建立目的檔 | CreateNew，永不覆寫；固定 source/target generation，race lost=409 |
| TARGET_CREATED | Flush／完整 bytes hash/size verify／durability proof | 成功 VERIFIED_ARCHIVED；失敗 FAILED_SOURCE_RETAINED／HASH_CONFLICT |
| VERIFIED_ARCHIVED + MOVE_AFTER_VERIFIED_COPY | 僅 approved cleanup inbox copy | 原 immutable capture 仍保留；cleanup 失敗記 FAILED_SOURCE_RETAINED，可獨立 retry |
| UNKNOWN_NEEDS_RECOVERY | 讀 durable journal／exact destination content | 同 hash＋proven operation ownership可完成 receipt；不同 hash conflict；無可信 proof不再搬移／不刪原文 |

MOVE 定義為 **先 immutable capture，再 CreateNew copy 到 archive、verify、durability receipt，最後受控清理 inbox 副本**。跨 Provider 不假設 rename 原子性；CreateNew、fsync/rename/reparse 行為的真正 Windows qualification 留後續。任何失敗前 source original／capture 必可取得；不把 mtime、檔名存在或 Hash 字串當原文存在。原檔 name/path、new name、provider locator、scan/tool revision、分類、Human actor/ref/time、license、dependencies、hash/size、effect/cleanup outcome 都保存 immutable audit artifact；未列入 SQL index 仍需 MA13 Capture Journal / Inventory backup closure。

安全 locator 只能 Provider allowlist namespace；拒絕 `..`、absolute/UNC/device path、ADS、危險保留檔名、symlink/reparse chain escape、source-target alias。不得在本轮直接掃描外部使用者資料夾或執行歸檔。

### UI／API／服務

UI04 Source Library 提供 Scan、Analysis view、分類覆核、Plan preview、Human Confirm、Recovery status、Duplicate／Conflict link。服務函式 `SourceAnalyzer.analyze`、`ArchivePlanner.preview`、`HumanArchiveService.execute_or_reconcile` 的 output 都有 exact named models。新增 API `analyzeInboxSource/getSourceAnalysis/createArchivePlan/executeArchivePlan/getArchiveOperation`；原 `captureInbox/dispositionInbox` IDs 保留，`dispositionInbox(ARCHIVE_EXACT_BYTES)` 必 delegate 同 Archive engine，不能第二套搬移程式。

## C2 — Builder variant／Switch／Immutable Graph-Code-Snapshot

`GraphNode.node_kind` 為 FEATURE／RULE／SUBSTRATEGY／SAFETY，`BuilderNodeBody` discriminator 對應 exact definition revision，不是 `split` 或自由 metadata。

| Variant | Definition／責任 | 開關與資格 |
|---|---|---|
| FEATURE | FeatureDefinitionRevision；pure calculation、typed ports／units／lookback | LAB可選 OFF；OFF 從有效 graph 移除，重驗 consumers；不能發 FLAT/EXIT |
| RULE | RuleDefinitionRevision；ENTRY／EXIT／STRATEGY_RISK | 最後一個有效 role 不可 OFF/remove；UI禁用、後端422 |
| SUBSTRATEGY | SubstrategyDefinitionRevision；完整 nested graph | 展開完整 closure 檢查，不能由「含子策略」猜滿足 required rule |
| SAFETY | SafetyDefinitionRevision；non_disableable=true | 永不能 OFF/delete；不取代 G/L Account hard safety |

`BuilderEditCommand` 只對 EDITING branch；Command expected_generation、payload expected_branch_generation、current head 三者吻合。在同 research transaction 保存 new GraphRevision、branch generation/head、history/outbox。兩個 writer 選同舊 head，最多一個成功；第二個409，沒有部分節點修改。

有效展開圖中至少一 ENTRY、一 EXIT、一 STRATEGY_RISK；Safety 為 policy 所需完整集合，不能以圖中漏放代替禁用。GraphValidator 依 exact Safety policy 檢查 required IDs。所有有效 edge endpoint、port type／shape／unit／time alignment、nullable、parameter bounds、lookback、nested graph refs、full dependency closure、cycles 在生成／seal／run 前重新驗證。普通計算節點沒有 role 語義；不能由 output name 猜 ENTRY。`saveGraphDraft`／`applyBuilderEdit` 共用同 Validator。

candidate.3 GraphNode 的 pure feature_ref records 可由具名 LegacyFeatureNodeAdapter 轉 FEATURE + enabled=true + FeatureNodeBody，保留原 node IDs／原 revision record；不從未知 feature 猜 Rule/Safety。原 immutable graphs 仍按原 schema保存，若要作新 B3 rule-valid策略，必建立 candidate.4 successor 並 Human review；不 retroactively宣稱舊Graph已滿足新的 minimum roles。

Generator 固定 graph/features/generator/package-lock refs，產 new GeneratedCodeRevision，寫入 branches history。`saveManualCodeRevision` 保存人工 modified bytes 為新 code revision，source AST／sandbox資格仍必要，branch標 `CODE_DIVERGED_RESEARCH_ONLY`。不得逆推或覆写舊圖；若要重建 equivalent graph需新graphrevision＋客觀equivalence review。Published release 不提供節點 OFF／直接 patch API；只能 clone 回 research branch。Seal 使用 `ResearchSnapshotDraft` exact branch/graph/code/features/dataset/config/engine/profiles，branch code divergence明示於source metadata，完整 Captured refs/hash，不以 latest join。

## C3 — Human-triggered bounded AI Analyst

Research Provider port：`ResearchProviderProfile`（model ID/build、tokenizer、allowlisted endpoint/egress/tools、qualification ref）→ `submit(AnalystRequest, input fingerprint)`／`poll(job ID)`／`cancel(job ID)`→ immutable suggestion/result bytes＋`AnalystUsage`。這是 F Research assistant port，**不是 MA14 Coding Executor**。CANDIDATE_UNQUALIFIED／DISABLED 不允正式 provider call；可使用 declared synthetic/offline fixture做設計驗證，不能把它當真正 AI qualification。Provider 無 SQL/Git/Broker/Library approval/Runtime tools，不能任意讀 private folders 或送 external URLs。

Human 在 UI05 選 Features／Parameters／Substrategies／Whole Strategy 後按 Start。`AnalystRequest` 固定 baseline snapshot+run、benchmark、selection、validation plan、provider/prompt revisions、requested receipt與 finite `AnalystBudget`；baseline不是「最新最好結果」。requested trials通常1～3、硬上限5，CPU/time/token/cost皆正數且受 configured source-bound policy限制；實際預設數值與正式 scheduling qualification沿原OPEN-AI-06，不能無限重試。依 exact input closure 先 validate dependencies/data leakage，再隔離 run候選 Backtest＋OOS／robustness。

Research job owner在每次provider submit／engine trial前原子檢查同job已消耗、reserved與worst-case本次需求；只有remaining可覆蓋才dispatch。配置硬wall deadline、CPU/process上限、provider輸出token上限，取消/重啟/失敗trial也占trial count，不無限補重跑。Unknown provider effect/usage保留reserved，先reconcile且停止後續providercall；缺成本capability或rate profile不宣稱符合cost budget。任何retry是原job新attempt，保留immutable input／trial identity及receipt，不能用換job ID規避上限。這是既有F研究job resource控制，不建立第二套WORK Scheduler／Progress。低於最大候選數仍可因budget耗盡正常返回無有效改善或FAILED_NOT_QUALIFIED，不造剩餘測試。

| 狀態／結果 | 來源與 Gate |
|---|---|
| QUEUED→VALIDATING_INPUTS→RUNNING_TRIALS | provider資格／finite budget／immutable inputs／leakage validate；失敗 FAILED_NOT_QUALIFIED |
| COMPLETED／VALIDATED_IMPROVEMENT_AVAILABLE | 同 metric/currency/window/cost/benchmark，fixed validation plan 有完整 trial evidence；不保证策略會改善 |
| COMPLETED／NO_VALIDATED_IMPROVEMENT | 0個有效改善；保失敗與no-improvement trials，另1～2個 UNVERIFIED 研究方向；不能寫「已胜baseline」 |
| CANCEL_PENDING→CANCELLED | cancel event先於terminal completion：保已有trial、partial artifacts、late provider output，全部不得整job qualification |
| terminal完成先於cancel | 保terminal，cancel receipt ALREADY_TERMINAL／no-effect，不倒退不刪Evidence |
| 重啟／unknown provider outcome | RECOVERY_HOLD；依job/token/input/hash reconcile，不blind重提交重复費用job |

`AISuggestion` 保原 fields+Entity ID，新增 analyst run/baseline/candidate/validation outcome refs，只有 Human exact choice才調 `applyAnalystSuggestion`。該操作 root-generation CAS 建新 ResearchBranch，存selected proposal來源與資格狀態；不修改baseline、release、StrategyInstance 或 deployment。UNVERIFIED方向可形成明示未驗證draft（具有效safe proposal時），不稱正式validation。無 graph/code proposal 的文字方向只能保存artifact，不能憑空構造Branch為已測策略。

Actual tokens/time/cost 無可取得producer則null＋原因；estimate不得填Actual。UI05顯示 fixed baseline、selection scope、budget、各trial狀態／failure、validation outcome、provider版本／來源、取消結果及usage未知。API `startAnalystRun/getAnalystRun/cancelAnalystRun/applyAnalystSuggestion` 的結果是 AnalystRun／ResearchBranch，不是 Deployment。

## C4 — Library exception／permanent warning／Runtime admission

正常 approval需 full qualification profile evidence、exact source/snapshot/reviewsubject及 Human receipt。未完成 STANDARD simulation 可由 `LibraryExceptionApproval`明確列 unmet qualification refs、理由與永久warning acknowledgement，authenticated LIBRARY_APPROVER＋Human exact subject確認。AST安全／license／來源／不可變code完整性不能以此exception豁免。

`approveLibraryRelease` 使用 `approval_kind=EXCEPTION_UNSIMULATED`必須匹配 exact exception ref，產生 `QualificationWarning(kind=UNSIMULATED_HUMAN_EXCEPTION, permanent=true)`。UI19 list/detail、clone draft history、PAPER/LIVE admission preview、audit timeline均展示；不能只記前端已點關閉toast。後續模擬完成只增加 exact resolution evidence annotation；原 warning和原approval lineage永不可删除。

LibraryApprover不能通過exception給Runtime grant。ArtifactPublication（bytes verified）、LibraryApproval（研究採纳）、RuntimeAdmission（原 L/H/G/J/K scope、risk、account、strategy、source資格）三者獨立；PAPER使用正式 fixedrelease＋獨立admission與MA08 SimulationSession，LAB research account不等同PAPER。未達PAPER／LIVE資格拒admission，不會因warningack放行。

## C5 — LAB STANDARD account／quality／qualifier counters

`ResearchSimulationRequest`绑定 immutable snapshot/branch、獨立 positive initial capital／currency、STANDARD config、成本／滑價／fill／clock／dataset sourceprofile、qualificationprofile。`ResearchSimulationAccount.scope.environment=LAB`，其 private virtual ledger 不引用 real BrokerAccount，更不寫 J authoritative actual capital。既有 F runner／H/J/K research adapters責任沿用，不建立第二個正式 economic writer。

初版 STANDARD；SIMPLE／STRICT profile IDs可以有 NOT_IMPLEMENTED／NOT_QUALIFIED reference，但 create拒未知或未實作profile。HISTORICAL_REPLAY與FORWARD_OBSERVATION是 execution source mode，不能混成qualification標籤。所有 `SimulationObservation`綁exact source event/hash、snapshot、coverage、event causal sequence、recorded／occurred／observedtime、source quality、estimated flag、reconstruction method及order/fill refs。

| Source quality | 研究績效 | Forward qualifier |
|---|---|---|
| OBSERVED | 必有可信原 capture/time/sequence/coverage，與mode明示 | 只有 FORWARD_OBSERVATION＋完整受准来源、固定profileproof 才可計sample |
| RECONSTRUCTED_ESTIMATED | 可以帶標示研究績效／estimated fill | 永不計observed forward samples |
| UNRESOLVED | result NA／gap reason，保audit | 0有效sample／DATA_INCOMPLETE |
| HISTORICAL_REPLAY中的原 OBSERVED source | 仍是歷史重播績效 | 計replay_samples，不能當本次forward實際觀察 |

STANDARD fill本質是 internal model，不是真實 brokerfill。`STANDARD_MODEL_FROM_OBSERVED`指根據當時可信觀察做model fill；`RECONSTRUCTED_ESTIMATED`指晚補時推估觸發／成交，估計方法、滑價平均值與版本皆保存。兩者都不得用於宣稱真實交易成交。Counter projection由F原owner按through_sequence＋qualificationprofile獨立聚合，不能信任client `qualification_eligible=true`；数值門檻尚未正式adopt時 `PROFILE_UNADOPTED`，不製造QUALIFIED。

斷網補 10:30訊號，在11:00重算必新derived observation，quality=RECONSTRUCTED_ESTIMATED；不能改原UNRESOLVED／OBSERVED行。Gap recovery使用 `SimulationRecoveryRequest`：RESUME exact same snapshot/profile/sourcefrontier且可信完整後准繼續；任何graph/config hotchange必FORK_REPLAY/newaccount/newstart，原session保留。恢復只研究資料一致性，不恢復BROKER／LIVE／WORK舊授權。

UI07明確 LAB research / PAPER session tabs，分initialcapital、snapshot/start、observed/estimated/unresolved/replay counters與未qualification原因；不能借PAPER API構造research account。新增 `createLabSimulation/getLabSimulation/listLabSimulationObservations/getLabSimulationCounters/recoverLabSimulation`。原 `createSimulation`維持MA08 PAPER-only，不重定義原operation。

## C6 — S001 Root／branch constructors／history／archive

`StrategyResearchRoot`是 F/E研究identity，尚無graph時可先存在、strategy_definition_ref=null；永久root ID、root CodeAssignment、owner、generation。原正式 StrategyDefinition 是另既有exact實體，不能以S001字串猜出runtime instance。既有legacy root references透過具名 ResearchRootCompatibilityBinding沿用原身份並記typed link，不把不同namespace entity合併。

`createResearchBranch`可以首次同研究transaction建立root與S001-01，generation0、parent0；`cloneResearchBranch`從exact parentbranch+snapshot或已publishedrelease構造新branch。clone恰一個primary lineage parent；merge/derived-from多來源另typed relation，不變成多父可編輯tree。S001-01／S001-02是 scoped code aliases，由MA11永久normalizedcode allocation service分配；ResearchRoot/Branch永久IDs不隨name／alias／archive改動，退役code也不重用。

同root兩writer clone使用相同expected rootgeneration：一個成功，另一409重新讀head；不給兩個branch同alias，也不挪用被archive alias。parent/ref/sourcehash缺失或不同root=422；不能從name查找latest parent取代exactref。Human從Libraryclone只建立研究branch，不改原release、runtime部署或歷史qualification。

`archiveResearchBranch`是logical archive，generation CAS；任何有snapshot/run/evidence引用的branch不可physical delete。`listResearchBranches/getResearchBranch/getResearchBranchHistory`全部scope/snapshot/cursor可重入，包含 archived branch與missingartifact availability；history逐operation source/actor/refs append-only。History存 CREATED/CLONED/GRAPH_REVISED/CODE_GENERATED/CODE_DIVERGED/SNAPSHOT_SEALED/RUN_REFERENCED/COMPARISON_SAVED/ARCHIVED，既有event／receipt replay不重复新增sequence。

UI04 root/branch sidebar create/clone/archive/history，加headrevision與code divergence警告；UI05固定 snapshot/jobsource，不持latest草稿作为已開始run inputs；UI06歷史比較不限六筆儲存。所有graph/code/snapshot新revision與history在F/E單一scope writer原transaction提交，durable event/outbox后consumer讀exactref，projection缺失保持PENDING不再產第二套researchtruth。

## 原有 WORK／Coding Handoff 與客觀驗收

沿用96永久 Unit IDs，RCG03不是第97個進度功能。MA04-U01 source analysis主IO與archive副IO、U02 BuilderEdit、U03 root/branch producer與generation/seal副IO、U04 researchmethods、U05 comparison/libraryexception、U06 AnalystRequest→AnalystRun及Humannewbranch副IO，按共同source/context可編cohesive wave。LABsim資料契約加入既有F/L simulationconsumer，不與MA08U03 PAPER output混合。

完整record須含 exact model/schema/chapter/source/fixtures/expectederror/receipt/consumer/refhash，讀 `RCG03_LAB_FIXTURE_ORACLES.json` 的人工合成正反／race／recovery例子。這些是 specification oracle，作者只可驗證logical closure／機器讀shape／expectation consistency；真正CPU sandbox、Windows reparse/CreateNew/crash、provider budget/cancel、兩writer SQL CAS、forward source、STANDARD引擎、B3端到端UI、backuprestore均獨立qualification，未執行。

STOP：任何missing/corrupt originalbytes、同command異hash、head／parent／source不符、license/safety未准、unboundedAIbudget、未知qualifier、實際Broker/Secrets/SQL／Git操作或原accepted Owner conflict。只停止受影響operation，已存immutable bytes與其他boundedanalysis保留。CODEX Sol6.1High是主施工端但本candidate不grant；GPT+VSCode/localLM fallback必同WO/source/schema/evidence與能力gate。
