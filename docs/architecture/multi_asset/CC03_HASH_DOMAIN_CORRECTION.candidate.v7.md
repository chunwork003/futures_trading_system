# CC03 Hash-domain 修正契約 — candidate.7

Subject：`MA-ARCH-REVIEW-v7-CYCLE03`。此為 Architecture Owner 作者片段，待 Root 整合及新一輪獨立審查；不產生採納、P00 credit、WORK dispatch、Git publication、SQL、DDL、runtime、Controller 或 Secrets authority。

## Summary／Analysis

`V6-REGISTRY-HASHDOMAIN-01` 的共同根因是 bare canonical SHA256 witness 使用了既有 prefix domain 名稱。C2 latest-fixed consolidated final review manifest 的 raw SHA256 為 `e9e4046b8a2f73228cc70d38a9777a73093e1462b75b75ded1bf4c8d3be8f88b`（ActiveInput v2）；影響範圍包含 aggregate 1、current plan refs 96、predecessor plan witnesses 96、既有 full-body history wrappers 3,660、duplicated requirement-history metadata 32＋32。八個 graph scopes 與兩個 source snapshots 的原 prefix witness 不需要改算法。

## 明確公式與 immutable adapter

`ma-canonical-json-sha256-v1` 一律為 `SHA256(UTF8(domain) || 0x0A || canonical_json_bytes(payload))`，canonical byte 規則沿用 `LOGICAL_SCHEMA_CONTRACT.md`。不按 record kind、年代或讀取順序選公式。Current aggregate 與 current plan semantic refs 使用此 prefix 公式；aggregate null-out exclusions 僅原本三族 self-hash pointers，不排除其他內容。

新增不可變、版本固定的 `LEGACY_HASH_DOMAIN_ADAPTER.candidate.v7.json`。其 `ma-legacy-bare-canonical-json-sha256-v1` 有唯一公式 `SHA256(canonical_json_bytes(payload))`。此 domain 僅經 finite、exact-source allowlist 解讀既有 witness。原 domain 字串、原 hash、原 full body、原 scope revision、captured bytes、accepted receipt 保留原樣；adapter 不將原 legacy row 改寫成正確 prefix row。

每一 adapter binding key 必含 source subject、carrier subject、candidate-relative source path、完整 source raw SHA256、literal JSON pointer、entity ID、revision ID、原 hash／原 domain。若 source bytes、selected payload、identity、revision、hash 或 domain 任一不符，返回 `LEGACY_HASH_BINDING_MISMATCH/HOLD`。沒有 exact binding 返回 `LEGACY_HASH_BINDING_MISSING/HOLD`；不得 bare/prefix 雙算後 first-match，也不得以通用 record-kind fallback 接受未知值。Metadata-only history 仍無 full-body/typed-read qualification；六份缺失 source 與 209 predecessor parser-schema 限制保留。

Adapter 的 `current_bindings` 僅宣告有限 current locator、current identity/revision 與 exact legacy witness key；不包含 current Registry 或 EXECUTION_UNITS raw hash、current plan semantic hash。Registry/Unit consumer 以 immutable adapter raw hash作 companion pin，因此 dependency 為 adapter → unit body → current plan refs → aggregate → resolver provenance，沒有 hash 回邊。

## 新增 C2 predecessor 的界線

C3 可在新 history metadata wrapper 保存 C2 current body，但 canonical payload 必與 C2 精確 source payload 相同。C3 新建 wrapper 直接採 prefix 公式；C2 原 wrapper 全 row 與 32＋32 requirement history 全 row 不變。C3 predecessor plan witness 保存 C2 原 bare hash及domain，必由 adapter 結合 C2 Registry current planref 與 C2 EXECUTION_UNITS 原 body驗證。這是 source witness，不是新 acceptance receipt。

C2 aggregate 自身成為 immutable legacy witness：adapter `source_payload_projection` 明列 `REGISTRY_AGGREGATE_THREE_SELF_HASH_NULLS_V1`，只准使用該 source 原本精確三族 self-hash null-out。`prior_snapshot_ref`、新 C2 snapshot history 與封存 payload 內引用此原裸 digest 的位置逐筆列 exact current anchor；不修改內部 hash／domain／body。對 C2 已封存的 v4/v5 aggregate也僅在原三族規則及裸 digest可自行核對時建立 binding。較舊 source 的原 projection規格不明或不相容時保持 `UNSUPPORTED/HOLD`，不得推測 serializer或任意 omit fields。內部 archive witness沒有 exact allowlist時同樣 HOLD，archive存在不表示可qualified讀取。

