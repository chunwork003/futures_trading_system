# P00 Context Reading Pack 檢查點

這些是固定 Git snapshot 的候選閱讀投影，不是 current authority 或可執行 handoff。

`dbf6d41/` 對應該 commit 的 P01/P02 revision1 與 context policy；後續 P01 revision2 未包含於其中。Pack 中 request.baseline_sha 保存完整 SHA。必須依當前 revision 重新產生新目錄，不能覆寫歷史資料。

JSON schema 共用 pool；以 scripts/p00_context_pack.py 的 expand_json 可還原原始完整 JSON 值。每份來源都綁定 Git blob/hash。CURRENT 歷史分離依原始明示 marker，archive_start_line 與 archive_text_sha256 綁定完整 suffix。需要歷史／lifecycle／矛盾判讀時讀完整 source。所有 AGENTS 文字保留。

Metrics 的 pack_sha256 綁定 Git 中的 compact UTF-8 LF bytes；不是 Windows checkout 換行後 bytes。P01 740998 → 367502 bytes；P02 741858 → 368689 bytes，約減半，但仍未達 131072-byte target。這不是 token 量測，也不代表已通過獨立審查。原 compiler 必讀 gate 完全不變。


`7477e51/` 保存 P01 revision5 / P02 revision2 的 selective profile 量測、實際 packs 與結果閱讀索引核對。`*.full-reading.metrics.json` 是同 snapshot 不做 endpoint/schema selection 的比較值。Selective pack 的 JSON projection 只能還原選取內容；excluded paths/schemas 及完整來源 hash 明示保留。兩包仍超標，不能用來解除 compiler gate。`result_reading.json` 不是完整 current intake 或執行授權。

## R06 source/session audit — 9106fbb

`9106fbb/reading-smoke.json` and P01/P02.reading-audit.json bind exact design snapshot and prior WORK profiles with current unchanged package scopes.33/31 mandatory representations,0 claims; active negative_assertions1496bytes unrepresented. Original aggregate and selective carrier still over128KiB. These are source-bound structural reading plans, not fresh compilations, trusted acknowledgements, current intake or readiness. New context/source/session changes require rebuilding before use.
