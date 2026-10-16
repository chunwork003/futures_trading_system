# P00 C3 → C5 → C6 接續 Runbook 與施工資格矩陣

狀態：`PLANNING_COMPLETE / QUALIFICATION_NOT_AUTHORIZED / NO_EXECUTION`。本附件為本輪架構到施工交接的規劃 companion，不是新的 Lifecycle、Compiler、Controller、Acceptance Owner 或正式授權。原 B3 架構及 Guide 已接受，本輪不重審 B3 設計。

## 可直接交接的結論

1. **目前不具備 C3 實際 Qualification 授權，也不具備新的有效 C5 正式 Review 授權。** 最新 Human 文字明訂若尚無 C3 授權只能規劃；不得把「開始本輪收斂」誤作 C3 同意。
2. **C3 no-effects 子任務通過不等於完整 C3 通過。** 原 proposal 只蒐集可觀測的 R02/R06 取證，不能完成尚未授權的 RQ03 backend/bootstrap、RQ05 successor adoption 或 RQ06 migration。若真實 host attestation 不能提供，對應項 `NOT_QUALIFIED / INCONCLUSIVE`，不以作者聲明、Fixture、Hash 或摘要代替。
3. **目前不允許自動條件式 C5 正式 Review。** 可以自動準備 C5 Exact Subject，也可以在已合法執行的 C5 PASS 後自動準備 C6 決策包。實際 Review/Acceptance 仍需其原權威。
4. 最短下一項 Human 決策仍是原固定 `P00-C3-NOEFFECTS-QUALIFICATION-01`，不要求重新批准 B3 或 Guide，不讓新增 conditional delegation 成為 C3 前置。
5. C5 的91列/A–S資料準備、12包來源/Contract/Mock/成本/能力/Regression 規劃可繼續；沒有產品 Coding、Mock 程式/測試、Compiler Invocation、Executor Dispatch、Git/SQL/Runtime 權限。

## 權威及版本

當前入口為 `docs/CURRENT_STATE.md` 最上層已接受 B3 Addendum；`docs/architecture/adopted/B3_V1_ACCEPTED_BASELINE.v1.json` 與 Human Receipt 提供 exact A+B。原 Architecture1.2.2、Capacity2.2、ProgramV2 operational rev5、GAP08/ADR 與 R01/R03/R04/R05/R07 有界接受保留。

本機 HEAD `2634717b1443eb95fa0fde4d5d987347ef2160e8`；master/origin/master `9b5ab5fdd98744a7db45ec9f14b64ef1f324920f`；main/origin/main `0cb0283b8c5f795f8da1672575cbb674945db73a`。只重新讀本機Refs，沒有 fresh network/GitHub 驗證。最終 main 政策已接受，實際遷移未執行。尚未發布的 accepted Addendum 用其原 raw bytes/Receipt 綁定；不得把 branch HEAD 當成已包含本機新文件。

原 Convergence 明示 C3→C5→C6，C5_PREPARATION 可與 C3 平行；`r06_not_blanket_design_review_veto=true` 允許不依賴未資格 profile 的設計/規劃，不等於豁免正式 C5 的明列前置。原 Request91列、A–S19項、七 acceptance predicates、131072 aggregate gate 保留。B3 是 source-bound delta sidecar，不更改原分母。

來源逐筆 raw SHA256、Git blob ID/SHA256 分別固定於 `SOURCE_PINS.json`；CRLF raw bytes 與 Git blob 差異不混算。舊 accepted source 由 pinned Git blob 判斷；新 Human 本機物化內容由 accepted raw Scope/Receipt 判斷。Historical 名稱/候選 Status 不可覆蓋新 exact Receipt 的有界效力。

## Stage Transition Matrix

機器版完整欄位與精確條件見 `P00_REMAINING_GATE_AND_CRITICAL_PATH_MATRIX.json#/stage_transitions`。

