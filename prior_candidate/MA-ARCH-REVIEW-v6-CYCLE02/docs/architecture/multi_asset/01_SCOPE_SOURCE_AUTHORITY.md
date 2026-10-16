# MA01 — 範圍、來源、正式權威與採納路線

Revision `candidate.4`；狀態 `DESIGN_DRAFTED`；Owner：existing Principal Architect；沒有 Runtime／Publication Authority。

## Purpose／Scope／前身

將新多資產、完整 LAB、PAPER／LIVE、URMS 需求接回既有 `docs/V1_SYSTEM_BLUEPRINT.md`、`docs/ARCHITECTURE.md`、`docs/ROADMAP.md` 與 P00 Program。這是一個版本化 companion，不建立另一份正式 Roadmap、Compiler、Controller、Progress Engine 或 Acceptance Owner。正式主線 master@`9b5ab5fdd98744a7db45ec9f14b64ef1f324920f`；設計來源 P00@`2634717b1443eb95fa0fde4d5d987347ef2160e8`。

來源優先序：最新具體 Human Scope Decision → exact accepted Architecture／Receipt → exact candidate source → 歷史／聊天建議。新的產品需求可以建立 Delta；不能追溯改寫舊 accepted Receipt 或宣稱新需求已實作。最新 Owner 請求完整原文已私有保全，Source Ledger 保存訊息身份與內容 Hash。

## 需求、身份與版本模型

Requirement 保存 `entity_id, revision_id, source_ref, source_clause, owner, reuse_or_delta, release_scope, dependencies, design_status, implementation_status, acceptance_gate`。Feature、Capability、Deliverable、Work Order、Task、GAP、Artifact、Evidence、AcceptanceReceipt 是不同 entity kind。名稱、代碼及顯示分期不是身份。Requirement-to-Feature、Feature-to-Deliverable、Evidence-to-Subject 都是有型別且版本化的 N:M 關係。

| Universe | Source／語義 | 保留規則 |
|---|---|---|
| 原 M0～M12 | ROADMAP.md 正式歷史工程分期 | 不等於新 P00～P12；保留來源限定 alias |
| 92 Capabilities | V1_CAPABILITY_MAP.md，blob b22ce06a228af4b148b36e23b639f48f882db4e2 | feature coverage 不直接計工程完成度 |
| 603 leaves／2137 weight | historical_requirements.v1.json，blob 397879b37830c7827b649dea77aef60324742fe9 | 717 mapping edges 不得變成 2541 weight |
| GAP08 26／113 | GAP08_FINAL_CLOSURE，blob 77f855dfc165c17402c3f5c1d39f963c0c3ffb55 | accepted correction core；不能外推 P08／全產品接受 |
| P00～P12：37／127 | program_baseline.v1.json，blob 1e6e4e3eead7908d90736892631e9c36045ebebb | 候選分母；非新多資產正式總量 |
| 新 LAB／URMS／多資產 | Owner 最新請求＋LAB Rev2／Rev3＋URMS input | 先登錄 source-bound delta，再由 R05／R08 採納新分母 |

Leaf weight 只由唯一 source universe／leaf revision 聚合一次。拆分施工 tasks 必須有 allocation，總 allocation 等於原 leaf weight；新的 feature／phase mapping 權重為零。不能平均複製 weight 給每條 edge。普通 child、research result、run 數量不形成新進度 credit。

## Release Slice 與產品範圍

完整產品範圍包括 TW／US stocks、futures、options、各類 ETF、個別 bonds／fixed income、funds、FX／多幣別及其共用研究／Portfolio／Risk／Accounting／PAPER／LIVE 設計。新需求的 FULL_PRODUCT_REQUIRED 不因工程排序被改成 V2。實際 Broker 支援不足是 deployment capability Gate，不是刪除產品身份。

`FIRST_USABLE_REQUIRED`：外部來源受控匯入、Feature Library／Builder、不可變策略／snapshot、單／多策略回測與結果保存、六策略比較、人工發布、單帳戶多策略群組、STANDARD 模擬、人工 budget／actual capital 分離、Order／Fill／PnL 歸屬。完整 OOS／WFO／MC／Benchmark／Ablation／Portfolio／Macro／Rate／AI capabilities 保持完整交付；其中第一 slice 的精確運算覆蓋與資料集合用 ReleaseSlice revision 列出，不用模糊「PoC 完成」代替產品接受。

完整 LIVE 架構本次 required；LIVE enablement 則需要 broker capability、各資產 qualification、資金風險準入、credentials 與 Human runtime grant。多帳戶／未來 provider 仍列產品 scope；先實作單帳戶不準改寫已確認的多資產完整需求。S14／S15三workbook原始來源已捕捉並維持Future研究；message級最早聊天日期仍未取得，不自行發明正式交易觸發條件。

LAB 原 Wave code 的 meaning 保留：01 inventory／AST；02 React prototype＋Library Draft＋S001＋六比較；03 snapshot／results／comparison restore；04 isolated backtest／ablation／OOS；05 bounded AI analyst；06 sim／replay／quality；07 mock group budget UI；08 qualified selective port。後來 LAB-02=Feature Library、LAB-03=Builder 是另一 product catalog scope 的 alias，不得把原 wave 身份覆寫。

## Authority／Inputs／Outputs／Public Interface

Inputs：Source Ledger、原 Program Baseline、Owner Decisions、exact reviews、歷史 registries。Outputs：Requirement Registry、Delta disposition、Coverage Crosswalk、ReleaseSlice candidate、review subject manifest。API/UI 只能讀其投影、提出 scope candidate，不能直接改 accepted baseline。Registry writer 收到 Draft Change；R05 owner 檢查 accounting；R08 整體 reviewer 檢查 closure；Human exact adoption 決定正式地位。

