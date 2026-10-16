# RCG05 — Private Inventory／External Capture Journal／Backup Closure Contract

Revision `candidate.4`；Owner O Storage、Artifact Provider、K Recovery及各既有private-source chapter Owners。候選規格／模型例子；未讀真實私人資料、Secrets或資料碟，未執行SQL/Dump/Backup/Restore。

## 私人原文與保存範圍

SQL index只是查詢索引，SQL refs不能證明完整私人歷史。Private-source Owner以`OwnerInventorySnapshot`發布明確scope的saved drafts/LLM messages/results/人工decision/review/研究originals/工作規格檔、classification與requiredpolicy、generation/immutablemembers/source-state及attestation。Owner membership版本由現有Architecture/Operations來源列明：Registry Draft Owner、E/F Research、O Artifact Writer、WORK結果／Human Decision capture Owners等；新producer未註冊/coverage未知不能省略當作空集合。只掃folder或只查SQL均不足。

每PrivateInventoryEntry保持itemID/source state/ref；已captured未index與INDEX_FAILED合法但必納closure。Mutable/private工作檔需要Owner穩定version/close/quiesce或qualified snapshot才能capture；不穩定、missing/corrupt/hashconflict明列coverage issue。未保存memory/not-committed data標UNSAVED_MEMORY，不能宣稱已backup。required exclusion即使Owner已知仍PARTIAL；若Human另採納縮小某named restore scope，只能新CoverageProfile，不把舊FullPrivate回標COMPLETE。

## 三軸狀態／capture receipt

| Axis | 狀態／證據 | 不能推導 |
|---|---|---|
| capture | CAPTURE_PENDING→CAPTURED_VERIFIED；original bytes/hash/size＋external durable CaptureReceipt/journal sequence | SQL indexed、A/B protected、spec accepted |
| SQL index | NOT_INDEXED／INDEX_FAILED／INDEXED／UNKNOWN；index command/source revision receipt | content存在、原文完整、providerprotected |
| provider protection | A或B的local closure verify→sealed set→ProtectionReceipt；每provider獨立 | 另一provider已保護、RestoreDrill PASS、舊grant重啟 |

Criticalcapture仍先CreateNew exact bytes／verify／durable provider→external append-onlyreceipt journal→SQL index；captureack須已durable verifiedreceipt。Index失敗receipt/content留externaljournal，reconcile同receiptID且冪等不發新Acceptance；object必由journal/inventory納下一set。Journal segment和its manifest本身也是required backupcontent，不能只保存frontier hash。相同object多來源必保留所有originrefs，dedup exactID/revision/hash不抹source lineage。

## 最小coordinated Backup Cut：不假跨系統原子提交

1. 根據固定ProducerMembership/RetentionProfile選sourceOwners；檢查capacity/targetprovider、建立SetIntent以及Store GC guard，freeze或capture Owner mutable saved versions。未能取得explicitcompleteinventory先保PARTIAL，不能繼續宣稱FullPrivate。
2. 取得bounded capture-publication barrier：已ack的capture receipts必已append於externaljournal。禁止新receipt被ack或被SQL新revision引用，固定各journal contiguousfrontier/segmenthash與Owner inventorygeneration。Writer可以暫存未ackstaging，但其pending內容要明示，不能認為已保存原文。
3. 保持capturebarrier取得只讀SQL exported snapshot，讀同snapshot的Draft/FormalGit/AppliedProjection heads、committed eventfrontiers、publicationUnknown/Pending/Conflict及required SQLArtifactrefs。SQL index可以落後已capture journal，這是可保存的真實狀態；不要求三head相等。若任何SQLref不屬已固定capturefrontier/inventory或noverifiedCaptureReceipt，abort或PARTIAL重試，不補查latest拼cut。
4. `BackupInventoryClosure`是**SQL refs ∪ fixedjournal所有acknowledgedcaptures ∪ fixedOwner inventory saved bytes ∪ journal/inventory/catalog/bootstrap/toolchain requiredobjects**。每origin均列明。取得全closure immutablepins後才解除粗capture/GCguard；pin保持到dump/copy/manifest/externalcatalog完整封存或explicitabort。SourceOwners不能提供barrier時可使用boundedquiesced registeredwriters profile；未qualifiedonline profile不宣稱online samecut。
5. Dump使用同SQLexportedsnapshot且coordinator存活至完成；copy exact pinnedbytes/heads及上述extraSQLcontent。BackupCoordinationReceipt固定每causalcut，不聲稱SQL/journal/file原子交易。新capture可在後續繼續寫，只进入nextset。
6. provider objects逐一size/hash/locator/可信source驗證；coveragecomplete且所有requiredclosureobjects在該provider才封存COMPLETE_VERIFIED setmanifest/catalog。Capture/index/protection独立狀態全部保留。最後以sealedmanifest digest發布ProtectionReceipt；restorequalification仍是另一receipt。

SQL snapshotfrontier不是sequence MAX；journal也須contiguouscommitted receipt proof。多DB交易／研究系統的productCheckpoint/Quiesce要求仍沿原K/J contracts；URMS engineering BackupCut不是AccountCut，不能替代economiceventdurability。

