# MA16 — 部署、環境、組態、Migration 邊界與可持續營運

Revision `candidate.4`；Owner L Safety／M Service／N Application／O Workspace；AUTHOR_CHECKED／FORMAL_REVIEW_PENDING。

## Purpose／Source／Reuse

沿用 M/N/Oblueprints、existingconfig/secrets/recovery 與 WORK 生命周期。第一版 Windowslocalhost 開發/研究環境；futureNAS/Cloud providercompanion，不要求現階段運行完整 container/Kubernetes/cloudscheduler。部署只有版本化 contract，沒有實際 install/start/migrate 授權。

## Deployment Manifest／Data／Inputs／Outputs

DeploymentManifest＝releaseID、Gitexactcommit＋registrySnapshot、chapter/contractbundlehash、Python/.NET/Node/DB/toolchainlocks、components/ports/interfaces、envscope、logicalstoragebindings、config/schema/migration/extensions、authproviderprofile、secretHandlesavailability、networkpolicy、backup/restorecompatibility、qualification/admissionrefs、recoveryepoch、expectedservicehealthchecks。每 environment 獨立 namespace/account/database/artifactproviders，不用同 folder 開關 MODE 來假隔離。

ConfigRevision 聲明 typedvalues/units/source/owner/effectivetime，不存 secretbytes；ConfigHeadCAS。Sensitivechanges auth/risk/broker/account/instrumentset 要求 impact/review/newadmission，普通 displaysettings 可 scopedrevision。Runtimefence 只由 existinggrant/leaseauthority；Windowsvolumeidentity 實際資格需 providerpreflight，不猜 driveletter。

## Host／Auth／Ports／State

Candidate topology：Reactstatic/UI servedbyASP.NETBFF、PythonprivateAPI 監聽 loopback、PostgreSQLprivateendpoint、isolatedresearchworkers/operationaladapterprocess、ArtifactProvider 私有 roots。OnlyBFF user-facing；Python/DB 不可 publiclisten 無 auth。固定端口不是 contract，configurationrefs 與 discoverylistallowlisted；無公網部署默認 loopback/firewalldenyexternal。

N blueprint 原 authNscheme/.NETmajor HumanPinGate 保留：候選本機 singleoperator 優先 OSintegrated 身份 profile，跨 device/OIDC 為后續 provider。必須 specificsource/qualifiedscheme 綁定后 scaffold；不能把 USERNAMEenv 當 loggedinauth。Sessionactor 與 accountrole 權限分開、csrf/sessionexpiry/revocation、review/restore/live 等 highriskstep-up 按 policy。

Service 生命周期 INSTALLED_STOPPED→CONFIG_VALIDATED→SCHEMA_COMPATIBLE→READ_ONLY_HEALTHY→ADMISSION_PENDING→RUNNING；operationalrestart/restore→RECOVERY_HOLD。Health 分 liveness/readiness/tradingreadiness，UIgreenprocess 不授權交易；schema/policy/version/requiredsource 不可用 failclosed。Researchjobs 可在 operationalHOLD 繼續如 inputsisolated 且合法。

## Migration／Upgrade／Rollback

MigrationRevision 包含 source/targetschema、preconditions、compatibilitywindow、forwardoperation、data-backfillplan/coverage、verification、rollback/restorestrategy、risk/estimatedsize/locklimits。Schema changes firstcreateversionedcompanion/adapterexpand、readcompatible→qualifiedbackfill→consumertransition→舊 artifact 保留；closedschema 直接改須 authorizedsuccessor。Migrationfiles 生成≠實際執行。

運行前 exactDBidentity/newbackupcompleteCut/compatibletoolchain/targetverifiedscope/Humanmigrationgrant；read-onlypreflight/SQL_PREFLIGHT_RF01pendingindependentreview 不能當實際 PG 合格。破壞性 Drop/Reset/overwrite 本次 DENIED；以后需 finalconcreteapproval。Rollback 不能簡單舊 binary 配新 schema：依 compatibilitymatrix，若不 compatrestorepreviousfullset 到 freshisolatedtarget，新 epoch/currentauthority 重入。

UpgradebundlepinGit/schema/contracts/SDK/fixtures；mixedversionconsumer 拒不兼容 event。關鍵 schema 或 riskconfig 升級前 drain/holdneworders、durablejournal/完整 reconcile、profile 版本不漂；researchengine upgrade 創建 newRun，不修改原結果。Gitbranch 默認 master 既已 align，Candidate 仍不能默默 merge。

