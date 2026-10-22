**正式 Verdict：`REVIEW_FIX_REQUIRED`**

固定 Subject：`ULTRA-B3-PRECOMPILED-QUEUE-ADDENDUM-V1/addendum.v1`  
固定 Manifest raw SHA256：`86b61152e8188c5495da5ba0bfd3cf063f7de1a62f6d82abb48cb1188fdd51c6`

本候選是具來源約束的導航補充與政策 successor **requirement set**。其保護規則、逐單施工入口與補審方法可保留；但尚不足以作為可直接採納的 deferred-review continuation／Bounded Batch Grant 政策。

本審查未發現必須重開 B3 的架構矛盾，因此不採 `STOP_ARCHITECTURE_CONFLICT`；也不否定這類有界政策的可行性，因此不採 `POLICY_REJECTED`。三項缺口均可由一份最小 cohesive policy successor 處理。本輪沒有修正候選、授予 Grant、啟用政策或執行產品測試。

**範圍與獨立性**

由獨立 fresh-context Reviewer 從實際檔案重新取證，未繼承原作者聊天推理；作者 PASS、驗證計數及 Mock 結果均只視為待核證資料。讀取原始契約以判定相容性，並未重新審查或撤銷已接受的 B3／U01 成果。

本報告以下使用：

- `R`：`D:/00_Learn/量化交易/Code/futures_trading_system`
- `Q`：`C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/ultra-b3-precompiled-queue-addendum-v1`
- `H`：同一上層目錄的 `ultra-b3-mvp-execution-handoff-v1`
- `S`：同一上層目錄的 `source-closure-pairing-20261015T005839Z/candidate/docs/architecture/multi_asset`

**Manifest 與來源核對**

| 獨立檢查 | 結果 |
|---|---|
| Manifest 本身 raw SHA256 | 符合指定值 |
| Manifest 列出的成員 | 118 個，各路徑唯一 |
| 實際檔案集合 | 119 檔，包含 self-excluded Manifest；無多檔、缺檔 |
| 118 個成員的大小及 raw SHA256 | 全相符 |
| Index 125 個來源 pin＋Witness 20 個 pin | 合併為 141 個唯一來源，全部可讀且大小／Hash 相符 |
| 96 張 spec 的 immutable original contract | 與原始 JSON Pointer 選取正文逐項相等 |
| 96 張原 Unit 的 canonical Hash／永久身份／plan revision | 相符 |
| 原 Unit dependencies、spec dependencies、Index edges | 同一 364 條邊 |
| Queue 全序 | 符合原 364-edge DAG 拓樸順序 |
| 每節點 direct／transitive consumers | 以獨立圖遍歷重建，全部相符 |
| MVP 範圍 | 57 Units／184 內部邊／11 Waves |
| Impact interface exposure | 578 筆 |
| 存檔 Mock Expected／Actual 序列、測試碼 Hash | 相符；不等於本輪重跑或正式 Qualification |

以上以獨立 stdlib 讀取、Hash、JSON 比較與圖遍歷核對，未呼叫作者投影器、PoC runner、Compiler 或產品測試。最後再次核對 Manifest 及所有成員，未見漂移。

本輪讀得本機：

- checkout HEAD：`2634717b1443eb95fa0fde4d5d987347ef2160e8`
- branch：`architecture/p00-v1-baseline`
- 本機 `master` ref：`9b5ab5fdd98744a7db45ec9f14b64ef1f324920f`
- 既有 dirty／untracked 狀態保留，不以 clean checkout 為前提。

遠端 master／publication topic 的值存在固定 Witness；本 Reviewer 未另外執行網路 GET，因此不把它們宣稱為本輪獨立遠端查證結果。

**原始權威與版本**

已依 `AGENTS → CURRENT_STATE → manifest／active policies → CURRENT_WORK → CURRENT_CODEX／具名 lifecycle／最新 handoff、result、review、STOP` 重進入。主要版本及本輪核得的 raw SHA256：

