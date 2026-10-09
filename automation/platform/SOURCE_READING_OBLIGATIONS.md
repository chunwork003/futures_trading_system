# R06 — P01/P02 Source-to-Reading Obligation Mapping

狀態：LOCAL AUTHORING CANDIDATE / REVIEW_PENDING；未accepted、未發布、product NOT_AUTHORIZED。

本輪source input為完整 `c10c6570ef420e9aa23655942dddc5ae77a333c9`，master為`9b5ab5fdd98744a7db45ec9f14b64ef1f324920f`。僅延續R06；R01/R05及舊compilation、reading/review evidence不重寫。

## Mapping範圍與證據

48份exact source、676個完整section／top-level pointer units。51項critical候選義務含13個active denied assertions及7個invariants，另列P01/P02完整mandatory來源與全部API selected schema/endpoint。所有ref保存Git commit/blob/raw SHA256；section保存line span與raw slice hash，JSON/YAML pointer保存完整value hash。Stable ID由path/heading/occurrence或pointer構成；版本、行號、內容變動由exact source hashes失效，不跨snapshot拼接。

此為關鍵語意對應與完整source fallback，**不是676項需求已驗收**。未人工分類的文字仍必讀，不能以critical mapping沒有列到為理由刪除。source unit索引完整只指固定bytes，語意完整性／consumer comprehension仍待獨立review。大registry不加入P01/P02 mandatory pack；以有界pointer導航，按需回到exact完整source。

## Positive / negative / protected義務

