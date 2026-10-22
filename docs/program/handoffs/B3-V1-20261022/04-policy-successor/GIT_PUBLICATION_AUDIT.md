# Git／本機交付同步稽核

核對範圍：2026-10-22 的 GitHub 19 個分支清單與各自完整、未截斷的 HEAD tree。原始 witness：REMOTE_ALL_BRANCH_TREES.json；逐檔 raw SHA256／Git blob SHA1／所有命中分支見 GIT_PUBLICATION_AUDIT.json。這是現在可達 HEAD tree 的精確原件比對，不代表歷史 commit、ZIP 或其他 derived carrier 絕對不存在。

| 來源 | 實際結果 |
|---|---|
| GitHub default/master | master；9b5ab5fdd98744a7db45ec9f14b64ef1f324920f |
| 已發表 B3 v3 | 9643bfc93a1631154be877536a1c91fc58df84be |
| B3/NAV topic HEAD | e287f6ac0744875e8d4bca103a6b73b4cf53416d |
| UI design branch | c44f75976affc3f7905a6ab407da099680d9d930；對 topic 有 68 blob 差異；僅候選，不取得B3接受權 |
| main | 0cb0283b8c5f795f8da1672575cbb674945db73a；遷移未執行 |
| remote P00 | d2bd7e9f24d339894b9f559030d1f78b1c78dca7 |
| local checkout | architecture/p00-v1-baseline；2634717b1443eb95fa0fde4d5d987347ef2160e8；既有 dirty/untracked 保留 |

本次未 fetch、checkout、建 branch、更新 ref/index、commit、push、merge。Connector 的 admin/push capability 不是本輪授權。

| 本機交付組 | 件數 | 任一當前遠端 HEAD tree 有相同 raw blob | 未有相同 raw blob |
|---|---:|---:|---:|
| 六份原 MVP 交接 | 6 | 0 | 6 |
| 預編完整包 | 119 | 0 | 119 |
| 最新政策審查包 | 10 | 0 | 10 |
| Architecture／Guide／baseline／雙採納／U01接受抽查六件 | 6 | 4 | 2 |
| 已閉合 B-TRACE 補件 | 1 | 0 | 1 |

沒有重建或推翻已發表 v3。GitHub 已有可讀 Architecture／Guide／12 Package 工程規格和可逆 Canonical transport，但新交接119、578 consumer補件及U01接受等本機Delta，不能假裝都已在master或topic。四份採納來源精確blob命中也不代表其他收據已發布。

## 最新閱讀入口與歷史文字

已直接取回 topic 上 SINGLE_CANONICAL_PRECODE_HANDOFF_INDEX.md（Git blob 49950d085ef9d4b006028413ea1e737bb950b874）。其正文仍說三檔尚未發布、全部B3尚無施工授權；這是原固定歷史文字，不能覆寫為目前狀態。本次只在新 dated supplement 分類，不修改歷史 bytes。

原 H/HANDOFF_STATUS.json 的 current_authority_entry 以及部分提案 locator 含損壞 Unicode 根目錄。保留原 bytes；新的導航只使用本機實際 Repository root＋同一 suffix＋事先固定 raw hash 的具名 root mapping，不依 basename 猜最新版。141 個原 source pin 均按 exact Hash 讀回。這是導航相容處置，非 Source/Schema語義修正。

## 最小獨立文件發布方案（未授權）

建議從 e287f6ac0744875e8d4bca103a6b73b4cf53416d 另提
codex/b3-v1-precompiled-policy-handoff-successor-01。
不在本輪建立分支，也不暗加原已消耗 v3/NAV Grant。

先以新的公開 dated index 固定：已接受baseline、BTRACE補件、96 specs/index、MVP57/184/11、policy候選／新review、U01接受狀態及原件/derived差異；對可逆Canonical的既有public定位直接引用，避免重新搬大型原件。

正式發布前仍必須另行固定 exact public file allowlist／base／raw hashes／readable targets／Canonical mapping、完成公開隱私與secret scan、取得新精確Git Grant。不得把本機完整取證目錄、Operator/Host trace、私密原文或本稽核的個人路徑清單自動公開。新候選尚待審／採納的文字必須保持CANDIDATE標籤。

U01 accepted產品、原生控制面與Current整合不是這個文件分支可暗含的效果；如需發布，另外提出最小精確source integration scope。main/master/P00歷史整合也不在此範圍。

