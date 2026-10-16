# MA03 — Market Data、來源、資料品質與可重播版本

Revision `candidate.4`；Owner B Data Pipeline／C Calendar／D Domain；AUTHOR_CHECKED／FORMAL_REVIEW_PENDING。

## Purpose／Source／Reuse

沿用 `B_DATA_PIPELINE.md`、`C_CALENDAR_CONTRACT.md`、`D_CANONICAL_DOMAIN.md` 與 existing MarketObservation。擴充多資產 source adapters、可固定的 DatasetSnapshot、quality/completeness 與實時 feed。既有 GAP-DATA-001 full completeness detector 是後續 runtime dependency，不能宣稱已實作；accepted fail-closed seam 不得移除。

## Models／Inputs／Outputs／Functions

RawObject：provider_object_id、licence_ref、received_at、byte_hash、immutable locator、coverage interval、format version、privacy tier。IngestionRun：run_id、provider/config/parser revision、raw refs、requested universe/window、observed completeness、errors、event frontier。CanonicalObservation：instrument/listing/session refs、event time(可 UNKNOWN)、received/recorded times、providersequence、type、prices/volume/units、quality flags。OHLCV 不足表達 NAV/yield/curve/Greeks，分 typed observations。

DatasetRevision：schema/parser/calendar/adjustment refs、partition manifests、correction lineage、coverage declaration、licence；DatasetSnapshot 固定 exact partition revisions、hashes、query/filter、selection chronology。PriceSeriesKind RAW/ADJUSTED/CONTINUOUS/NAV/YIELD 不混用；adjusted price/volume/totalreturn 各記 policy。Research 可看 correction retrospective snapshot；PAPER/LIVE only as-known-at cut，不偷未來資料。

`ingest(raw_ref,config_ref)`→validated partitions/quarantine report；`canonicalize(native,profile_ref)`→typed observation；`build_snapshot(dataset_ref,selection)`→immutable manifest；`query(snapshot,range,fields)`→ordered data＋coverage proof；`subscribe(scope,instruments,cursor)`→events/gap state；`repair_gap(request)`→new revision，不回填舊 snapshot。來源資料不能執行 embedded scripts。

## Business Rules／Lifecycle

Raw RECEIVED → HASH_VERIFIED → PARSED → QUALITY_CHECKED → PUBLISHED／QUARANTINED；partial success 清楚 partition coverage，不能標全 runcomplete。重匯相同 byte/config revision 冪等，same provider identity differentbytes 為 correction 候選。品質包括 duplicate/timeorder/tickunit/negativevolume/OHLC consistency/calendarbounds/corporateactions/sourcecrosscheck；合理0 volume 不是 missing。

CompletenessContract 固定 expected universe、interval/session、source selector、success/empty semantics、run scope 與 frontier。無交易而空集合必須有「成功且完整」receipt，空檔/timeout 不能宣稱市場無單/FLAT。Real-time sequence gap 進 DEGRADED，dirtydata 拒絕新 RiskApproval；已存在 order 依 MA08 safecontrol 處理，不能丟失 fill。

實時 latency policy per venue/feed/environment，不硬用一個秒數。occurred_at 無來源可信時間則 UNKNOWN；received_at 第一次 durable canonicalacceptance 固定。exchange tradingdate 用 calendar/session mapping，Windows localdate 或 UTCdate 不替代。Tick aggregate 包含 closedinterval、late-event policy；重算 bar 形成 revision，不能修改已使用 Run。

Parquet partition 建議按 dataset/instrument/session，排序 timestamp/source_sequence；exact layout 由規模調整，不將 filesystem 路徑當 ID。Raw bytes 保留/licensing/reacquisition 與衍生 retention 見 MA13。Indices/partition prune 為查詢效率，必保 snapshot closures。研究大檔 artifact 與 SQL metadata/reference 分開。

## Interfaces／Events／Dependencies／UI

