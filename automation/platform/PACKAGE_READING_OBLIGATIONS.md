# R06 — 套件閱讀義務與分階段載入

狀態：CANDIDATE / REVIEW REQUIRED；不修改原 mandatory context，也未降低 compiler byte gate。

## 固定規則

所有階段先取得 exact master / planning SHA、CURRENT、AGENTS、manifest/active policies、package scope、latest result/delta/STOP 與變更影響。不可把上述義務改成作者摘要取代原始證據。選取 API 投影仍依完整來源 hash 核對；跨版本不得拼接 context。

文件移至按需載入必須同時具備：明確 responsibility、觸發條件、反例、相依來源及 reviewer 決定；不得僅因檔案很大而省略。未知相關性時讀完整文件。契約間有衝突即停在設計決策，不交由低階 executor 猜測。

## P01 義務

| 工作階段 | 完整載入來源 | 必須解決的問題 |
|---|---|---|
| Scope / ownership | V1_BASELINE、V1_CONTRACTS、P01 candidate | 資料版本與 canonical observation 不混同；檔案 publish 不冒充 PG operation success |
| Import implementation | V1_DATASET_QUALITY、V1_DATASET_IDENTITY_IO、dataset fixtures、選取的 API schema closure | CSV/UTC/Decimal、identity frames、mapping/calendar coverage、衝突及修正版、receipt lineage |
| Integration boundary | V1_API_ARCHITECTURE、V1_STATE_MACHINES、V1_GENESIS_AUTH_CONTRACT | upload/command/cancel 邊界與非 owner 範圍；不得順手實作 research worker 或 account genesis |
| Review | 上述所有受影響來源、exact diff、tests、adverse evidence | 保留 scope 與規格完整性；不能僅讀低階執行者的摘要 |

P01 目前不可直接省略整份 API/state-machine 文件：其中包含 import publication、cancel 和跨 owner 限制。若要拆成精簡 section，需先將這些義務標記為穩定 IDs 並驗證所有反向引用；本輪不以標題相似度自動切掉文字。

## P02 義務

| 工作階段 | 完整載入來源 | 必須解決的問題 |
|---|---|---|
| Boundary / security | V1_BASELINE、V1_CONTRACTS、V1_API_ARCHITECTURE、V1_GENESIS_AUTH_CONTRACT | BFF/Python authority、login/CSRF/service identity、LIVE server deny、未知狀態不可默認成功 |
| Build / host | V1_APPLICATION_BUILD_TESTHOST、application_build_profile、P02 candidate | exact lock resolution、test composition isolation、production artifact exclusion |
| DTO / UI | Python/BFF 所有 endpoints 與 closure、V1_STATE_MACHINES | async operations、錯誤/timeout/idempotency、非權威 UI、沒有 durable provider 時503 |
| Review | 所有受影響契約、跨平台測試、browser trace、artifact isolation | 測試用 provider 不得滲入一般 startup；不能只驗 JSON 形狀 |

## Byte target 的正確處理

現有 128 KiB 是完整必讀包 target；不能偷偷改成每批128 KiB 然後聲稱通過原 gate。若未來改成分階段 context sessions，必須另定 read receipt、source/scope hash、階段進出摘要及遺漏反例，並由 reviewer 核准 compiler migration。現階段減少的是閱讀重複，不是免除義務。

## Review 後才能變更的項目

允許 exact byte去重、明示歷史引用、已列 root 的 schema closure。尚不允許：用新摘要替換安全規則、跳過原始非 API 文件、移除既有 accepted policy、以 NONE 填補未追蹤的 pending 工作、縮減 reviewer adverse evidence。此表是載入計畫，不是已完成的 context gate qualification。