| ID | Package | 類型 | Source section | 候選解讀 |
|---|---|---|---|---|
| COMMON-SCOPE | P01,P02 | PROTECTED_SEMANTICS | `docs/architecture/V1_BASELINE.md` section:4ddcbecbc4f03e142e1a | BACKTEST/SIMULATED；P00未accepted/exact grant不得product implementation |
| COMMON-MONEY | P01,P02 | POSITIVE_AND_NEGATIVE | `docs/architecture/V1_BASELINE.md` section:ca8e2f13776363a8d611 | finite Decimal/UTC/calendar/identity；float、日期猜測、修正版silent switch拒絕 |
| COMMON-OWNERS | P01,P02 | PROTECTED_SEMANTICS | `docs/architecture/V1_BASELINE.md` section:6e6a433b168e21db2112 | 單一domain owner及薄adapter；BFF/UI不得建立經濟或恢復truth |
| COMMON-CUT | P01,P02 | PROTECTED_SEMANTICS | `docs/architecture/V1_BASELINE.md` section:1e7f64f3e9d411687a5b | required cohort/current cut、risk減少仍驗authority；EXIT-confirm FLAT-re-evaluate-ENTER |
| COMMON-COMPAT | P01,P02 | PROTECTED_SEMANTICS | `docs/architecture/V1_CONTRACTS.md` section:2b0a5df4ded9453734c2 | accepted models/legacy next-bar/cost/identity保留；新wire不替代domain constructor |
| COMMON-DATA | P01,P02 | POSITIVE_AND_NEGATIVE | `docs/architecture/V1_CONTRACTS.md` section:1769b026efd6cda9d1fb | immutable reference/data identity及quality語意，不把snapshot當canonical acceptance |
| COMMON-RECEIPT | P01,P02 | POSITIVE_AND_NEGATIVE | `docs/architecture/V1_API_ARCHITECTURE.md` section:c45ccd407736bc1c9552 | exact key/body/revision replay、CAS、unknown response；不用new key重做 |
| COMMON-ERROR | P01,P02 | POSITIVE_AND_NEGATIVE | `docs/architecture/V1_API_ARCHITECTURE.md` section:094e3ed80ceff0db6b48 | auth/permission/errors、artifact/access/hash、upload safety；CSV矛盾不得省略 |
| COMMON-SHAPE | P01,P02 | NEGATIVE_ASSERTION | `docs/architecture/V1_API_ARCHITECTURE.md` section:ce47a6cf2650f8441e08 | schema/hash/source match非currentness、broker/provenance或semantic acceptance |
| COMMON-GENESIS | P01,P02 | PROTECTED_SEMANTICS | `docs/architecture/V1_GENESIS_AUTH_CONTRACT.md` section:434446107bce5bb51a81 | reservation不等於account；missing genesis不可FLAT/READY；fence/atomic closure |
| COMMON-AUTH | P01,P02 | POSITIVE_AND_NEGATIVE | `docs/architecture/V1_GENESIS_AUTH_CONTRACT.md` section:e417068e16067feb306d | cookie/CSRF/Origin/service身份、expiry/revocation、redaction；不能信UI/header |
| COMMON-SYSTEM-AUTH | P01,P02 | NEGATIVE_ASSERTION | `docs/architecture/V1_API_ARCHITECTURE.md` section:810fbc23c49f7a69c22c | 兩個listener身份不同；Python私有credential、BFF actor stripping、TLS驗證 |
| COMMON-STATE | P01,P02 | PROTECTED_SEMANTICS | `docs/architecture/V1_STATE_MACHINES.md` section:d1ed680fa600ad01ef09 | consumed/invoked/resume/wake、review/integration/acceptance不同，不產生grant |
| COMMON-READ | P01,P02 | READING_INTEGRITY | `automation/platform/CONTEXT_READING_RECEIPTS.md` section:8a2d7054b61fbf23fa0c | claim-only、同key衝突、source/scope/session/epoch失效重讀，不創造trusted ack |
| COMMON-INTAKE | P01,P02 | INTAKE_DEPENDENCY | `automation/platform/CURRENT_INTAKE_REGISTRY_CONTRACT.md` section:e1852a2d00d4491b90f0 | 完整producer/current registry positive coverage未建立時UNKNOWN；既有WORK re-entry保留 |
| P01-FRAME | P01 | POSITIVE_AND_NEGATIVE | `docs/architecture/V1_DATASET_IDENTITY_IO.md` section:694db3b5328dfc5ad2fb | exact framing/排序/既有mor1、semantic hash與raw file hash分離、correction lineage |
| P01-CSV | P01 | POSITIVE_AND_NEGATIVE | `docs/architecture/V1_DATASET_IDENTITY_IO.md` section:be483ef64908dea198a7 | 十欄CSV_V1/source_code/可選檔首BOM/UTC Decimal bytes cap；禁止URL/path/sniffing/filler |
| P01-REF | P01 | POSITIVE_AND_NEGATIVE | `docs/architecture/V1_DATASET_IDENTITY_IO.md` section:fc838930f876dd7b256c | pinned mapping/calendar/listed有效區間、owner/hash/ID一致，不讀DB猜coverage |
| P01-FILE | P01 | PROTECTED_SEMANTICS | `docs/architecture/V1_DATASET_IDENTITY_IO.md` section:8a092c88e81ebbfb3944 | hash/framing/fsync/同filesystem atomic rename；stage非published、衝突不覆寫 |
| P01-COVERAGE | P01 | POSITIVE_AND_NEGATIVE | `docs/architecture/V1_DATASET_QUALITY.md` section:5bef886456288f1f958e | caller interval及完整calendar evidence；missing reference不變required=0、不猜夜盤日期 |
| P01-QUALITY | P01 | POSITIVE_AND_NEGATIVE | `docs/architecture/V1_DATASET_QUALITY.md` section:ab405e50c4c694860b35 | invalid/reference/missing/conflict/outside判定次序、完整immutable report，不信flag |
| P01-CORRECTION | P01 | PROTECTED_SEMANTICS | `docs/architecture/V1_DATASET_QUALITY.md` section:c9c516b792f527a46315 | 完整新version；不混parent reference、不原地修補、不靠arrival/priority挑winner |
| P01-TERMINAL | P01 | POSITIVE_AND_NEGATIVE | `docs/architecture/V1_DATASET_QUALITY.md` section:33c3e643882932d9dbc0 | receipt/report跨record約束、null非0、cancel/infrastructure unknown不偽造terminal quality；P03 owner |
| P01-CASES | P01 | REQUIRED_EVIDENCE | `docs/architecture/V1_DATASET_QUALITY.md` section:3f27fd3e695e8eb7ba11 | Q01–Q10需actual importer/filesystem qualification；規格fixture不是runtime結果 |
| P02-HOST | P02 | POSITIVE_AND_NEGATIVE | `docs/architecture/V1_APPLICATION_BUILD_TESTHOST.md` section:7e7a641e1f20e26b9c44 | exact locks/native lanes、replay不重新解依賴；P11 container/install不冒充P02已驗證 |
| P02-ISOLATION | P02 | PROTECTED_SEMANTICS | `docs/architecture/V1_APPLICATION_BUILD_TESTHOST.md` section:e9d557c30b1b8ace5ef9 | 無durable adapter=503，auth先401/403；fake/provider/test credentials不入普通artifact |
| P02-ACTOR | P02 | PROTECTED_SEMANTICS | `docs/architecture/V1_APPLICATION_BUILD_TESTHOST.md` section:c0c817d16f9dc1d7ee29 | trusted subject/session per-request；browser無URI/role/credential authority；redirect不轉secret |
| P02-CASES | P02 | REQUIRED_EVIDENCE | `docs/architecture/V1_APPLICATION_BUILD_TESTHOST.md` section:fd28f00db2a3d5915eb0 | auth/session/503/CSRF/cookie/artifact/unknown retry/LIVE拒絕；實際host/browser尚未run |
| P02-WORKLOAD | P02 | POSITIVE_AND_NEGATIVE | `docs/architecture/V1_API_ARCHITECTURE.md` section:3d413c8b1dd3a0d44517 | limits不可caller override；missing config拒絕、不宣稱throughput或partial success |
| P02-WORKER | P02 | PROTECTED_SEMANTICS | `docs/architecture/V1_STATE_MACHINES.md` section:f09182f7f46511699ee1 | operation/attempt/lease states、cancel/publish CAS、expiry holder不能成功，P03 durable owner |
| P02-SIM | P02 | PROTECTED_SEMANTICS | `docs/architecture/V1_STATE_MACHINES.md` section:11120d97abcb9fa0f94c | 非P02經濟implementation；kill非flat、MATCH/VALID不等於READY/permission |
| NEG-CONSUMED_REDISPATCH | P01,P02 | NEGATIVE_ASSERTION | `automation/specs/negative_assertions.v2.yaml` /semantics/denied/0 | DENY CONSUMED_REDISPATCH |
| NEG-NON_INVOKED_CONSUMED_RESUME | P01,P02 | NEGATIVE_ASSERTION | `automation/specs/negative_assertions.v2.yaml` /semantics/denied/1 | DENY NON_INVOKED_CONSUMED_RESUME |
| NEG-FABRICATED_INVOCATION_OR_HISTORICAL_EVENTS | P01,P02 | NEGATIVE_ASSERTION | `automation/specs/negative_assertions.v2.yaml` /semantics/denied/2 | DENY FABRICATED_INVOCATION_OR_HISTORICAL_EVENTS |
| NEG-NEW_RESUME_WO_EXECUTION_AUTH_RESERVATION_DISPATCH_BUDGET | P01,P02 | NEGATIVE_ASSERTION | `automation/specs/negative_assertions.v2.yaml` /semantics/denied/3 | DENY NEW_RESUME_WO_EXECUTION_AUTH_RESERVATION_DISPATCH_BUDGET |
| NEG-UNFINISHED_EXECUTION_NEW_WORK_BYPASS | P01,P02 | NEGATIVE_ASSERTION | `automation/specs/negative_assertions.v2.yaml` /semantics/denied/4 | DENY UNFINISHED_EXECUTION_NEW_WORK_BYPASS |
| NEG-PERCENT_DERIVED_EXACT | P01,P02 | NEGATIVE_ASSERTION | `automation/specs/negative_assertions.v2.yaml` /semantics/denied/5 | DENY PERCENT_DERIVED_EXACT |
| NEG-RAW_EVIDENCE_MUTATION | P01,P02 | NEGATIVE_ASSERTION | `automation/specs/negative_assertions.v2.yaml` /semantics/denied/6 | DENY RAW_EVIDENCE_MUTATION |
| NEG-FORECAST_REVIEW_AUTHORITY | P01,P02 | NEGATIVE_ASSERTION | `automation/specs/negative_assertions.v2.yaml` /semantics/denied/7 | DENY FORECAST_REVIEW_AUTHORITY |
| NEG-REVIEW_PASS_AUTOMATIC_ACCEPTANCE | P01,P02 | NEGATIVE_ASSERTION | `automation/specs/negative_assertions.v2.yaml` /semantics/denied/8 | DENY REVIEW_PASS_AUTOMATIC_ACCEPTANCE |
| NEG-IVF01_REV1_SILENT_REUSE | P01,P02 | NEGATIVE_ASSERTION | `automation/specs/negative_assertions.v2.yaml` /semantics/denied/9 | DENY IVF01_REV1_SILENT_REUSE |
| NEG-IVF01_WAIVER | P01,P02 | NEGATIVE_ASSERTION | `automation/specs/negative_assertions.v2.yaml` /semantics/denied/10 | DENY IVF01_WAIVER |
| NEG-AUTO_IMP_003_AUTHORIZATION | P01,P02 | NEGATIVE_ASSERTION | `automation/specs/negative_assertions.v2.yaml` /semantics/denied/11 | DENY AUTO_IMP_003_AUTHORIZATION |
| NEG-UNATTENDED_WITH_UNQUALIFIED_CAPACITY | P01,P02 | NEGATIVE_ASSERTION | `automation/specs/negative_assertions.v2.yaml` /semantics/denied/12 | DENY UNATTENDED_WITH_UNQUALIFIED_CAPACITY |
| INV-1 | P01,P02 | PROTECTED_SEMANTICS | `automation/specs/negative_assertions.v2.yaml` /invariants/0 | PROVIDER_ACTUAL_DENIAL_WINS |
| INV-2 | P01,P02 | PROTECTED_SEMANTICS | `automation/specs/negative_assertions.v2.yaml` /invariants/1 | NO_AUTHORITY_CREATION |
| INV-3 | P01,P02 | PROTECTED_SEMANTICS | `automation/specs/negative_assertions.v2.yaml` /invariants/2 | HISTORICAL_PHASE_SNAPSHOT != CURRENT_LIFECYCLE_PROJECTION |
| INV-4 | P01,P02 | PROTECTED_SEMANTICS | `automation/specs/negative_assertions.v2.yaml` /invariants/3 | CONTRADICTORY_CURRENT_PROJECTION_FAIL_CLOSED_RECONCILIATION_REQUIRED |
| INV-5 | P01,P02 | PROTECTED_SEMANTICS | `automation/specs/negative_assertions.v2.yaml` /invariants/4 | REVIEW_PASS != INTEGRATION_PASS != MATERIALIZED_ACCEPTANCE |
| INV-6 | P01,P02 | PROTECTED_SEMANTICS | `automation/specs/negative_assertions.v2.yaml` /invariants/5 | IVF01_BLOCKED_UNTIL_REVIEWED_1_2_ACTIVATION_THEN_REV1_STALE |
| INV-7 | P01,P02 | PROTECTED_SEMANTICS | `automation/specs/negative_assertions.v2.yaml` /invariants/6 | AUTO_IMP_003_NOT_AUTHORIZED |