| 來源 | 版本／raw SHA256 |
|---|---|
| `automation/governance/master_manifest.v1.yaml` | `8e727b9c548895d482939aad8922517fc4427209d3c395f80f463020b3cf08da` |
| `development_entry_protocol.v2.yaml` | 2.0；`b5486d9cd27c86555123eed96c57e5b7f59dfd46dbb23cb00b7350feffef8b10` |
| `authorization_lifecycle.v1_1.yaml` | 1.1；`547e5dae820541740a72a341bd1797305929bacdbff21b90acfe8866585f5393` |
| `development_state_machine.v2.yaml` | 2.0；`038e2c226b64d29dce9aa0d3b8cf24321b2bc0c526467b6f8784b11d7d83ff39` |
| `execution_capacity_policy.v2_2.yaml` | 2.2；`4e4fd91163d50619e0bea14e96aed67e1568f1bcd781bf4d1ab76c2509ad23cb` |
| `execution_cost_contract.v2.yaml` | 2.0；`daace9c6a9ea0ec83bc86eca6ebcc091318be60c381ab21877dc1d051f8b8120` |
| `work_cost_accounting.v2.yaml` | 2.0；`070e138173c47f2c24f4c58507c53dd01c6b6ae17bb7c4011bc97642178da201` |
| 原 Guide v2 | `dae411b42acba4471307d6291b93c3df7e5f5bb5293ee8b202328e72661803ba` |
| Guide C01～C07 Annex | `a83fb8c9c79f447349892da7bae0dc6fdbff675e7a6712ac868b0b86ba414f82` |
| 原 WORK Kernel | `9f170a4aec8019d2a78384a4f445dbcb04e6b317ff1441acfd91315e998a541f` |
| 原 CODEX Kernel | `6c3b6dfcbc17cdbd2c37ebd11e26457c2bc6e7534dbc8d63c0d391c042e0e9fa` |

另讀取原 `AuthorizationRecord`／`WorkPackageRecord`、實際 U01 native Grant、accepted Source 中的 `ExecutorProfile`、`UnitExecutionResult`、`UnitResultIntakeRequest/Receipt`、`ReviewSubject`，及 MA12／MA14、compiler adapter v5／v6／v7 的相關責任與依賴契約。

原始 frozen 文件內的 candidate 標籤，依外部精確接受收據判定其適用地位；沒有用歷史正文標籤推翻已物化接受，也沒有把未啟用的 Bridge Profile 解讀為現行資格。

目前仍為 U01 Accepted `1/96`；U02 actual qualification 的具名 checkpoint 為 `NOT_OBTAINED_HOLD_U02_QF01`，其 provenance successor 尚未執行。這是 U02 原資格支線，不能改稱 Ultra 缺席的 Deferred Product Review，也不新增 MVP DAG 邊。

**八個問題的判定**

| 問題 | 判定 |
|---|---|
| 1. 非強制高階 Stage Review 可否延後、保留強制 Unit Review？ | **方向相容，但本候選尚未充分定義。** 額外彙總 Review 可與原 mandatory Unit／Wave／Human Gate 分開；須先具名辨識哪些屬非強制，以及補審最遲門檻。不能只以 R1／R2／R3 或「高階模型」名稱判定可延後。見 F-01。 |
| 2. 有限具名 Unit 的 Bounded Batch Grant 是否已充分定義、可採納？ | **否。** 現在只有逐單新 Grant；沒有 Batch Grant 的有限集合 binding、逐項消耗、失效及部分完成語義。這不證明 bounded preauthorization 不可行，但本 Subject 尚未提供該政策。見 F-02。 |
| 3. 每 Unit eligibility、單次消耗、Writer、Cost、STOP 如何維持？ | 原制度已有明確約束，候選正確承接。每 Unit 必須 fresh resolve exact WO／Source／dependencies／Profile intended-use／適用資格／Grant／budget，再依原 lifecycle 取得唯一 Writer、建立 reservation、重驗 binding、durable consume 後 invocation。Result 固定後停止，不能由 NEXT 自動推進。Batch 情況仍缺 F-02 的規則。 |
| 4. 獨立 candidate 授權下，未審 candidate 可否供下游 candidate？ | **本候選沒有可放行定義，目前不得據此開始。** Lane B 有獨立 Grant／隔離／Writer 要求，卻仍把「使用未審上游」留給未來 successor；未定義 candidate consumption scope、固定輸入、傳播及失敗處置。見 F-03。 |
| 5. 資格／安全／架構／Human／mandatory Review 可否延後？ | **不可越過其原 required-before gate。** 候選保護方向正確；實際適用的 Source／Context／Identity／Continuity／Result／Intake、重大架構／authority 決策、mandatory Unit／Wave Review 與 Human Gate 均保留。這也不代表將所有未來 SQL／Broker／P00 Gate 無差別前移到不相關離線工作。 |
| 6. 能否使用獨立替代 Reviewer？ | **可以，須具原制度適用資格。** 不永久綁 Ultra；須符合任務風險、契約及來源閱讀能力，與作者／作者推理上下文分離，固定 exact subject，保留原 Review／Intake／Acceptance 責任。一般 Worker 或 LM 名稱本身不構成資格。 |
| 7. 補審是否按 Consumer DAG／Evidence，而非全部重跑？ | **方法可接受，證據限於導航與合成模型。** Direct／transitive closure 已獨立重建相符；共享 Contract 額外 Consumer 仍須證明影響。先審最早未驗證共享前置，逐 Subject 保留 Verdict；修訂只撤新用途適用性，不覆寫歷史 Receipt。原 mandatory full／Wave-final 檢查仍須執行。 |
| 8. 是否只使用現有 WORK／CODEX，不建 Controller？ | **相容。** 本包未建立具執行效果的 Controller；projection 是導航文件工具，Mock 不得作正式 eligibility evaluator。未來政策仍須由既有 Owner／WORK 承接，不另建調度或 Acceptance 主體。 |