## Observability／Ops／Recovery／Security

Logs metadata 有 correlation/actor(安全 opaque)/env/accountscope/eventref/version/latency/error，無 secrets/nativePII/rawprivatecontent；debugpayload 私有分類限保。Metrics queues/lag/coverage/gap/dumpage/capture/protectionlag/headmismatch/costunknown，不輸出新進度 engine。Auditappend-only/hash/receiptproducer；rotation 不能刪不可再生 acceptancebytes。

Runbooks：serviceunavailable→liveness/requireddependency 檢查、不 autoREADY；queueoverflow→rejectnewjobs/保 journal；brokerunknown→MA08hold/query；DBspace/failure→stopwrites/noack/restorecut；artifactcorruption→MA13quarantine；pubunknown→MA12reconcile；suspectedsecretleak→isolate/revoke/rotateexactprovider，由 HumanSecurity 授權、不聊天印 credentials；新磁盤 provider 發現→驗證 VolumeIdentity/rootACL，不能自動遷移 existingdata。

Leastprivilege roles：BFFcallusecases、researchreadonlysnapshots/privatejobwrite、operationalwriterexactaccountenv、backupreadsource/writeA/B、restorerisolatedonly、GitPublisherexplicitgrant；禁止所有共享 admincredential。Reparse/symlink/UNC/device/networkproviders 分別 qualified、auth/provenance 與 scopeallowlist；backupkeys 獨立 offlineescrow。B 盤在線 host 風險仍需 futureoffline/異地 mitigation。

## API／UI／Events／Dependencies

API `/api/v2/config-candidates`、`/health`、`/recovery-status`、`/backup-catalog`(redactedread)、`/operation-receipts`；本輪無 restore/startbackup/executeMigrationAPI 自動開啟。UISettings/Operations 顯示 schema/toolchainprofiles、secretavailability、hold/reentryreasons，只有 exactauthorizedaction 才出現可用 command。EventsConfigRevisionValidated、DeploymentCompatibilityChecked、ServiceHealthChanged、RecoveryEpochEstablished，不能健康事件自動 grant。

## Examples／Acceptance／Test Strategy／Handoff

正：DBschema 不符 service 只 read/HOLD；升級 profile 重新 qualified；restore 到 newisolatedtarget 后 read-onlyreconcile。反：系統重啟保舊 dispatchlease、Gitclone 就 productionReady、root 相同不同 diskidentity 繼續 backup、downgradebinary 默讀 newfields、使用真實 DB 做 RestoreDrill。

驗收：可從 Gitmanifest 重建 compatibleprogram/schema/registry、private 缺失有狀態、env/storage/credentials 隔離、configuration/refversionexact、drain/upgrade/rollback 路徑可操作、allhighriskeffectsdefaultdeny。Tests：install/configschemadryvalidation、mixedversions、missingextensions/roles/secretavailability、port/networkisolation、processcrash/queueoverflow、migrationexpand/backfillcoverage/rollbackisolated、volume/reparse/restoretargetnegatives。actualinstall/SQL/broker/restore 另授權 qualification，本輪未運行。

WORK 單位：deploymentmanifest/toolchainpin、config/Authprofileadapter、servicehealth/envseparation、migrationplan/compatibilitychecker、observability/runbooks、install/rebuildqualificationfixtures；新 runtime 版本依原 HumanPinGate 集中決定，不每個字段都問 Owner。Knownlimits：actualdisk 容量/DB/versionSDK/identityprovider 資格與具體 productionrisklimits 待對應 Gate，不阻新章節 sourcechecked 設計。


## RCG04 candidate.4 mandatory consumer closure

[TRADING_CAPITAL_UI_ADDENDUM.md](TRADING_CAPITAL_UI_ADDENDUM.md)與MODEL/TYPE/API/EVENT同版為本章不可省略契約；external EconomicOrigin、全帳戶budget preview/confirm、PAPER SimulationSession、MarketBar DTO、servercold-reentry/error/cursor/stream及consumer映射隨exactsubject一起審核。原accepted語義不變，Runtime NOT_RUN。


## Candidate.5 有界修正承接

正文Capture成功、SQL Index、A/B Protection各自獨立；health/restore透過既有domain結果/consumer，Restore保持Recovery Hold不復活舊權限。

唯一詳細契約：`BODY_CAPTURE_READBACK_CONTRACTS.md`。原已接受範圍與尚未完成qualification保留。