Events RawCaptured、DatasetRevisionPublished、QualityFlagRaised、FeedGapDetected、SnapshotReady；schema 版本＋sourcehash＋scope。MA02 profile 是 canonicalize input；MA04/05 consume fixedsnapshots；MA07 feedhealth input；MA08 liveguard completeness；MA13 backupclosure。UI Market/Chart 顯示 source/asof/serieskind/quality/gaps；不把研究 adjustedclose 當可下單 price。

API `GET /api/v2/datasets`、`POST /api/v2/dataset-snapshots`、`GET /api/v2/dataset-snapshots/{id}`、`GET /api/v2/market-observations`；snapshotcommand key/hash/CAS，query 需 snapshotref/cursor/timebounds、返 coverage。大型資料返回 authorized contentref/page，不嵌全檔 DTO。Realtime 於 BFF 只讀訂閱，UI 重連先 snapshot+cursor，gap 不可假裝連續。

## Error／Retry／Security／Versioning

Provider rate limit/backoff 上限/斷路由 runpolicy；schema drift、licence denied、wrongtimezone/instrument ambiguity 均 quarantine。retry 重用 runcommand identity、newattempt receipt，不複製 observations；providercorrection 不同 revision。資料路徑 allowlistedprovider roots、拒絕 traversal/reparseunsafeobjects；personalaccountquotes/nativelogs 私有並 redact。Secrets 僅 Provider runtime，不能 Artifact/Git。

LegacyMarketBar adapter only compatible OHLCV instrument/currency/session；extensions incompanion，missingrequired newkind 返回 UNSUPPORTED。Real data acquisition 本次未執行；exactfields/sourcecapability 需 qualification，query API 設計不能宣稱 feedcurrent。

## Examples／Acceptance／Tests／Handoff

正例：14:00 收到13:59tick，保兩時間；夜盤 session 對次交易日由 calendar 決定；股票 splitadjustedseries 不覆蓋 raw。反例：feedtimeout 空集合變完整；兩 source C01 symbol 直接合併；後來訂正 bar 污染已完成 backtest；researchdownloadlicense 當 LIVEpermission。

Concurrency：兩 run 寫相同 partitionrevision 只允許 samehashduplicate，differenthashconflict；publishsnapshot 需所有 requiredpartitionverified，generationCAS 衝突重建 manifest 不重寫舊結果。客觀驗收：request/observedcoverage 可比、immutableSnapshot 可重取同 bytes、gaps 明示、requiredmissing 阻止下游 qualification。

測試：positiveemptyreceipt、clock/DST/sessionfixtures、latecorrection/duplicate/outoforder、OHLC/tickunits、point-in-time/leakage、rate-limitretry、manifestmissing/corrupt、subscriptiongapresume、多資產 typedobservations。Actualfeed/SQL/filesystempersistence 另 qualification；模型 fixtures 非 RuntimePASS。

WORK 單元：sourceparser、canonicalprofilesadapter、quality/coverage、dataset/snapshot、feedreplay、APIprojection；資料 fixtures 用非真實私有資料，保護 data/與既有 acceptedschemas。Knownlimits：資料量/吞吐/retention、providerlicences、actualcompletenessdetector 尚需實測。


## RCG04 candidate.4 mandatory consumer closure

[TRADING_CAPITAL_UI_ADDENDUM.md](TRADING_CAPITAL_UI_ADDENDUM.md)與MODEL/TYPE/API/EVENT同版為本章不可省略契約；external EconomicOrigin、全帳戶budget preview/confirm、PAPER SimulationSession、MarketBar DTO、servercold-reentry/error/cursor/stream及consumer映射隨exactsubject一起審核。原accepted語義不變，Runtime NOT_RUN。


## Candidate.5 有界修正承接

queryMarketBars inner/outer CursorRequest採canonical equal-or-reject，錯誤code/retry/effect走v2統一詞彙與versioned legacy aliases。

唯一詳細契約：`CAPITAL_TRANSPORT_VERSIONED_ADDENDUM.candidate.5.md`。原已接受範圍與尚未完成qualification保留。