| Current State | Required Evidence | Gate / Authority | Next State | Stop |
|---|---|---|---|---|
| B3 A+B 已採納，本輪僅規劃 | Receipt/Scope/來源無漂移 | 當前 Human planning scope | C3 請求、C5準備 | 採納不推導 Invocation |
| C3原提案待授權 | Human exact grant + current source/profile/tool/capability/cost/writer | Human/既有 WORK | 一次有界 no-effects 取證 | 缺授權、缺trace、保護來源寫入 |
| no-effects結果 | 每RQ正反例、讀回、真正host及獨立omission evidence | 真正 Independent Reviewer | 已證子項閉合，未證項保留 | 子項PASS不升全C3 |
| RQ03/05/06仍未閉 | accepted producer/currentness、exact successor decision與migration授權/證據 | 原 A2/P00/compiler Owner +必要Human | 完整C3證據可固定 | 不擴張no-effects範圍 |
| C5準備 | 91/A–S/七predicates逐項 final disposition及accepted delta | 已授權planning | 準備封存Final Subject | NOT_YET_VERIFIED不變成PASS |
| full C3必要條件滿足且 C5 Subject固定 | 完整Manifest、coverage、source/applied successor、有效review authority | 新exact Human/真正既有delegated Review Owner | Fresh C5 Review | 作者不得充Reviewer；未知subject無權執行 |
| C5 PASS | independent verdict/manifest、end drift與integration證據 | 既有planning可準備 | C6 Human Decision Request | Review不產生Acceptance |
| C6 Human exact批准 | 精確Subject、保留gate、明示物化範圍 | Human Owner | 合法P00物化，逐Unit資格評估 | 未列權限全部保留 |
| P00 accepted +各包自身資格 | exact dependency/reuse、compatible compiler、baseline、grant、writer、capacity/test/review | 既有WORK/Grant Owner | 只執行已授權工作 | 不由P00或Package計畫推導Dispatch |

## C3 Qualification Preconditions、判斷與失敗處置

**Invocation 前**：原提案/本次 witness/最新 adopted delta 精確一致；Human exact scope grant 已取得且無撤銷；profile=`P02.IMPORT / CONTRACT_REVIEW_NO_EFFECTS`；工具/來源/原始與 loaded bytes/模型/consumer/task/session/epoch固定；觀測與必要carrier metadata可取得；輸出只在原提案指定新目錄；成本未知據實標示，不能虛構；writer/未完成 execution/STOP/能力/Provider 均經原 Owner 檢查。實際 Executor invocation 若使用既有 lifecycle，沿用 exact single-use identity及既有順序，不把這份規劃當執行reservation。

| RQ | PASS 所需 | FAIL／INCONCLUSIVE 與保留權限 |
|---|---|---|
| RQ01 | exact source/tool、完整義務、payload roundtrip、來源/版本/Hash一致 | source缺漏/衝突即FAIL；無原文/loaded證明則INCONCLUSIVE |
| RQ02 | 由原文獨立建立 obligation inventory；逐unit/stage/reverse exclusion及seeded omission被獨立發現 | Expected不可由selector成功輸出產生；UNKNOWN保留full source/STOP；old48/676/51不是latest B3完整證明 |
| RQ03 | accepted producer/consumer trust、真實durable receipt/registry bootstrap、complete current coverage/heads | caller/session/fixture不是trust；backend未qualified仍NOT_ESTABLISHED；no-effects不可自行bootstrap |
| RQ04 | intended profile 真實 injection bytes/必要overhead、actual model/tokenizer count、task/session/epoch、讀回/continuity/STOP/head失效及獨立任務 | 只有synthetic/human claim無法PASS；host不支援為INCONCLUSIVE；不捏造成本或注入值 |
| RQ05 | 原aggregate131072實際滿足，或另經精確獨立審核及Human接受的successor | 原已知FAIL不變；不能變成每批128KiB、少算metadata或拿估計當actual；新successor須自己的Gate |
| RQ06 | exact qualified successor與明確compiler/resolver migration grant及其實際required evidence | 本輪及no-effects提案不授權Migration/Activation；沒有必要profile/adapter/來源整合證據即HOLD |

所有 required predicates 為 AND，而不是打勾項數達到門檻。明確區分 `SOURCE_REVIEW`、`MODEL_SIMULATION`、`ACTUAL_NO_EFFECTS_PROFILE`、`ACTUAL_BACKEND_RUNTIME`；後者本輪 NOT_RUN。

