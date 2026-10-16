# MA13 — Storage、Critical Capture、A／B 備份與可驗證恢復

Revision `candidate.4`；Owner O Storage／K Recovery／Security；AUTHOR_CHECKED／FORMAL_REVIEW_PENDING。頻率、容量、RPO/RTO 均候選；未啟動備份或實際 Restore。

## Purpose／Source／責任

Owner 確認三顆獨立實體碟：system、A 短期高頻、B 長期獨立；不預設 driveletter/location。承接 CG5/CG6 與 acceptedRecoveryCut/FreshReentry。正式 Git 可重建程序/schema/IDs/relations/contracts；私有 SQL＋Artifact 備份恢復完整工程歷史；Hash 不能恢復原內容。以下是設計契約，不把本次 sourcepreservationbundle 當全系統 BackupSet。

## Data Classification／Retention Owner

| Class | 例／主要責任 | 保存/保留/還原 |
|---|---|---|
| REPRODUCIBLE | derivedquery/progressprojection/buildcache、可固定 inputs 重算資料 | Git+sourceclosure 可重建；cache 短保；重算與 originaloutputs 不同 identity |
| SOURCE_REACQUIRABLE | 公開行情/參考商品資料且 licence/source 保證可重新取得 | source/version/licence/coverage 保留；provider 消失則重新分類，不保證再取得同 bytes |
| PRIVATE_BACKUP_REQUIRED | SQLdraft/tasks/revisions/relations/receipts/audit、詳細規格/LLM/研究 sources/outputs、privateoperations/config | SQLconsistentdump＋immutableartifactset＋manifest，A/B 保護 |
| IRREPLACEABLE | 原 Humandecision/reviewevidence、首次 sourcebytes、不可再取得市場資料/原研究結果 | 先 criticalcapture 再 ack；長期 B 保留，不能用重新跑/summary 取代 |
| SECRET (額外 security 標籤) | tokens/CA/password/keys/必要環境重新配置資訊 | secretprovider 或加密 escrow，keys 分離；不進 Git/一般 Manifest/plainSQLrolepassworddump |

分類是每 object/policy 與 reacquisition 證據，不是整個 folder 同級。Git 正式 registry/schema/migration/contracts/source/acceptedbinding 由 GitPublisher 保存＋privatebundle 保全；Artifact bytes/version 由 ArtifactWriter；ResearchSnapshot/output 由 F；行情 datasets 由 B/C；economicjournal 由 J/K，**工程每數小時 backupRPO 不適用 LIVEfilldurability**。非可重生內容長保有 Ownerdisposition，不能 capacity 不足默刪。

## Artifact Capture／Availability／Models

ArtifactRevision{artifact_id,revision_id,raw_hash,hashdomain,size,media,classification,source_ref,createdactor/time,immutablecontentref}；ArtifactIndex 是可查 metadata，contentavailability 另外 CAPTURE_PENDING/CAPTURED/VERIFIED/MISSING/CORRUPT。ProtectionReceipt 另 A_PROTECTED/B_PROTECTED/OFFSITE_PROTECTED，capture 成功不等 A/B 保護成功。

Criticalcapture protocol：receiveexactbytes→allowlistedCreateNewstaging＋boundedsize/hash→durableclose/flush→immutableprovidercontentaddress→verifybytes→externalCaptureReceipt→SQLindex/decisionreceiptref→ack 可讀 exact 內容。SQL 失敗時 externaljournal 可 reconcile；filesystem 失敗不 ackcaptured。不能只 SQLoutbox 保存尚未落地的 Humandecision，再假設備份可重建原文。Externaljournal 自己需 A/B 保護；Protectionpending 可明示損失風險，重大 acceptance 前 requiredpolicy 必 protected。

既有 chat 摘要/檔案 metadata 不是全文；messageID/rawcontenthash/partialcoverage 明示。不可變 capture 內容原樣，查詢 searchindex 可重建；GC 與 retention 不改 capturelineage。Keys/secrets 不含在 capture。

## A Short-term／B Long-term 最小策略