問題 3 的重要原始依據包括：[Lifecycle dispatch order](D:/00_Learn/量化交易/Code/futures_trading_system/automation/policies/authorization_lifecycle.v1_1.yaml:18)、[CODEX entry gate](D:/00_Learn/量化交易/Code/futures_trading_system/automation/prompts/CODEX_EXECUTOR_KERNEL.md:57)、[Review Barrier](D:/00_Learn/量化交易/Code/futures_trading_system/automation/prompts/CODEX_EXECUTOR_KERNEL.md:162) 與 [Guide Annex C02～C04](D:/00_Learn/量化交易/Code/futures_trading_system/docs/architecture/adopted/GUIDE_V2_COMPATIBILITY_ANNEX.source.v1.md:13)。

成本必須保持 forecast／actual／capacity proxy／billing 分離；不可觀測保留 `UNKNOWN/null＋reason`，有限 scope、correction 與 spend cap 仍須固定。工具重試、provider pause 與產品修正不得混算或重置預算。

**F-01：尚無可採納的 Stage 延後／review-only parked 判定規則**

證據：

- [Decision Request:51](C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/ultra-b3-precompiled-queue-addendum-v1/MINIMUM_POLICY_DECISION_REQUEST.json:51) 使用的是 `minimum_successor_requirements`，包含「Define…」「Name exact…」等未完成定義。
- 同檔 `#/decision_requested` 明確只請求將 **requirement set** 送入 Review／Owner adoption process；`#/if_approved/required_before_any_effect` 又要求未來 exact successor。
- [Protocol:33](C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/ultra-b3-precompiled-queue-addendum-v1/GENERATOR_AND_REVIEW_PROTOCOL.md:33) 正確承認現行 barrier；[Deferred Ledger](C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/ultra-b3-precompiled-queue-addendum-v1/DEFERRED_REVIEW_LEDGER.json:25) 只有待填的 mandatory review type／required-before gate。
- H 的 `STAGE_GATES.yaml:188–193` 分別描述 ordinary Unit 與 high-level Stage Review，但未提供這次所需的可延後分類及最遲補審規則。

精確反例：同為「結果已固定、Writer 已釋放、Review pending」，一項可能只是額外 Stage 彙總，另一項可能是尚未取得的 Source／Profile 使用保證。候選沒有完成的判斷式，讓 WORK 據以確認前者可 park、後者不得越過 use gate。現行結果應保持 HOLD；不能由 Owner 採納一句 requirement 就推定兩者已被正確區分。

Mock 的限制也可靜態重現：[PoC:57–61](C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/ultra-b3-precompiled-queue-addendum-v1/poc/test_six_mock_contracts.py:57) 在 prospective fixture 下，只看兩個 policy flag，不驗 pending entry 的 review type、required-before、`frozen` 或 `writer_released` 欄位。把這些欄位改成不合格值，該合成模型仍可能返回 gates satisfied。這不是 native 系統漏洞；它表示 P3 未證明 proposed successor 的安全條件。

風險：若把 requirement set 直接採納成 operational exception，可能誤延 mandatory assurance，或由不同 WORK 解讀出互斥結果。

最小修正：在同一有界 successor 中固定 review 分類、可 park 的充分條件、不可延後項、最遲補審／阻擋門檻，以及與現行 priority／barrier 的精確 precedence；補相應 positive／must-reject 政策反例。無須修改原 frozen evidence 或新增 Machine enum。