P01 schema closure：28個完整schema values，沒有HTTP endpoint施工義務；P02：93個schema values、46個Python/BFF endpoint paths，包含auth/security/error及所有recursive refs。數量是兩個surface的閱讀值數，不是新DTO或已實作數。P01排除的simulation等schema仍有full-load trigger；P02不以縮包為由移除登入/CSRF/LIVE deny。

## Required evidence與最新結果/intake dependencies

原resolver mandatory P01=33份、P02=31份完整來源；negative_assertions、reading claim schema/contract、current intake registry設計與exact latest-at-snapshot P00 checkpoint/review為補充。三個result-index records各自保留exact來源：已accepted AUTO-IMP-002前件、P01r5/P02r2歷史編譯。它們不能冒充global current registry，舊編譯也不能證明新context可用。

復用原p00_intake.observe：active execution/writer只在原source projection明確NONE；STOP、pending result/review/integration/acceptance、latest delta、last accepted result七項仍UNKNOWN。route=REHYDRATE_MISSING_EVIDENCE。P00設計有獨立human authoring grant，可續作；任何product dispatch仍需accepted current intake/registry、source/policy、dependency/authority/one-writer/capacity等gate。

## Reading claim完整性與可重現性

每份mandatory有FULL_EXACT_SOURCE義務，selected schemas/endpoints另有完整value hash；源文件未映射內容保留fallback。原reading plan/claim工具不改：同consumer/task/session/epoch、scope、context/pack、payload hash才能比對；同key相異payload拒絕。source/registry/STOP/context loss使proposal失效，舊item保持PRESENT或UNKNOWN，不以已讀claim改NONE。