FAIL 時固定原反例/Expected/Actual、source/tool/profile/output Manifest及影響範圍；有界既有取證可以持續，但不得自動修正式契約/改gate。INCONCLUSIVE 時明列缺不可替代資料與下一最小授權，繼續其餘planning。no-effects結果即使有PASS，也只適用其觀測profile/model/tool/session/stage；executor/publisher effects profile不繼承。

## C5 授權與 Independence 的精確結論

`P00-closure-convergence.v1.json#/remaining_work_groups` 是依賴與 NEXT 規劃，不是 review grant；`review-binding.v1.json`、舊 review-request 是各舊exact subject的請求/歷史結果，不授權本機新的Final Subject。前輪 `C5_PREPARATION_REPORT.md` 明示 NOT_FORMAL_C5_REVIEW。原 P00 baseline允許作者 bounded offline validation；不能把此 self-check權限解釋為作者可接受自己的正式 independent baseline。

Accepted `authorization_lifecycle.v1_1` 及 `development_entry_protocol.v2` 明示 NO_AUTHORITY_CREATION、WAKE_ONLY、Review!=Integration!=Acceptance。既有 `EXECUTION-CAPACITY-FINAL-LIVENESS.owner.json#/correction_grant/review_fix` 有限的conditional precedent只屬原特定WO，不可轉移到C5。原文也明說 unknown future SHA 沒有 executable authority，後續要fresh exact childbinding。

因此 **現有可取來源未建立合法、可直接使用的conditional C5 grant**。主推薦只核准 C3；C3必要條件完成、C5 exact manifest固定後，以真正已delegated的原Review Owner或新Human exact decision授權一次 fresh review。若Human堅持一次條件授權，另有 `C5_CONDITIONAL_AUTHORITY_DISPOSITION_AND_OPTIONAL_PROPOSAL.json` 作非必要討論草案：需明示的新bounded authority amendment/delegation、來源封存、獨立Fresh Reviewer、一次額度、scope/STOP/CAS/防漂移，不是本輪可執行路徑，也不授權RQ03/RQ05/RQ06/C6。不要為縮短等待把新policy計畫加成C3前置。

Fresh C5 Reviewer須有獨立工作上下文與固定來源；只交exact Subject、原91/A–S/predicates、已接受範圍、原始Evidence及反例。作者可以提供Finding狀態，但不能提供其判斷作oracle；Reviewer自行讀必要上/下游閉包，唯讀候選、只寫獨立review輸出，記錄reviewer角色、source hash、正負例、未驗runtime。工具若不能隔離，就停在PENDING_FRESH_REVIEW，不使用作者自檢代替。Reviewer來源讀取前及判決後皆驗hash；發生漂移停止受影響Review。

## P00 R01～R08 最新狀態與保留Gate

完整精確來源見機器矩陣 `#/stream_matrix`。狀態是本輪讀取原Convergence後的有界投影，不是新接受紀錄。

| Stream | 設計／Review | 尚需／later qualification | 本輪Closure |
|---|---|---|---|
| R01 | bounded Human accepted、原兩反例已獨立閉合 | final P00；P05/P06/P08 actual adapters/PG/locks/ABA/permission source按使用Gate | 未關閉 |
| R02 | full tool/compiler未accepted | latest accepted-pointer/source整合、RQ01–06及profile、原AC05/06 | 未關閉 |
| R03 | bounded Human accepted | qualified templates/tools、P01/P02實作build、Q01–Q10/U01–U08/A2按需要 | 未關閉 |
| R04 | bounded Human accepted | policy successor與A1/A2/A3 schedule/CAS/dedupe/crash/revoke/promotion；standing publication既有GOV-F02/03/04未自動消失 | 未關閉 |
| R05 | bounded Human accepted | final universe/weight decision與外部UNKNOWN；trusted progress/throughput/ETA在promotion前取得 | 未關閉 |
| R06 | probe設計可review，完整資格未取得 | CTX02 exhaustive/reverse；CTX03 actual injection/continuity/trust；原budget FAIL；exact successor/migration | 未關閉 |
| R07 | bounded Human accepted、原兩finding已獨立閉合 | final P00；A2/A3/D4/D5 actual golden/model/cost及qualification按promotion | 未關閉 |
| R08 | final baseline未完成 | 原91列/A–S final dispositions、七predicates、C3後fresh final review、C6 | 未關閉 |

