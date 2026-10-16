# CC01 — Scope Revision 與歷史正文修復

本文件是 `MA-ARCH-REVIEW-v5-CYCLE01` 的候選修正，沒有正式採納或執行權限。

32 個已確認 B3 必做需求保留永久 Entity ID，取得新的 Entity Revision。新 revision 的 predecessor 指向 v3 中原始合法 payload 的 revision，並保存其完整 canonical payload、canonical SHA-256、原檔 raw hash 與 JSON pointer。Scope 的採納仍須原正式流程；不把新名稱或分期當成新的產品身份。

v4 的同-ID／同-revision／不同正文不是另一個可匯入的合法 revision。其原始bytes、聲稱revision、payload與hash完整保留為 `FIXED_REVIEW_OBSERVATION_NOT_ADMISSIBLE_ENTITY_REVISION`。不能以該觀察取代 v3 正文，不能讓兩個內容以同一 key 同時進入正規化 Registry，也不能因保存 v4 觀察就宣稱 v4 全Snapshot具有正式資格。

以下修正必須一起滿足：需求registry與Identity current head一致；B3 Slice綁新revision；所有Unit requirement bindings、當前relation endpoints、snapshot會員、crosswalk與Git Rebuild payload綁相同新revision。Legacy Alias及舊 Work Order／Evidence 仍可解至原永久身份與其精確歷史版本，不回溯重寫已接受資格。

每個同 `(entity_id, revision_id)` 的可匯入正文只容許一個canonical content hash。合法同hash重送冪等；不同hash拒絕並保留conflict receipt。MOVE／改名／分期不改永久ID；新版本只能append。v3／v4候選歷史與所有已接受Receipt保留，本修正不更新正式master/main或SQL。

新版snapshot與Unit plan／Relation revision也是successor，不原地改其predecessor。History須區分完整payload、只有identity metadata的legacy history及不可接受的歷史候選觀察；只有metadata不能冒稱已保存全部正文。缺歷史正文時明列availability，不補造接受。

客觀檢查：32筆 old/new scope、ID、revision與hash對照；prior不是self；舊正文可驗證；endpoint revision closure、跨樹／Dependency DAG、95 API／96 Unit反向引用、Git-only正式身份重建一致。Source／schema／模型檢查不代表真PostgreSQL或Restore資格。