本輪沒有生成actual reading claims。重建由exact candidate/master、相同WORK request、既有source-bound resolver/packer/intake及本工具定義完成。新工具必須在exact committed snapshot核對loaded-source；reconstruction PASS也只到結構一致，trusted producer/context-continuity attestation、真正理解與independent semantic review均未建立。

## Context bytes與未過gate原因

| Package | 原mandatory bytes | 補充unique bytes | selective pack bytes | 原target | pack超額 |
|---|---:|---:|---:|---:|---:|
| P01 | 915209 | 76040 | 326281 | 131072 | 195209 |
| P02 | 866534 | 76040 | 422465 | 131072 | 291393 |

最大的原source包括BFF/Python OpenAPI（216252/204713bytes）、含歷史CURRENT（88326/60363bytes）、manifest50903bytes及dataset fixture/status/ledger。重複值雖已去重，P02保留全部endpoint/schema、auth與錯誤契約，另有完整prose/治理binding與metadata；P01也不能刪掉required quality/correction/framing/拒絕條件。補充來源76040bytes不假装計入舊compiler已有清單：另列required-source debt，原mandatory gate保持原算式。

| 解決候選 | 所需證據／目前界線 |
|---|---|
| Lossless shared schema/JSON去重 | 已有owner；目前仍超額，不能宣称gate PASS |
| Compact CURRENT/status/governance projection | 全部current binding/positive-empty/歷史trigger須可解析；accepted resolver migration未授權 |
| Stable section IDs與bounded semantic closure | 本map提供追溯起點；雙向引用、安全negative/adverse evidence須獨立review，不能靜默截字 |
| Explicit successor aggregate-budget/continuity decision | 若確實仍超限，提交精確新語意；不變成每批128KiB、不用token估算免除義務 |

