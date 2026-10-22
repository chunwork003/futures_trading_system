# MA02-U01 — Source-bound Qualification Delta / WO Candidate Preparation

你是 futures_trading_system 的 WORK／Executor 準備責任端。本工作只允許唯讀核對與隔離候選文件；不是產品 Coding、正式 Qualification、Compiler Invocation、Grant 或 Writer 授權。

Repository：
D:/00_Learn/量化交易/Code/futures_trading_system

本輪固定恢復入口：
C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/b3-fresh-reentry-policy-successor-20261022T052152Z/README.md

先讀此根的 DURABLE_CHECKPOINT.json、MA02_U01_PREPARATION.candidate.json、SOURCE_AND_GIT_AFTER.json；再依 AGENTS → docs/CURRENT_STATE.md → automation/governance/master_manifest.v1.yaml → active policies → docs/CURRENT_WORK.md → 最新適用 Qualification/Grant/Review/STOP 重新取得權威。若 checkpoint 尚未列檔或 Hash 不符，停止受影響用途；不得用聊天摘要補值。

精確原規格：
C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/ultra-b3-precompiled-queue-addendum-v1/unit_specs/MA02-U01.spec.json
raw SHA256：033a3737a4f3e2823570a3dfec844f0fdc4f43ad97f8c676e508a1f978f02608
Unit ID：69b6baec-4e0d-42df-ab4f-5900e97f48b6
plan revision：candidate.7
plan revision ID：ef3b999d-d11d-5bf3-a359-94367868e2bb
原 Unit selected-body canonical SHA256：dce2e833f1f5a9d00687ed025f1f84e8a378651cb09a11f5d8b3ed847074cdbd
有效外部採納 Subject 是 v9 SOURCE-CLOSURE-PAIR01；內文歷史 v7 標籤保留，不能依名稱改選舊基準。

原需求：Permanent Instrument／Listing bridge；同 symbol 不同 venue 是不同永久 Instrument identity；舊 integer mapping 不變。保留 InstrumentRevision／ListingRevision、listInstruments、getInstrumentRevision、MA-DTO-v6、UI03 及全部 required IO/Consumer，不擴張為真實 Broker、SQL 或全部 Registry。

唯一直接依賴為 MA01-U01。讀：
automation/work_orders/MA01-U01-MANUAL-01.acceptance.json
docs/program/decisions/MA01-U01-FIRST-RESULT-ACCEPTANCE.owner.v1.json
並核對其引用的 immutable Result body、Fresh Review、WORK Intake、三項 accepted products。Result 的歷史 outcome 不重寫；外部接受收據是 status 權威。僅可提出符合 intended source/schema/profile/environment/operation/cut 的 scoped reuse，不轉授 U01 的 Manual Qualification、Grant、Writer 或 Invocation。

依序完成：
1. 核對已固定 MA02 packet 的 Source/readback/9 Fixture selector，僅查 Delta，不重審 B3／Bridge／U01。
2. 從適用 accepted Profile／Amendment 查明 MA02 是否已在允許 intended-use 範圍。沒有就固定 MA02 專用 applicability／替代保證決策候選與 Narrow Source Review subject。不得以 HUMAN_DIALOGUE 名稱自動豁免 C3/C5/C6/P00，也不把全部 P00 closure 無差別前移。
3. 固定 MA02 Source／Context／Operator／Producer／Consumer／Continuity／Result／Intake 所需的實際 use qualification 差額。舊 U01/U02 收據不可直接轉授；新的受控試驗另需 exact Grant。沒有已授權模型 API 資源；不反覆索取，也不呼叫 API。
4. 使用既有 native WORK 契約與合法 accepted binding 準備 singleton Program/Package/WO 候選；PK02 是 planning group，不可填入不支援的 closed Pxx schema。不建立第二套 Compiler。
5. 只提議三個產品路徑：
domain/instrument_profiles.py
domain/asset_valuation.py
tests/architecture_companions/test_ma02_contracts.py
在當下核對 CREATE_NEW／preimage；目前提案不是 Allowlist Grant，不建立檔案。
6. 全部 9 case IDs、fixture revisions／selectors、正向／負向／race Oracle 與必需 regression 原樣納入；測試為 NOT_RUN。實作時的候選 targeted command：
python -m pytest tests/architecture_companions/test_ma02_contracts.py -k ma02_u01 -p no:cacheprovider
本準備工作不得執行不存在的測試或任何 SQL test。
7. 原 risk HIGH；planning L2 是最低提案，實際 identity/source semantics 不得低於適用 L3。編列獨立 Reviewer／Intake／ASSET_CONTRACT_ADOPTION gate。
8. Forecast 不可觀測為 UNKNOWN＋原因；Hard budget／外部 API cap／correction 次數／時間／Executor／Writer／Result Profile 由新的 exact決策固定，不繼承 U01 cost acceptance。沒有有效 native Grant 不得 invoke。
9. 保存候選 WO、資格差額、Source/readset/hash、scope/reuse proof、未取得的 Receipt 及唯一最小下一個 Human request；不自行簽發、Activation、Git 或 Coding。

目前 Accepted Units 1/96。MVP 結構候選為 MA01-U05、MA02-U01、MA10-U01、MA11-U01；它們不是 executable frontier。MA01-U02 資格支線不在 57-Unit MVP closure，不能無條件阻擋 MA02；也不能刪除其原義務。不得加全 Package completion barrier。

完成點：提出「已有哪些可重用正式證據、哪些 exact applicability/use qualification/WO/Grant 還缺」，使下一個 Human 只處理真正必要的精確授權。政策 successor 即使 source review 通過仍須 Owner 採納及原制度適用整合；不是此 Unit 的 Coding Grant。

禁止：產品 Coding、native受控Compiler/Dispatch、Grant/Writer materialization、Git index/ref/Commit/Push/Merge、SQL/Migration、Broker/LIVE/Runtime/Controller、覆寫任何 accepted evidence。任何未知保持 UNKNOWN，不以 Mock 或計畫當 PASS。

