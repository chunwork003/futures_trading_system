# R06 — Current intake registry / receipt 契約候選

本文件凍結供審查的設計，未建立 accepted registry、未補造 lifecycle evidence。未來實作歸屬 A2 result/review orchestration；A3 controller 只消費提案，不能自行接受 registry 或工作結果。既有 master 不因本文件而取得新欄位權威。

## 唯一 ownership 與資料模型

WORK control-plane store 是 registry 的唯一 writer；executor/reviewer/integrator 各自 append 原始結果，由 WORK intake 驗證後更新 registry。各 producer 自己的檔案不直接覆寫 global current。trading/research runtime 不參與 development registry。

每個 immutable snapshot 至少包含：schema_version、program_id/revision、registry_revision（正整數遞增）、previous_snapshot_hash、authoritative_master、program_definition_blob、producer_heads、coverage、active_execution、writer、STOP、pending_results、pending_reviews、pending_integrations、pending_acceptances、latest_deltas、last_accepted_results、source_refs、snapshot_hash。hash 使用既有 canonical JSON bytes，不以 timestamp 排序；published snapshot 不可覆寫。

每項工作 identity 為 program/package revision/work_order/execution/result revision 的精確 tuple；不適用欄位須依 item kind 明示 null。source_refs 綁原始 Git commit/blob/hash。review additionally 綁 reviewed subject/scope、reviewer identity、verdict；integration 綁 reviewed source blobs 與 destination；acceptance 綁 review/integration/test evidence 及 exact delegation。result 不是 acceptance，PASS 不是 dispatch grant。

coverage 記錄此 snapshot 涵蓋的完整 program lane、所有已啟動 execution 與 producer heads，以及逐分類 COMPLETE/INCOMPLETE。空集合只有在對應 coverage COMPLETE、來源具權威且 consistency check PASS 時能投影 NONE。沒有 ledger head、未知 producer、未收錄 execution 或 head drift 必須 UNKNOWN。不得僅掃目錄後推斷 completeness；registry 本身須有接受過的 bootstrap/successor authority。

## Bootstrap / successor

現有來源沒有完整 global pending registry，因此初次 bootstrap 需獨立盤點：所有仍有效 execution/grants、writer disposition、未 intake results、open reviews、STOP、latest delta 及 acceptance lineage。保存逐項原始來源與例外清單，獨立 review 後，由 exact operational successor grant 啟用。任何未解來源保留 INCOMPLETE，不修寫歷史 records。

Master 改變時先驗證對 program/source 的相容性；純其他 package 變更也需有 bounded compatibility evidence，不能拿日期或祖先關係當全部等價。影響 authority、scope、reviewed subject 或 producer head 的變更使相關 proposal/receipt eligibility 失效；原始 receipt 保留。

## 原子接收與冪等

Intake transaction 輸入 expected registry revision/hash、producer head、exact result identity/payload hash。先驗 source lineage、identity、scope、producer authority，再以單一 CAS 提交 append-only intake receipt、新 snapshot 及 current pointer。失敗不發放任何新 execution；重試先查 receipt。

receipt idempotency key = `(program_id, producer_id, result_identity, result_revision)`；同 key 同 payload 回傳原 receipt；同 key 不同 payload 是衝突，不能以較新 timestamp 覆蓋。receipt 包含 source snapshot、validated input hashes、decision、new revision、causation/correlation；收到 result 與釋放 writer 必須符合既有 lifecycle gate，不能把本文當額外 release authority。

單機初始可採既有 repository-governed append/commit 模式；若後續採 DB，需要另定 transaction/backend 契約與 crash qualification。此設計不授權引入第二個與現行 accepted Git control plane 競爭的資料庫。

## Read acknowledgement 與 progression

讀取 delta/accepted baseline 後產生 **讀取 acknowledgement**，key 為 `(consumer_role, program_revision, source_item_id, exact_blob_hash)`；不改動該 item 的 PRESENT，也不假裝已 acceptance。下一次評估只跳過 exact hash 已讀且 governing snapshot 未失效的閱讀動作。換 source、consumer task context 丟失或 contract revision 改變都需重讀。

acknowledgement 不表示 reviewer 認可、結果 intake 或新 package grant。新工作 eligibility 仍需全部 pending categories 可解、無阻塞 STOP、one writer、正確未消耗 authority/dependency/capacity；本規格沒有 ALL_CLEAR 自動 dispatch 權。

## Snapshot race / resume / escalation

選擇 next action 與執行前各讀一次 registry head；revision/hash 不同就丟棄 proposal 並重新評估，不攜帶舊 writer lease。安全 STOP 可撤銷未啟動提案。unfinished execution 優先，但 resume 必須有既有 invocation/lineage；consumed-not-invoked 只能依既有 authorized first-invocation route，不製造 resume。

未知 registry coverage 只阻擋依賴它的 autonomous dispatch，**不阻擋另有明確 human authority 的 P00 設計工作**。如需更動 accepted authority model，使用一份 bounded successor decision，不每天重新要求相同授權。完整 control-loop implementation 與真實 crash/CAS 驗證屬後續 A2/A3，不把規格測試說成 production qualification。

## 必要驗收反例

1. 未列出 pending review → UNKNOWN；不能選新工作。
2. 同 key 相異 payload → CONFLICT；receipt/history 不被覆寫。
3. snapshot read 後收到 STOP → 舊 proposal 作廢。
4. read acknowledgement 只有舊 blob → 新 delta 必須重讀。
5. reviewer PASS 綁舊 subject → 新 candidate 不可 acceptance。
6. result 存在但 writer release 尚未 durable → 不 dispatch 其他 package。
7. consumed 無 invocation → 禁止 resume；不得 backfill invocation。
8. COMPLETE coverage 缺 producer head／未知 execution → 降 UNKNOWN。
9. intake 寫入中 crash → restart 以唯一 receipt/current pointer 原子結果解析，不重複消耗。
10. 只有合成 fixture／mock 測試 → 不授予 registry bootstrap 或 controller promotion。
