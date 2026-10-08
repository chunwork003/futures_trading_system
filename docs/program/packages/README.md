# P01 / P02 planning candidates

These JSON files are concrete authoring inputs, not ACTIVE work orders. Their scope lists describe proposed future writes; P00 is not modifying those product files. Source baseline remains accepted master `9b5ab5fdd98744a7db45ec9f14b64ef1f324920f`; planning/tool snapshot is a separate later commit. No self-referential commit hash is stored in its own artifact.

P01: reproducible immutable dataset import, manifest and quality boundaries. Exact proposed modules/tests are listed. Quality policy schema and correction precedence still need final design; no runtime work before that gate closes.

P02: cross-language application/React contract slice. Test-host fixtures prove browser→BFF→Python boundaries; ordinary startup must never expose a successful fake research job. Durable research comes from P03, real dataset-backed outcomes from P04. This slice cannot credit V1 release journeys merely because its fixture workflow passes. Dependency/build pins and precise test-host identity wiring remain design gates.

Weights are provisional decomposition units for these candidate outcomes, not accepted product progress. P00 acceptance, exact grants and a stable V1 ledger are still required. `parent_wave_grant=null` is deliberate; no grant/evidence hash is invented.

## Snapshot-safe compilation

1. Verify master/source drift; snapshot the candidate tools/specs on this branch.
2. Resolve context with package ID P01/P02, changed_paths exactly matching its proposed scope, and the planning snapshot SHA.
3. Run `p00_compile.py --root <repo> --package <candidate.json> --context <manifest.json>`.
4. Compiler compares executing tool source to snapshot (only CRLF transport normalization), rehydrates context from Git, verifies registered JSON package values, checks input schema JSON pointers and preserves source baseline separately.
5. A planning/review handoff can use `handoff.schema.v1.json`; it cannot target CODEX execution or assert authority. Do not replace CURRENT_CODEX or existing lifecycle evidence.

Public semantic gaps, missing predecessor acceptance and over-budget context produce PACKAGE_NOT_READY. Input schema existence does not prove complete public semantics. Hashes do not certify that a process was trusted or independently reviewed; source-match evidence is never labeled Reviewer PASS.

Latest operational result/handoff remains the accepted current pointers resolved from repository authority. The candidate handoff format does not silently replace the accepted intake format. Full latest-delta aggregation and reviewed-tool acceptance adapter remain R02 work.

## 實際編譯檢查點

`compilation/` 保存 planning snapshot `f04484cb3983a78f885a89e3e1c74f25a0289b71` 的 P01/P02 context、compiler output 與 planning-only handoff。兩包皆 `PACKAGE_NOT_READY`；不得將檔案存在解讀為可執行。Artifact SHA256 是 Git 儲存的 UTF-8 LF bytes；Windows checkout 的換行轉換不應用來判定歷史 artifact 損壞。

這是固定 snapshot 的歷史結果；之後設計修訂須產生新的 compilation evidence，不得覆寫成當時已完成。新的 master 或 accepted result 應先 re-entry，再決定是否重編譯。
