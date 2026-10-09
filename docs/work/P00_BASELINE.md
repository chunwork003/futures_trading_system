# P00 — V1 Architecture / Knowledge / Development Platform Baseline

Status: `IN_PROGRESS / CANDIDATE_ONLY`。本文件是本輪 Architect 工作封裝，不是 CODEX runtime authorization。

## 授權與邊界

- Repository: `chunwork003/futures_trading_system`；authoritative branch: `master`。
- Fresh source baseline: `9b5ab5fdd98744a7db45ec9f14b64ef1f324920f`。
- Working branch: `architecture/p00-v1-baseline`；不得將本分支候選狀態冒充 master 已接受狀態。
- Human request: `docs/program/P00_OWNER_REQUEST.md`，原始需求逐字保存；request hash／reconciliation 位於 `docs/program/current_truth.v1.json`。
- 直接授權：盤點、架構候選決策、Git-trackable docs／registries／schemas／templates、bounded offline validation、下一包編譯與 continuation。
- 此輪只執行一個 mainline package P00。P01/P02 runtime implementation、CODEX dispatch、broker、credentials、DB access、migration execution、LIVE、production activation 均不由本 package 授權。
- 不偽造既有 controller execution／reservation／dispatch／invocation。這是 HUMAN_REQUESTED_ARCHITECT_MATERIALIZATION，非 AUTO-IMP-003 executor。

## 必讀與唯一 owner

1. `docs/CURRENT_STATE.md` at fresh master：已接受 operational truth。
2. `docs/program/current_truth.v1.json`：固定 baseline 的 evidence index；不能反向授權。
3. `docs/program/p00_status.v1.json`：本候選的交付完成度與 continuation。
4. `docs/architecture/V1_BASELINE.md`：P00 產品架構候選。
5. `docs/architecture/V1_CONTRACTS.md`、`V1_STATE_MACHINES.md`：契約與 transition owner。
6. `docs/program/V1_PROGRAM.md`：package DAG／驗收／進度規則。
7. `automation/platform/README.md`：development platform spec／registry 導航。
8. `docs/program/HISTORICAL_REQUIREMENTS.md`：R05有界來源／明列義務、歷史接受與尚缺交付；大型 machine index只作選擇性追溯，不加入 P01/P02必讀 pack。
9. `docs/program/HISTORICAL_SEMANTIC_BRIDGE.md`：八份補充source／selected interpretations、年代差異與future non-waiver；不是第二個current authority或完整歷史closure。

10. `automation/platform/CONTEXT_READING_RECEIPTS.md`：R06 source/session claim compatibility及RQ01–RQ06；negative assertions mandatory缺口保留待審，不修改原128KiB gate。

11. `automation/platform/SOURCE_READING_OBLIGATIONS.md`：P01/P02 positive/negative/protected來源與context；CSV source02 LEVEL3待決，不更改原contracts。
12. `docs/program/publication/P00-entry-c10c657.manifest.v1.json`：凍結entry publication inventory；final核准manifest在payload freeze後另存repository外，禁止推入尚未核准範圍。

13. `docs/program/decisions/R06-SOURCE-02.md`：CSV source02 的 exact A patch／B 八項語意決策與保存證據；未選定／未套用，architecture choice 不等於實作或 publication grant。

14. `automation/platform/READING_SPEC_EVALUATION.md`：repository-bound omission/continuity 規格矩陣，synthetic claims非trusted receipt；RQ04 actual model／durable race／semantic completeness仍未qualified。

## Scope

Allowed: `docs/architecture/`、`docs/program/`、本文件、`automation/platform/`、`scripts/p00_*`、`tests/platform/`；可在既有導航增加候選 pointer。
Protected: 所有產品 Python source、既有 migrations、accepted automation engine/policies/programs/authorizations/runs/work-orders evidence、`data/`。
CURRENT／ACTIVE 的精簡與 successor integration 必須在候選自洽、preservation／resolver compatibility 通過後才進行；未完成時維持原 accepted pointers，登錄 migration plan。

## Acceptance

- Owner request 0–90 requirements 每项有 coverage／evidence／remaining，不能只用文件數結案。
- Current truth 與 candidate decision 分離；既有 GAP-08／AUTO-IMP-001/002 acceptance 不重開。
- Required domain contracts、state machines、API、deployment、release journeys 均有具體決定與反例。
- Registries 先 inventory，沒有 fixture／eval 的 Skill 不宣稱 L3+。
- Package／context schema 檢查、path／hash／DAG／weight／API ref checks 與負例通過。
- Fresh independent baseline review 是 P00 ACCEPTED 的必要 gate；作者自查不能代替。
- P01/P02 可達 COMPILED_PENDING_BASELINE_ACCEPTANCE；baseline 未 accepted 時不能標 READY_FOR_EXECUTION。

## 驗證策略

只有 P00 文件與工具的改動：targeted platform tests → full platform regression → baseline consistency checker → git diff --check → scope/protected blob verification。
產品 full regression 不因新增文檔重跑；若出現產品 source delta，立即 scope violation，不以擴測試掩蓋。
機械檢查只證明 structural consistency，不證明 trading semantics、API usability 或外部環境已驗收。

## 停止／續作

Public semantics 仍不完整：記錄精確 gap，延續 P00，不把它交給低階 executor。
重大 authority contradiction／真實資金／LIVE／不可逆 external effect：停止受影響工作。
每次結束保存 `p00_status.v1.json`；後續以 exact continuation 接續，不重做已完成 baseline inspection。

使用者指定續作措辭：原回覆內文增加「目前總進度O/O(已完成數量/總共多少須完成數量)，下一步驟預計執行OO，請回覆「繼續」，使工作繼續執行」。數字以 p00_status 的 R01～R08 完整結案項目為準；部分完成不計入 numerator，必須標示此為 P00 結案口徑，不冒充 V1 產品完成度。範圍改變時另記原因，不因 split/correction 任意變動分母。

本輪最新使用者續接格式取代上列舊回覆句式，以p00_status.v1.json為current owner：「尚有【具體未完成項目】未完成，下一輪建議使用【Sol Medium／High／XHigh】；請回覆『繼續』，使工作繼續執行。」繼續本機authoring不等於publication／P00 acceptance／product grant。