| Policy | 初始候選（可調） | 驗證/清理 |
|---|---|---|
| A Artifact incremental | 每15 分鐘 batch＋criticaleventcapture 後優先 queue | contenthash/size/manifestverify；保30 日或依分類 longer |
| A SQL consistent dump | 每4 小時＋重要變更前 | customFc＋snapshotcut；保48rollinghoursets、14dailysets |
| A milestone | schema/acceptedbaseline/privatecritical 內容更動前 | newself-containedcompatibleBackupSet，不覆寫 |
| B long-term | 每週完整 compatibleSQL/artifactclosure | weekly12 份、monthly12 份、annual/milestone 長保需 Ownerpolicy |
| B critical evidence | 重大 decision/review/acceptance/Schema 節點額外 copy | 保存 exactbytes/contracts/cut/catalog，不等普通 mirror |
| Integrity/restore drills | 每次 backuphash＋每月輪替 actualisolatedrestore | 驗 testA/B/C、latest 及一 historical；記版本/時間/失敗 |

A/B 是 providerID/VolumeIdentity/policyroot，不 hardcodeD:/E:。B 可 contentdedup，但每 retainedset 必 closurecomplete 於 B，Bcatalog/referencecounts 獨立；A 刪檔不能觸發 Bdelete。Bpromote 先 verifyallobjectslocalpresence 再 markPROTECTED；Copy 只有 blob 而缺 manifest 不 complete。刪除只依該 providerretention、legalpin、復原驗證與容量 policy，不雙向同步 deletes。

Failures retry bounded1/5/15/60 分鐘候選，providerIOerror 先 stopretrystorm、不干擾 productprocess；兩次連續失敗/watermark 超 RPO/criticalprotectdeadline 觸警。capacity80%warning/90%critical 是候選；優先清可再生 cache/已 expiry 不 pinnedset，無可刪項則 stopnewbackup/report，不刪唯一 IRREPLACEABLE。Alarm 在 existingWORK/opsnotificationowner，不另 controller。

## PostgreSQL Backup／Restore Contract