**P00維持0/8；候選127不轉正式進度；V1仍UNCALIBRATED。** B3設計接受與產品runtime qualification不同；P00接受與work authorization不同。未做的真實資格測試不需假造，也不能一律前置到所有UI/Research工作。

## Source Integration 與最早可推進工作

1. 當前可做：所有12包 exact Unit/API/UI/DTO/Mock world/Oracle/Context/成本/能力/來源方案之planning；C5逐條final evidence整理與剩餘標示。不呼叫Compiler、不建reservation、不標READY。
2. **另有exact Human scope grant時可先做隔離Mock或P00 no-effects qualification**，但要其獨立來源/目錄/測試/writer/取證邊界；mock結果不冒充producer accepted result、同版本product integration或P00 closure。
3. PK01 是最早planning grouping，但不是一個所有Unit都免C6的機器WO。`MA01-U01`無上游Unit依賴，可最先完成source/scope/provenance候選與測試spec準備；真正動手仍須既有 compiler companion/adapter profile可用、fresh accepted local Addendum及完整source/歷史ContractRef閉包、精確current preimage/protected allowlist、所需review/tests、writer/cost/單次grant。**每個Unit/Package尚需其實際可消費的source assembly/integration證明**：只在C:讀到accepted原文不等於現有Git snapshot compiler可編譯；若未有合法支援的assembly/Git source或accepted overlay adapter/profile及exact grant，即`HOLD_SOURCE_ASSEMBLY`。C6完成也不能讓目前master clone自動coding。其工作若變成Git主線遷移、Acceptance或Current authority寫入，即需那個exact額外授權。
4. `MA01-U04` 明含P00 scope/C3→C5→C6，不能因B3已接受省略P00；`MA15-U04`保留四類Gate/資格矩陣不偽稱runtime PASS。所有已存在依賴維持原圖，不能將PACKAGE0crossedge推成所有unit無前置。
5. 原P01/P02候選明列依賴P00：C6前最多 `COMPILED_PENDING_BASELINE_ACCEPTANCE`，不能READY。C6後也尚需P01/P02 exact baseline/current source、compiler/context profile、current intake/writer/cost/Scope和Implementation authorization。PK01!=P01，不能強塞closed PXX schema；用existingOwner的versioned companion/adapter。
6. 只有實際依賴trusted receipt/autonomous eligibility的行動需要RQ03/A2 current trust；全局pending UNKNOWN不阻止另有Human明確授權之P00 planning。PG/Restore/Broker/Controller只限制其實際消费者、feature模式及release journeys，不要新增為每個read-only或UI mock規劃的總前置。
7. 未發Git的local raw accepted source可用於exact-authorized manual planning/Mock設計；實作前一定要解決該Unit source assembly/integration。任何需Git-only committed inputs的compiler/profile，必須先有可驗證controlled source assembly/integration與該效果exact grant；可接受overlay的路線也必須先有真的accepted adapter/profile，不能由VSCode／Human手動模式豁免。Source assembly、Git publication和整個main/master遷移是不同效果，不得把全部主線遷移加為每個UI前置。尚未有Git grant不能假裝遠端已有v9，也不必為讀本機文件先遷移main/master。

## C5 PASS 到 C6 與 WORK 接續

在已授權且真正獨立的C5 PASS後，WORK可依現有planning authority組裝一次Human決策請求：exact final P00 subject/envelope/manifest、91/A–S/predicate結論、各已接受bounded receipt、明列全部retained implementation/runtime/profile gates、允許物化檔案/效果與尚未發布狀態。C6 Human正式回覆前維持P00未accepted，不改CURRENT標籤/分母/receipts。C6後只物化明示的acceptance來源，不自動reserve/dispatch。

下一個必需Human行動見 `NEXT_HUMAN_AUTHORIZATION_AND_CONTINUATION.md`。本輪僅有規劃/來源完整性檢查；C3、C5、C6、Compiler、產品測試/獨立資格、Git/SQL/Runtime皆未執行。沒有要求Ultra重新判定已確認設計；普通WORK可以依此表讀來源與逐Gate接續。真正需高階升級的只有新受保護語義衝突、authority amendment、互斥scope/產品規則或無法可靠恢復之原始來源，而不是每包例行規劃。
