# R06-SOURCE-01 negative binding 與 aggregate context successor 候選

本輪僅保存精確提案；resolver／policy／compiler 均未套用或 migration，非可執行 package。Input `52fdbe074e27004e2e4f1dbb2615920ef93e47e5`；master `9b5ab5fdd98744a7db45ec9f14b64ef1f324920f`。Proposal canonical SHA256 `563c801267b78abd0a0c5fc47f7fd505f82f85c3ada4b84d523bd90ea9bc89cd`。完整 35 個 raw Git refs、13 條 denied、7 條 invariant、兩包量測與反例在同名 JSON；舊 R01/R05/R06 成果沿用原 subject，不重算接受狀態。

## 問題與保全

原 resolver 只迭代 manifest.policies，漏掉頂層 active negative_assertions 的 mandatory 與 operational baseline drift。原 negative source 1,496 bytes 與 hash 完全保留，不為縮小 context 刪除 denied、安全契約或未分類 prose fallback。Positive API/source closure、protected scope、最新 result/intake dependencies、task/session/epoch claim 同樣保留；source shape/hash 不能證明閱讀、語意完整或 producer trust。

## 精確候選與替代

推薦 existing resolver owner 三個 zero-context hunks：要求 active negative binding，將該 binding 併入既有 hash/path/mandatory loop，並併入 baseline blob drift 集合。Patch `d1125418eabbfb719245ccb6cd9a395d730d688c2a55e4cae161c148a3426d3f`；before `80788fd834e1d4dac6bd517475c211f1b1403e181f0ee5050565d06701fff8a3`；after `97cb315a24522ffc71bc099493d1cc2d4bad79bcb3e2e3008bc27f2f8b64cacd`；owner 增加 285 bytes。硬加 policy required 靜態 path 不能單獨修復 hash／future binding／baseline drift，不推薦作唯一修訂。

`git apply --check --unidiff-zero docs/program/decisions/R06-SOURCE-01.resolver-candidate.patch` 僅檢查。唯讀 reproduce.py 從 input raw blobs 重建 exact patch，memory overlay 推演 path-set 與六項 missing／inactive／hash／unsafe path／baseline drift／stale collision 反例。Overlay 沒有 Git commit，未存為 context、reading receipt 或 producer evidence；這些反例不代表 backend/model qualification。

## Context 門檻與必要決策

| 包 | 原 mandatory bytes | 現有 selective pack bytes | 假設套用候選後 mandatory bytes |
|---|---:|---:|---:|
| P01 | 924002 | 333729 | 925783 |
| P02 | 875327 | 429913 | 877108 |

門檻仍為 original total mandatory source 131,072 bytes，全部 NOT_PASSED。兩份 CURRENT 原始 source 合計 148,689 bytes，單獨超標 17,617；即使診斷上移除全部兩份 OpenAPI 420,965 bytes，P01/P02 仍為 503,037／454,362 bytes。本輪沒有實際移除 source。加入 negative＋resolver delta 反而增加必要 context 1,781 bytes。

| 候選 | 下一份精確證據 | 目前狀態 |
|---|---|---|
| CTX01 lossless／selection | 既有 dedup、ref closure、量測 | 原 gate 不會因 pack 較小而通過，pack 也超標 |
| CTX02 compact current successor | 全部 current／history／negative preservation mapping、consumer compatibility、exact migration diff | 待獨立審查與 exact operational grant；不修改 CURRENT |
| CTX03 obligation closure carrier | prose fallback／API security errors refs／最新 intake cut、語意 omission 與實際 model golden | NOT_QUALIFIED，不把穩定 ID 等同完整語意 |
| CTX04 explicit aggregate successor | 新 aggregate target／continuity、成本 capacity／model golden、exact contract/compiler diff | 尚未選定或授權；不悄悄改為分批 128KiB |

## 風險、必要審查與建議

Owner patch 本身尚非完整 execution package：既有 reading tests／eval report 預期 missing-negative，synthetic manifests 也需要 exact fixture compatibility successor。不得只套用 patch 後聲稱所有測試會通過。先準備 exact tests／fixtures 與 consumer migration 範圍候選，獨立 reviewer 驗證 missing/inactive fail-closed 與 source semantics，再取得必要 migration 授權。原 gate／P01-r5／P02-r2／舊 report 不改寫成 PASS。

原七類 intake UNKNOWN 與兩類 source-projection NONE 保留；global bootstrap universe 未完備，reader producer 未 qualified，STOP/CAS/backend／actual model golden 未執行。SOURCE02 CSV exact A/B 選擇仍待人類決策。P00 acceptance、exact P01/P02 grant、registry bootstrap／pointer integration、controller activation 均未授權。

本輪狀態 LOCAL_COMMITTED candidate／REMOTE current turn NOT_PUBLISHED／REVIEW_PENDING packet only／P00 NOT_ACCEPTED／product NOT_AUTHORIZED。Publication 必須以最終新 payload SHA 與 manifest digest 單獨核准，heartbeat 不構成核准。

## References／可重現性

同名 proposal.v1.json 的 source_refs 固定 input/master raw blobs；validation.v1.json 保存 exact reproduction projection。執行 `python -B docs/program/decisions/R06-SOURCE-01.reproduce.py` 只輸出 JSON，重建結果可與 validation.reconstruction 比較。Git patch check 僅檢查，不套用。原 mapping、spec-evaluation 與 bootstrap refs 的 qualification 保持原狀。