Owner Gate：只可對這些已完成且固定 Hash 的政策語義作精確採納；本候選的「進入未來 Review 程序」請求不足以建立此例外。

**F-02：Bounded Batch Grant 完全未定義**

證據：

- [Protocol:21–27](C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/ultra-b3-precompiled-queue-addendum-v1/GENERATOR_AND_REVIEW_PROTOCOL.md:21) 定義逐單 exact Grant，沒有 Batch Grant。
- [Decision Request:55–58](C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/ultra-b3-precompiled-queue-addendum-v1/MINIMUM_POLICY_DECISION_REQUEST.json:55) 仍要求 separate exact WO／Grant，未定義 bounded set 的授權承接。
- [PoC:29–31](C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/ultra-b3-precompiled-queue-addendum-v1/poc/test_six_mock_contracts.py:29) 為每個 Unit 建立不同 Mock Grant；[P1:101–115](C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/ultra-b3-precompiled-queue-addendum-v1/poc/test_six_mock_contracts.py:101) 明確驗它們不同，沒有 Batch envelope 或逐項 ledger。

精確反例：Owner 若只批准有限集合 `{MA02-U01, MA02-U05}`，A 執行後已消耗授權，候選沒有規則判定：B 是否仍有未消耗項、是否必須有獨立 native authorization、部分失敗或 Source revision 改變如何失效，以及如何防止把同一 envelope 再當新 Grant 使用。

原 Capacity 2.2 的 `#/semantics/bounded_correction_grant/review_fix/single_use_rule` 確有**特定工作單**的有界條件預授權，但不能把該具名權限轉授為一般跨 Unit Batch Grant。原 native authorization record 也不因存在 nested section 就自動支持任何新 Batch 語義。

風險：授權消耗歧義、重派、隱含 child authority，或把已批准有限集合擴大為 queue／package 的普遍施工權。

最小修正：只補政策層級的有限集合 binding、逐 Unit eligibility／scope／Profile／budget、單次消耗與部分完成／撤權／漂移／中斷規則，並說明如何由既有 native lifecycle 表達、哪些情況必須停止。保留每 autonomous run 一個 mainline Package、唯一 Writer 與 Review Barrier。**不需要現在建立 96 張 Grant，也不應在本輪建立任何 Grant。**

Owner Gate：須採納 exact bounded authorization 語義；真正具名集合及其權限，仍由後續精確 Grant 固定。未知的未來 WO 值本身不是缺陷；缺的是約束那些值的政策。

**F-03：未審 candidate 供下游 candidate 的使用契約尚不存在**

證據：

- [Lane B 上游條件](C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/ultra-b3-precompiled-queue-addendum-v1/GENERATOR_AND_REVIEW_PROTOCOL.md:24) 明定使用未審上游要先取得未來 reviewed successor。
- `MINIMUM_POLICY_DECISION_REQUEST.json#/proposal/purpose` 限於 non-dependent work；`#/proposal/minimum_successor_requirements/5` 未提供 candidate consumption 判定。
- [PoC:64–66](C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/ultra-b3-precompiled-queue-addendum-v1/poc/test_six_mock_contracts.py:64) 對兩個 Lane 都要求所有 dependencies 為 Accepted。
- [P5:163–166](C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/ultra-b3-precompiled-queue-addendum-v1/poc/test_six_mock_contracts.py:163) 即使設定 candidate Grant／prospective policy，缺外部接受仍回 `STOP_DEPENDENCY_UNACCEPTED`。

精確反例：A=`MA02-U01` 的未審 immutable candidate 已固定；B=`MA02-U05` 即使另有明確 Lane B candidate Grant，也無法從本候選判定何種 candidate-only consumption 可允許。P5 實際驗證的是拒絕，不是受控允許。

這個保守拒絕沒有違反現行政策；缺陷在於它未交付題目要求評估的候選串接政策。不得將「不可成為正式 Accepted Dependency」反向解讀為「所有 candidate-only 消費皆已獲准」。

風險：若使用者誤以為 Lane B 已完成，可能在未定義輸入版本、風險傳播、失敗重驗及 promotion barrier 下施工。

最小修正：若 successor 要涵蓋此功能，原作者須固定允許／禁止的 candidate consumption scope、exact immutable input／grant／consumer binding、衍生追蹤與上游失敗／修訂的下游處置；保留所有不可延後資格及正式接受／整合／依賴 Gate。若刻意只涵蓋完全獨立工作，則明確縮限 adoption claim，維持 candidate-to-candidate 禁止；不能宣稱問題 4 已完成。