## R06-SOURCE-01 / R06-SOURCE-02

R06-SOURCE-01（P1／REVIEW_AT_CHECKPOINT）：active negative_assertions在original mandatory清單缺席。本輪將13個denied及7個invariants全量對應為required supplement，並核對exact1496-byte source；原resolver沒有改，source debt未結案。

R06-SOURCE-02（P1／LEVEL 3／受影響public CSV semantics HARD_BLOCK）：API `Queries, errors and audit`要求九欄instrument_id/contract_id/timeframe且無BOM；dedicated `CSV_V1`要求十欄source_code/amount/trade_count/tick_count且容許一個檔首BOM。現有format=CSV_V1 wire未宣告格式轉換adapter；不能用package旧public_semantic_gaps=[]或過往tests PASS掩蓋。

候選A：以explicit CSV_V1/P01 owner為準，另提出exact reviewed API/upload prose修訂；候選B：若兩格式確實都需要，明定版本與adapter責任、BOM/identity/quality lineage反例，不能隱式轉換。本輪未挑選或改寫任一source。阻擋受影響implementation/projection qualification，其他P00 mapping與publication inventory可完成。

## Publication及持久化界線

Entry manifest已固定c10c657、10commits、57檔（A43/M14/D0），含全部父鏈、每commit及淨delta、before/after blob/raw-content hashes。完成本輪local commits後另生成final HEAD manifest；兩者scope不同，不能把新commits加入舊核准。普通fast-forward只表示Git ancestry；候選仍REVIEW_PENDING而非ACCEPTED。

Final approval artifact存於repository外的本機輸出目錄，避免manifest把自身加入payload造成自我引用；其JSON/Markdown均持久保存，但不在push payload。Repository內entry manifest、R06 map/tests/continuation是LOCAL_COMMITTED候選；REMOTE_PUBLISHED維持遠端已知head。不存在acceptance、merge、controller activation或product grant。

## Risks / 下一個合法工作

先準備R06-SOURCE-02兩來源相容性decision與精確修訂候選供選擇／review，維持原安全契約；再完成stable semantic closure／negative omission qualification及trusted receipt/current registry bootstrap。RQ01–RQ06、原128KiB、actual golden、independent P00 review/acceptance、exact P01/P02 grant未完成。P00 closure0/8、7partial，journeys0/6，產品完成度UNCALIBRATED。維持Sol6.1 High，無切換必要。