採第一版單一 URMS DB customformat logicaldump。官方[pg_dump](https://www.postgresql.org/docs/17/app-pgdump.html)提供單 DB 一致性 snapshot；globalroles 另需受控重建清單，[pg_restore](https://www.postgresql.org/docs/17/app-pgrestore.html)用於 archive 還原。資料庫一致性不證 Artifact/Git 同 cut，不證 extensions/roles/keys/OSrestore。

BackupContract 含 servermajor/minor、dumpclientversion、DBidentity/schema/migrationrevision/extensions/collations/encoding/timezone、roledefinitions(無 secret)、grantpolicy、dump/hash/TOClist/exitstatus、snapshot/frontiers、qualifiedrestoretoolchain。禁止 rawcopyrunningPGdatafolder 當 logicalbackup。dumpclient/server 相容 matrixpin；不能盲新版本 restore 至舊版本。

Restore target 由 Human/existingowner 精確授權的新 isolatedDB/container/volume，默認無 brokernetwork/credentials/controller。驗證 expectedemptytargets、source 可信性/TOC/roles/extensions/schema，再 controlledpg_restore；archive 可含 SQLcode，未信任 backup 不能 superuser 盲 restore。restore 失敗棄置隔離 target（需單獨 deletegrant），原 DB/sourcebackup 不動。schema 遷移由 MA16gate，僅有 migrationfiles 不準對現庫執行。

## SQL／Artifact／Git 同恢復 Cut

1. 所有 SQL 引用只指已 CAPTURED immutablebytes；newartifactwrite 先落地再引用。依固定privateProducerMembership取得OwnerInventorySnapshot並捕捉saved工作內容，建立capture-publication barrier／GCguard；固定ExternalCaptureJournal contiguousfrontier，包含已capture未index／INDEX_FAILED原文。backupwriter不是economicwriter。
2. 開始 REPEATABLE READ 只讀 cut transaction 並 exportsnapshot（[PG snapshot functions](https://www.postgresql.org/docs/17/functions-admin.html)）；從同 snapshot 讀 DraftHead、FormalGitHead、AppliedProjectionHead、committed perstream eventfrontiers、publicationstates、所有 requiredArtifactrefs。MAXallocatedsequence 不是 committedcontiguousfrontier。
3. 使用支援 `pg_dump --snapshot` 的 pin toolchain 在 snapshot 存活期間 dump，取得完全同 SQLsnapshot；exporter 保持活到 dump 完成。若 profile 不支援此同步，退回 boundedquiescedengineeringwriter 模式，記錄 barrier/start/end，不能 claim online samecut。
4. 此snapshot SQLrefs與同cut OwnerInventory／ExternalCaptureJournal／bootstrap requiredobjects取union成BackupInventoryClosure，檢查SQL引用未超過capturefrontier；先pins所有immutablebytes再解除粗barrier。copy/verify原文與Gitexactcommit/contracts；newversions只進nextSet，未索引原文不得漏掉。
5. OwnerInventory未知／必需mutable尚未capture／journalsegment缺失／optional對象缺失→coveragepartial；requiredprivate不可再生對象缺失→PARTIAL_NOT_FULL_RESTORE_CAPABLE，dump 成功不等整套成功。完成 hash/TOC/catalog，再 externalCompleteReceipt；最后 releasepins。
6. Pending/Unknown publications 原樣保存，restore 再 queryGitexactoutcome/reconcile；不在備份時擅自視為 published/accepted。

跨 DB 經濟系統另各自一致性 cut/causalbindings，不假設一 URMSsnapshot 覆蓋全部交易 DB。若多 DB 聯合 restore 必要，要專屬 manifest/frontier 協議/停寫 barrierqualification。RPO 只有 verifiedcompleteBackupSet 保護范圍；capture 但未復制 A/B 可能 host 損失。

## Backup Set Manifest／External Catalog

候選 successor schema `backup.set.v2`（原closed v1保留、經versioned companion/adapter採納）：setID/revision/status/createdinterval；canonicalrepo/mastercommit、registrySnapshot/schema/contenthash；SQLobject/hash/size/schema/toolchain/extensions/collation/roles；SQLcommittedEventFrontier、DraftHead、formalHead、appliedProjectionHead；publicationintent/receipt/pendingunknownconflict；OwnerInventorySnapshot/ExternalCaptureJournalCut/BackupInventoryClosure/BackupCoordinationReceipt exactrefs；ArtifactManifest exactIDs/revisions/hashes/class/required/presence/origins/indexstate；coverage/exclusions/missing/validation/drillreceipt；providerID＋VolumeIdentityopaqueRef＋safeLocator；retentionpins/expireafter/compatibletargets/keyhandle(notkey)。

ExternalCatalog appendonlyJSONrecords/manifestobjects 存在 A 與 B 各自，無需 SQL 可讀；setmembership/cataloghash 鏈＋ACL，加密備份清單僅可泄露必要 opaqueID/hash/size/class，敏感 title/account 名稱不明文。Authenticity 需獨立 trustreceipt/簽名 keypolicy，hash 只能 detectcorruption 不能防有權者換 manifest+content；私鑰與備份分離、verifypublickey 可隨 bootstrap 保全。第一版可手動 sealedhashwitness＋immutableACL，必須標 tamperprotectionlevel 而非宣稱抗 ransomware。

## Restore Tests／Historical Recovery

TestA Git-only：潔凈隔離獲取 verifiedGitcommit→compatibleSchema/migrations(registrybootstrap 只在 disposable)→sameIDs/codealiases/雙樹/typedrelations/deps/crosswalk/contracts→private 缺 bytes 顯示 MISSING/UNVERIFIABLE→不造 Acceptance／恢復后 HOLD。Expectedidentity/relationshipsethash 與 Gitmanifest 一致；程序 build/tests 另測，不憑 registryimport 稱整程序 ready。

TestB FullPrivate：選擇一個 COMPLETEcompatibleSQL/Artifact/Gitset→verifycatalog/signature/hashes→isolatedroles/extensions/dbrestore→artifactnamespace 恢復→校驗所有 requiredrefsbytes／eventfrontiers／publicationheads／receiptapply→freshRecoveryHold。Runreportsoriginalbytes 保留，重新計算是 newrun。

TestC Historical：指定 formalcommit 或 timequerycatalog 找到 compatiblecut；有多個候選返回其 coverage/approximation/lostwindow，人選，不由 timestamp 插值 fabricate 歷史。保對應原 schema/contracts/toolchain、舊 Artifactrevision，B 無需 A 也能 restore。PITR 未采用時**不能保證任意秒級時間點**；只能保存的 cut。

## Failure Recovery Matrix

| A–P | 偵測/損失範圍 | 恢復/自動與人工 |
|---|---|---|
| A A 壞 B 好 | volume/hash/drillfailure；B 最近 cut 後私有更新可能丟 | 從 B 完整 set 隔離 restore；Human 確認 lostwindow/replaceA |
| B B 壞 A 好 | B 不可達；長期歷史若 A 已刪可能不可恢復 | A 最新 set；重建 B 新 provider，歷史損失 Humandisposition |
| C 只有 Git | A/B 不可得 | TestA 正式閉包；privatehistory 不可重建，HOLD+lossledger |
| D dump 好 artifact 壞 | requiredhash/coveragefail | PARTIAL，不 FullPASS；retryexactobjects/前 compatiblecompleteSet，critical 需 Human |
| E backup 中寫入 | snapshot/head/refdiff | 固定 cut+pins，不混 newrevision；barrier 失敗 abort/retry |
| F B 被 A 清理聯動 | providerindependentretention/asserttest | 拒絕 delete 鏈；若已刪其他 copy 恢復，Human 調查設計缺陷 |
| G manifest 遺失 | catalog 對象缺但 blobs 在 | reconstructcandidate 清單/SQLrefs 校驗；不能自認證原 cut/trust，Humanreconciliation |
| H hash 不符 | byte/signatureverify | quarantine，不 restoreclaim；其他 verifiedcopy；tamperHuman |
| I Gitpublished 投影落后 | heads/pendingjournal | canonicalGitverify 后冪等 import，不改舊 Acceptance |
| J publicationunknown | outcomeUNKNOWN | queryGitrepo/tree/subject，ambiguousHOLD/Human，不盲 commit |
| K SQL 有私文缺 | refclosureverify | MISSING/PARTIALPRIVATE；找 exactbytes，無則明確損失，不補造 |
| L reimport 重復 | command/snapshot/eventunique | samehashno-op；differenthashconflict 人工，不 newID |
| M 容量不足/長期中斷 | space/lastcompleteage/RPOwatermark | boundedretry/報警/安全 GC；唯一歷史不可自動刪 |
| N 勒索/未授權修改 | hashes/ACL/monitor/offlinecopy | 隔離 host/credentials，不從被污染 set 恢復；Humansecurityresponse |
| O PG/schema 不相容 | compatibility/preflight/drill | 原 toolchain 隔離 restore 再授權 migration，不能 overwrite 生產 |
| P 覆寫真實原資料 | targetidentity/path/reparse/grantgate | defaultdenyexistingtargets；freshisolatedonly；任何真實變動 Humanexactgrant |

## Security／Provider Extension／Capacity／RPO RTO

Provider port `put_immutable/get_verified/list_sets/pin/unpin/promote/check_capacity/retire_set`，bindproviderID、volumeidentity/physicaldeviceproof、allowedroots、permissions、encryption/keyhandle、policyrevision；unplug/reletter 不默默換另一盤。Windows path/reparse/UNC/device/ADS/case/TOCTOU 完整拒絕；見[Windows path](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file)、[volume API](https://learn.microsoft.com/en-us/windows/win32/fileio/volume-management-functions)。服務帳戶僅 readsource/writebackup，productaccount 無 Bdelete；密鑰獨立 encryptedescrow 與恢復驗證。

B 常態在線仍受 host/ransomware/電源/火災影響，雙 physicaldisk 不是離線/異地保證；未來 NAS/Cloud/offlineprovider 加 auth/capability/network/immutability/signedcatalog，但不成為 P00runtime 前置。WAL/PITR 僅當 measuredRPO/volumejustify，專屬 source/cut/restorequalification。

候選工程 RPO：A artifacts15 分鐘 batch、SQL4 小時；criticalcaptureack 前 localdurable 但 A/Bprotectionlag 單獨顯示；Bweekly 可能7 日 losswindow。RTO 候選 Git-only1 工作日、FullPrivate4–8 小時，在容量/throughput/toolchain/drill 前皆 UNMEASURED，不產品 SLA。LIVEeconomicdurability 須原 J/Ktransaction/日志/外部 reconcileGate 另定，不能允許4 小時丟 Fill。

容量公式：A≈48×compressed_dump_size＋14×daily_dump_size＋unique30dayartifactchanges＋restorestaging＋20%headroom；B≈retainedSQLsets＋所有 retainedclosureuniqueartifactbytes＋catalog/keyescrow＋headroom；SQLsets 可按真實 dedup 減，未實測不承諾。diskinventory/capacity/write-rate UNKNOWN，本輪不讀實際資料盤。

## P00／Implementation／Acceptance／Handoff

P00 先定義 class/capture/cut/manifest/authority/restoretarget/RecoveryHold 與客觀測試，不需 backupUI、NAS、scheduler、PITRruntime。授權 URMS 后實現 capture/storage/dump/catalog/A-Bcopy、disposableRestoreDrill；V1data/runtimeacceptance 需對應 research/privatehistory 與 economicrestoreGate；futureproviders 后續。

驗收：A/B 獨立 closure、samecut、criticalbytes 可找、外 catalog 無 SQL 可讀、keysseparate、explicitmissing/loss、freshreentry。Tests source/model、真實 SQL/Windowsfile、TestA/B/C 各層級；本次只有 source/model 設計，實際 RestoreNOTRUN。WORK 嚴禁原交易 DB/目錄、data/、secrets 或 backupjobs；targetverifiedempty 與 exactgrant mandatory。

## 精確文件下載及模擬 wire binding

getArtifactContent 返回 ContentDescriptor；getArtifactBytes 是獨立權限再驗證的 VerifiedBinaryStream/BinaryContentMetadata，不返回 ArtifactRevision JSON 代替原始內容。PAPER SimulationSession 與 LAB ResearchRun 的 STANDARD 研究方法分開；startSimulation/session lifecycle 僅 PAPER admission。

## RCG05 / S6-TEST-02 necessary typed companion

[PRIVATE_INVENTORY_BACKUP_CONTRACTS.md](PRIVATE_INVENTORY_BACKUP_CONTRACTS.md)固定SQL未索引originals／LLM工作檔／capturejournal的完整備份閉包。MA13-U03正例input是BackupCut，AccountCut為拒絕反例；MA13-U06 input是RestoreRequest，Git-only／FullPrivate／HistoricalSavedCut各有oracle，BackupSetManifest不是request。Fixtures見[RCG02_RCG05_FIXTURES.json](RCG02_RCG05_FIXTURES.json)。實際dump/Restore皆NOT_RUN。


RCG06 integration clarification：MA13-U06 `RestoreRequest → RestoreReport`回傳工程/私人coverage、exactRegistry/Git/Artifact refs與RecoveryHold；Git-only沒有金融AccountCut時不得虛構tradingRecoveryStatus。產品交易K_RECOVERY的既有RecoveryStatus及FreshReentry仍獨立；storagecontent verified不授brokercurrent/tradingready。


## Candidate.5 有界修正承接

Body capture journal + Owner inventory precede SQL indexing; capture/index/protection axes separate; no backfill and no crossstore atomicity claim. Catalog body hash/rawbytes/source provenance distinct.

唯一詳細契約：`BODY_CAPTURE_READBACK_CONTRACTS.md`。原已接受範圍與尚未完成qualification保留。