| Role | 唯一責任 | 禁止推導 |
|---|---|---|
| Human | scope／風險／exact acceptance 與 runtime 授權 | 設計請求不是 broker／DB 執行授權 |
| Architect | 語義、章節、跨域契約候選 | 作者自檢不是 Independent PASS |
| WORK／Compiler | 合法單元編譯、依賴、成本、Intake、STOP／Resume | 新 UI／URMS 不接管 Controller |
| CODEX／GPT／LM | exact WO 內實作與 evidence | 不能改 scope／accepted architecture |
| Independent Reviewer | exact subject 獨立檢核 | PASS 不自動取得 dispatch／LIVE |
| Integrator／Publisher | exact authorized materialization | 合併來源不創造 Acceptance |

R01／R03／R04／R05／R07 維持各自原 exact bounded design acceptance；P00 stream closure 仍 0／8，V1 product completion UNCAlIBRATED（正式值 `UNCALIBRATED`）。R02／R06 coverage／qualification／context successor 先完成 C3；R08 原91 rows／A–S disposition＋Source Delta＋final review 是 C5；Human exact acceptance/materialization 是 C6。C5 資料準備、新 addenda 可以並行；final C5 不得略過 C3。

## Lifecycle／Error／Compatibility／Security

需求：CAPTURED → SOURCE_BOUND → DESIGN_MAPPED → AUTHOR_CHECKED → INDEPENDENTLY_REVIEWED → OWNER_ADOPTED；implementation／runtime qualification 分軸。Source 失聯／hash drift：保留身份，標 NEEDS_REBIND，只停止受影響 subject。重大 conflicting accepted semantic：升級 existing Architect/Human，不讓 executor 猜。一般 mapping 修正形成新 revision，不回改 receipt。

三項 reverse mapping 修正保留：P03-ARTIFACTS、P11-HEALTH、P11-BACKUP-RESTORE；原 weight 3／2／4 不因補 mapping 改變。Reuse／Implementation／Qualification／Acceptance 四種 edge 不可混用。GAP08 reuse acceptance 不等於新 P08 integration acceptance。

Public Git export 不包含私有聊天原文、個資、logs、SQL dumps 或 secrets；source_ref 可以是 opaque private ID＋hash＋missing state。Hash 不是原文，也不是來源 authority。Path 僅作安全 locator，不作 Acceptance。

## 正反例／Concurrency／Acceptance／Tests

1. 一 feature 映射三 P phases：同 feature_id、三 typed edges、weight 一次；拒絕生成三 feature 身份。
2. LAB Wave-02 與 product LAB-02：兩 catalog/entity；裸 LAB-02 lookup 回 AMBIGUOUS，要求 context。
3. 工程 task 拆三份：allocation sum invariant；未定 allocation 不得報進度。
4. 717 mappings 聚合 weight：assert distinct 603 leaves、sum2137；raw join sum2541 判失敗。
5. Owner 新 scope 與舊 V1 Blueprint 突出不同：新 delta＋source link，舊 accepted revision 不變。
6. Concurrent ReleaseSlice update：expected_generation 不符回409，不能 last-writer-wins。

客觀接受：每個 requirement 有 source/owner/design/unit/gate；unknown 有限定 blocker；既有 accepted blobs/weights/identities 保留；新分母有 R05 exact candidate＋Owner adoption；無平行 Authority。測試層級為 source review／model simulation，實際 Program adoption 另行。

WORK Handoff：MA01 units 必須帶原 universes、protected SHA、exact delta、mapping assertions、R05/R08 owner；不授權修改 CURRENT／accepted Receipts。Known limitations：S14/S15 原聊天message級日期來源、R02/R06 qualification、新增分母正式採納與 runtime 證據尚缺。

## 本次有界補充契約

[REGISTRY_EXPORT_ADAPTER.md](REGISTRY_EXPORT_ADAPTER.md) 為本章不可省略的候選 companion；typed resource/obligation、T12 witness、export adapter 與 exact dependency/source bindings 必隨章節 subject 一起編譯及審核。原 accepted predecessor 不變。


## RCG01 candidate.4 source-bound successor

Currentformal/default仍master；Human長期main目標與受控雙歷史遷移PLANNED_NOT_EXECUTED見[MAIN_MASTER_MIGRATION_CONTRACT.md](MAIN_MASTER_MIGRATION_CONTRACT.md)。最新完整B3要求以[B3_RELEASE_SLICE.json](B3_RELEASE_SLICE.json) exact requiredset為準，包含OOS/WFO/MC/benchmark/ablation/AIAnalyst，不採舊薄firstslice。CODEXSol6.1High主要Coding、GPT+VSCode/LMquotafallback見../ENGINEERING_EXECUTION_POLICY.candidate.v3.md；旧政策與原接受source保留。舊段落只表示priorcandidate/historicalsource，不可拿來覆蓋此source-boundcurrent/target successor。原P00C3→C5→C6、0/8、所有runtime與發布授權不變。


B3 ReleaseSlice mandatory equality：REQ-MA-026/027/031與所有原first_usable_slice=REQUIRED的atomicrequirements均保留V1_REQUIRED及同exactrequiredset。OOS/WFO/MC/benchmark/ablation、AIAnalyst與原LAB操作不得只停留fullproductscope；research-first sequencing不代表降低已定B3。原multiasset/s14/15future條目另source scope，完整保留，不回寫歷史分母。


## Candidate.5 有界修正承接

B3方向及main目標／CODEX主路由不重選；新版本修正是candidate source delta，沒有實際Git遷移或Formal Adoption。

唯一詳細契約：`REVISION_HISTORY_REPAIR.candidate.5.md`。原已接受範圍與尚未完成qualification保留。