## Consumer／Alternatives／Recommendation

Registry rebuild、history lookup、unit compiler／predecessor verification／reuse proof、source witness validator 必先解析 exact adapter companion；不能直接把 ambiguous legacy domain 當 prefix 也不能忽略 adapter。Current current-planrefs 使用 prefix，不需 adapter。Source resolver 的 selected/raw source hashes保持各自 domain；Registry aggregate raw hash只能是外部 provenance，不反向寫入 frozen row payload或adapter。

Candidate adapter所攜帶的 C2 raw carrier及其封存來源，只供本輪 review evidence／source design使用，不自動加入 Public Git正式 export allowlist。正式 Git-only baseline必須可由獲准的 closed current payload重建 current IDs、codes、relations及明確 hash-domain policy；不能把私人候選 carrier當作恢復 current identity的必要公開來源。正式 current projection與保留歷史驗證分開處理：缺原 private source時，舊 legacy witness仍為 `UNKNOWN/HOLD`，不重製或繼承 acceptance。

若未來採納新的 hash-domain/source export，必須由具權限的 Owner建立另行 versioned projection，只移入 allowlisted formal closed payload與 exact source proof。此 projection仍保留永久 IDs／原 revisions及既有責任，不把 private candidate整包轉成 Public Git強制歷史。此作者片段不授權 formal adoption、Public Git export、accepted-source修改、Migration或Controller。

簡單改 global rule 會破壞已正確使用 prefix 的十個 controls；覆寫歷史 hash會破壞已有 immutable revision／receipt lineage。採 finite legacy adapter＋current prefix witness 的修正，保留來源與責任界線。

## Root 精確整合順序

1. 固定其他 author fragments／candidate.7 契約與 final unit IDs/revisions，保留 C2 predecessor及必要原始 source bytes。
2. 執行本片段 generator 的 prepare，取得 finite adapter 與 coverage；必要 companion 加入 compiler／unit source contract。Adapter 不讀其 consumer 的 raw hash，所以 companion pin可加入 Unit 而不形成循環。
3. 完成 Unit final binding，將 exact final unit bodies同步至 Registry `entity_revision_data.execution_unit_plans`；96 current plan refs以 prefix 重算，舊前驅 witness保持原樣且有 exact adapter。
4. 完成 Registry current relations／history predecessor metadata；再次 prepare/apply，本片段逐筆保留 C2 old wrappers／32＋32 requirement history，新增 C2 wrapper以 prefix 重算。
5. Registry pin adapter raw hash；null-out三族 self-hash後 prefix重算 aggregate，更新 snapshot與所有 governing snapshot source_hash。
6. 刷新 resolver external provenance、外部 operation-world binding、source/author manifests；它們不得回流 adapter或aggregate。最終再次執行 verification並freeze source envelope。

`finalize_hash_domains.py --apply` 只能由 Root 在指定 C3 candidate 執行。作者本片段只產生 prepare output／source-only checks；不直接修改 C3 candidate。

## Risks／驗證／References

必要 source-only反例：裸 hash不得被 prefix verifier接受；相同原 domain只有 exact finite adapter可讀；未知 binding/不同 bytes/pointer/ID/revision/hash拒絕；adapter不能使缺失 body／schema／receipt成立；current aggregate、96 refs、新 wrappers prefix計算一致；既有 wrapper與32＋32 history逐欄位不變。通過這些作者檢查不是 Independent PASS、runtime或正式restore conformance。

References：C2 fixed `fresh-review/registry/{RESULT.json,REPORT.md,HASH_DOMAIN_IMPACT_CLOSURE.json,REVIEW_OUTPUT_MANIFEST.json}`；C2 source `LOGICAL_SCHEMA_CONTRACT.md:9`、`GIT_REGISTRY_REBUILD.candidate.v1.json`、`EXECUTION_UNITS.json`、`REQUIREMENT_REGISTRY.json`。