Owner Gate：須精確決定是否涵蓋 candidate-only dependent development，以及其限制；本 Review 不自行設計或批准該例外。

**六個作者 Mock 的實際證明範圍**

| 案例 | 實際涵蓋 | 沒有證明 |
|---|---|---|
| P1 | 不同 Unit 使用不同 Mock Grant；缺 Grant／跨 run scope 拒絕 | Batch Grant、durable consumption、實際 reservation／Writer |
| P2 | 合成 checkpoint 的 invocation 欄位、source、competing Writer 分支 | 真實 continuity、撤權／完整 binding／safe reacquisition |
| P3 | current-policy barrier 拒絕；prospective flag 允許獨立 fixture | 已完成的 parked predicate、mandatory review 排除與政策採納 |
| P4 | 缺 Grant／source／qualification／budget／Writer 的布林拒絕 | 原生 Profile／Source／Context／Intake qualification |
| P5 | 拒未接受上游；偵測 body 與外部 receipt 不一致 | 未審 candidate 的受控下游使用正例 |
| P6 | 兩個直接相依待審節點排序、同作者／Hash drift 拒絕、影響標記 | 真實補審、Reviewer qualification、完整相容 Batch 分組及實際重驗 |

存檔顯示 6 passed，Expected 與 Actual 一致；只能維持 `PASS_MOCK_SCOPE_ONLY`。本輪未重跑 PoC。P6 也未涵蓋所有 transitive pending ancestor 情況；這是測試覆蓋限制，不能取代 Protocol 所要求的完整影響閉包。

**可保留的補審設計與替代方案**

候選對 immutable Result、原 native Review reference、逐 Subject Verdict、共享 ancestor 優先、578 Consumer／191 source-only 關係分離，以及歷史 Receipt 保全，方向均與原契約相容。實際 deferred product entries 為 0，不能從 96 張 spec 推算待審數。

現在可用的既有替代路線，是由**已符合原資格的獨立替代 Reviewer**完成原 mandatory Review，再按新 exact Unit authority 推進。這不需要等待 Ultra，也不需要啟用 continuation exception。若缺合格 Reviewer，維持真實 PENDING、固定 Evidence，繼續原範圍允許的唯讀準備。

**Owner exact decision 請求框架**

目前不應請 Human「把 requirement set 當已完成政策採納」。後續可審決策包至少須固定：

| 決策欄位 | 應有內容 |
|---|---|
| Exact subject | 新 successor ID／revision／Manifest Hash；保留 addendum.v1 |
| 原政策差異 | 精確 preimage、條文／JSON Pointer、precedence；無 blanket bypass |
| Stage／pending 規則 | F-01 的可延後分類、predicate、required-before、阻擋條件 |
| Batch 規則 | F-02 的有限集合、逐項 eligibility／消耗／失效／部分完成 |
| Lane B 規則 | F-03 的允許範圍，或明確維持禁止 |
| 保留項 | 資格、安全、架構、Human、mandatory Review、單 Writer、Cost、STOP |
| 獨立審查 | exact successor 的 fresh narrow Review；逐 Finding disposition |
| 採納與效果 | 精確 Owner adoption；必要 source materialization 另授權 |
| 執行排除 | 不產生 Unit Grant／Invocation／Activation／Git／SQL／Runtime 權限 |

建議下一合法工作是：**原作者依三項 Finding 編製一份最小 cohesive policy successor 候選，固定新 Subject／Hash 後做 fresh narrow re-review。** 不修改 frozen addendum.v1，不重開 B3，不重跑未受影響產品測試，也不藉本 Review 開始 Coding 或建立 Controller。

**限制與停止點**

- 未執行受控 Qualification、作者 PoC、產品／SQL／Broker／Host／Controller 測試。
- Hash／原文／DAG 核對不證明全部 95 API／19 UI 的產品語義符合性。
- 尚不存在 future actual WO／Grant／budget／executor／writer；本報告沒有替它們補值。
- 未執行具名 Git mutation；只使用 HEAD／branch／status 類讀取命令。缺 `.git/index` 審查前 raw SHA，不能宣稱已獨立證明 index bytes 零變動。
- 記憶只用於重進入及權限邊界提示；所有本輪判定均以實際來源重新核對。

本輪停止於獨立政策審查交付。`NEXT`、本 Verdict、作者 Mock PASS 與未來 Owner 政策採納，均不自行構成產品或候選 Coding、Grant escalation、Activation、Integration 或正式 Acceptance。