## Manifest／external catalog／A與B自足

BackupCut/SetManifest新增owner_inventory_refs、external_capture_journal_cut_refs、inventory_closure_ref、coordination_receipt_ref。BackupSet另外保存required_bootstrap_refs。ArtifactManifest指sameCut/InventoryClosure，所有entries有origins/capture/index/providerverify。Partial/missing/conflict保存exactID/revision及losswindow；Hash/摘要沒有content時仍MISSING。

A短期高頻與B長期週期/重大節點模式沿MA13，不另建Scheduler/Controller。B set的journal segments、Owner inventory、allprivateobjects、Gitexactcommit/schema/contracts/toolchain/roles/extensions/trustpublickey/objectlocatorcatalog都必在B本地closure或declaredindependentkeyescrow。B不是A mirror；A GC不能驱动Bdelete。從無A/無原SQL的新隔離環境，B bootstrap能找到retainedset全部content並verify；單有cipherbytes但key不可得UNRECOVERABLE，不能以hash當key。

Hash環：Inventory/Journal/Closure manifests不含自身hash；其member refs不遞迴展開。Current set的ProtectionReceipt在set sealed後另append外catalog，不讓setmanifest反向引用尚未產生的自己ProtectionReceipt；Artifact entries可以記以前set的protection history，今回protection結果由catalog/receipt承接。

## Restore與Fresh Re-entry

GIT_ONLY RestoreRequest只需exact GitRebuildPlan、freshisolatedtarget/grant，不以SQLBackupSetManifest作input前提；重建正式registry identity/relations，private refs MISSING/UNVERIFIABLE，不補Acceptance。FULL_PRIVATE/HISTORICAL_SAVED_CUT需要compatible verified retainedset，恢復SQL+immutablecontent+journal/inventory；已capture INDEX_FAILED原樣保留待冪等索引reconciliation。歷史只能saved compatiblecut，沒有PITR時不interpolate指定time。

所有restore後RecoveryHold/newEpoch/FreshReentry；舊writerlease、claim、WORK/CODEX/Broker/LIVEgrant不復活。MISSING requiredbytes/journal/inventory→PARTIAL/HOLD，找其他verifiedset或Human lossdisposition，不重新生成同原文/研究結果。RestoreTarget必須verifiedempty且exactgrant；現有交易DB、data/、Secrets、現盤不觸。

## Decision table／expected failure semantics

| Case | Detection／Result | Recovery／Human |
|---|---|---|
| Captured decision SQL index失敗 | journal枚舉、INDEX_FAILED；bytes仍必列required | Backup可COMPLETE若objects/journal均verified；restore保持待索引、sameReceiptIDreconcile |
| 未索引Draft/LLM saved file | Owner inventory exactsource state，穩定capture | 納closure；來源mutable無法freeze→PARTIAL，不自造summary |
| Inventory未知或registeredOwner未回應 | ProducerMembership/attestation差異 | COVERAGE_UNKNOWN/HOLD；只stop受影响FullPrivate claim，SQL-only备份可标partial |
| SQLsnapshot refs超過journalcut | capture/reference causal proof mismatch | abort/retry compatiblecut，不抓latest補洞 |
| Backup期間新capture/revision | fixedfrontier/version/pins | 只進nextSet，舊set immutable |
| 同objectID/rev不同hash | closure equality conflict | QUARANTINED、不FULL；Humanintegrity調查 |
| A被刪或故障 | Bbootstrap/catalog/localobjects/keyproof | B獨立restore保原retainedcontent；losswindow以Bcut明確 |
| B缺journal segment或一原文 | required closureverify失败 | PARTIAL_NOT_FULL_RESTORE_CAPABLE；copyexactverified來源或选另一set |
| 外catalog缺失、blobs仍在 | originalsetmembership/trustproof不足 | reconstructcandidate+人工reconciliation，不冒稱原FullRestoreSet |
| onlyGit | 無private set | registrysameID，original privatehistory不可重造；lossledger/HOLD |

## 作者檢核與後續資格

`RCG02_RCG05_FIXTURES.json`含BackupCut正常／financialAccountCut拒绝、capturedbutunindexed閉包、mutablepartial、B-only、RestoreRequest三分支、manifest-as-inputnegative等合成例子。Author source/model checks不等actualSQLdump/restore。PostgreSQL exported snapshot、WindowsCreateNew/durableflush/pins/reparse/TOCTOU、journalfsync/Crash、twoindependentphysicalvolumes/keyrecovery、B無SQL/無A restore、historicaldrill等須既有WORK编译后合法disposablequalification。没有NAS/Cloud/PITR runtime前置扩张。


RCG06 integration clarification：MA13-U06 `RestoreRequest → RestoreReport`回傳工程/私人coverage、exactRegistry/Git/Artifact refs與RecoveryHold；Git-only沒有金融AccountCut時不得虛構tradingRecoveryStatus。產品交易K_RECOVERY的既有RecoveryStatus及FreshReentry仍獨立；storagecontent verified不授brokercurrent/tradingready。
