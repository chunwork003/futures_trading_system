# P00 跨流程阻塞診斷與 bounded successor 候選

本輪完成 root-cause 與可執行的離線 stage probe；沒有接受、policy adoption、push 或產品施工。正式 P00 仍 **0/8**，原 aggregate 128KiB gate 仍 **FAIL**。完整十項交付、每個問題的 source pins／反例／修正策略、七個精確 Work Packages，集中在 [decision bundle](P00-bottleneck-resolution.decision.v1.json)，量測與驗證在 [evidence](P00-bottleneck-resolution.evidence.v1.json)。這兩份候選不加入 mandatory context。

根因是把「完整證據保留」「每次 invocation 的必要輸入」「設計驗收」「工具與後續 backend 資格」混成一條結案 gate，加上 focused review 長期沒有 dispatch。提高模型能力或持續增加同類文件，無法改變這些條件。

| 問題 | 判定 | Fresh source／反例 | 最小處置 |
|---|---|---|---|
| RC01 | Context Representation Error | resolver:126–171；兩份完整 OpenAPI 420,965 bytes、CURRENT 148,689 bytes 同時累加 | retained source 與 stage obligation closure 分離 |
| RC02 | Incorrect Gate Dependency | compiler:52–53 只驗原 mandatory；packer metrics 不作 gate input | 原 gate 保留，另審 V2 successor 與 exact migration |
| RC03 | Governance Overhead／Missing Independent Review | p00_status review_readiness 的32／47／63／73／83 refs皆待 dispatch | 固定原 subjects，focused review各自設計，不再擴大一包 |
| RC04 | Incorrect Gate Dependency | R05/R07實測資格、RQ03/A2與P00設計closure混列；intake contract:39明列backend在後續 | 四個證據軸分開：design、tool、execution、promotion；這是候選依賴衝突，未證明accepted engine已有runtime cycle |
| RC05 | Architecture Design Error | 22檔scope外仍要求未知全部歷史，補8檔仍不能證明closed universe | Owner凍結review universe及exceptions；不改分母／權重 |
| RC06 | Missing Implementation／Review | active top-level negative_assertions不在policies loop；existing五檔fix/513PASS待審 | 審既有SOURCE01後exact migration，無失效不重跑 |
| RC07 | Context Representation Error | metadata commit也改planning SHA／context hash；caller session不等於trusted retention | semantic ID／value version／carrier SHA分離，trusted epoch才可重用 |
| RC08 | Architecture Design Error | API:53九欄無BOM，CSV_V1:21–29十欄一個檔首BOM | Owner選A／B，獨立語意審查後改契約 |
| RC09 | Governance Overhead | 舊exact approval只涵蓋75ef4207；後續兩commit不在原payload | 兩commit另批；future standing grant明定撤銷／期限 |
| RC10 | Tool/Sandbox Permission | fetch已成功，未測本輪push；repopolicy不改工具network boundary | 支援時用工具；否則另批Windows pinned publisher setup |
| RC11 | Model Capability | 固定程式算930,223 >131,072，任何模型相同 | 模型不足未證立；XHigh只用於重大決策 |
| RC13 | Governance Overhead | publication generator:67–69要求payload等於mutable HEAD，合法續作也使舊request不可重建 | 另審immutable payload/prefix verifier；後續commits明列不包含，原builder不偷換 |
| RC12 | Actual External Blocker | importer/PG/browser/model backend資格未run，來源明列後續implementation | 保留後續資格；不當作不能審P00設計的外部原因 |

## Context V2 實際原型

`scripts/p00_context_v2_probe.py` 以固定 Git snapshot、完整既有 safety sections、全部13 negative assertions／7 invariants、OpenAPI request／response／security／error及遞迴引用 closure建立 capsule。Omission oracle從來源重建，不信候選自行重算的hash。

| stage | 無effects契約審查 capsule bytes（含envelope） |
|---|---:|
| P01.CSV | 109,210 |
| P01.IDENTITY | 111,596 |
| P01.QUALITY | 115,877 |
| P02.AUTH | 118,745 |
| P02.IMPORT | 124,924 |
| P02.OPERATION | 122,272 |

原P01/P02 mandatory仍930,223／881,548，selective仍339,165／435,349。保留來源945,540／906,985 bytes；原始全量未丟棄。第一輪只拆stage仍151–179KB；混合import+operation的無effects版本仍135,815 bytes，依實際stage責任分開後降到target內。

**適用限制：六個代表性no-effects review stages；不是完整verified obligation graph、executor或publisher context。** 全部unclassified source仍待semantic review。無effects profile明列WORK kernel、CURRENT_CODEX及capacity/cost程序來源在re-entry/action stage必須完整載入；任何效果、authority/STOP/head/scope/context-loss問題都需fresh re-entry。完整control profile仍151–167KB，不能拿這個review profile冒充executor input。

actual injected bytes／token count仍NULL，真實模型閱讀、trusted epoch、registry/crash/race未qualification。Graph節點的source/value hash證明投影，不證明理解。獨立graph/safety/omission審查、Owner successor生效與specific profile qualification完成後，才可另批Resolver／Compiler migration。

重現：

```powershell
python -B scripts/p00_context_v2_probe.py --baseline 6b717d5b7b9447272e5ff35b7715ad33ad6fb026 --profile CONTRACT_REVIEW_NO_EFFECTS --output-dir .tmp/p00-bottleneck-final-capsules
python -B -m pytest tests/platform/test_p00_context_v2_probe.py -q -p no:cacheprovider
```

## Closure 與 CSV 決策

Bundle提供三段exact replacement clauses，供Owner核准P00 review universe／design-vs-backend／RQ gate boundary。既有規範不被自行改寫，R01–R08不因此PASS。R01/R03/R04/R05/R07設計已有focused review入口；R06 SOURCE01、CSV及V2分段審查；R08最後審baseline。

Accepted upstream `domain/market_observation.py` 在master與candidate為同一blob，規定exact Decimal、canonical identity/mor1及nullable content，**沒有決定CSV physical header/BOM**。Dedicated CSV文件與API都標candidate，不能按檔名自行宣告其中已接受。

推薦A（未選定）：HTTP和bytes同一十欄CSV_V1，容許一個檔首BOM。既有exact一段patch可直接供語意review；保留原upload byte hash、retry、mapping/calendar、null、atomic publication及256MiB等契約。九欄client若存在會拒絕，consumer inventory UNKNOWN。B須明定format/version、identity mapping、optional fields、timeframe、BOM、hash lineage、owner/scope、compatibility八項，不提供猜測adapter。Bundle附positive/negative fixture規格與migration impact，沒有parser測試或正式契約rewrite。

## Publication 的具體界線

Repo `chunwork003/futures_trading_system`、source/target `architecture/p00-v1-baseline`。遠端75ef4207已發布先前23commits。現在凍結另批的兩commit依序：

1. `e2fd2dd42cfaff1b766843f34f1910c310e8f03b`
2. `6b717d5b7b9447272e5ff35b7715ad33ad6fb026`

12檔：A10/M2/D0；exact manifest SHA256 `012cf99b5612e6126bcaaae55392ba49c9b49333c883cf33873a5b0b04a8b1e1`。Fresh核對675 raw commit objects／all parent edges／16 raw content blobs。全部檔案與before/after hashes在原manifest，這個request **不包含本輪新增工作**。

Standing grant候選：一次Owner明確核准，7日／累計16commits或100檔先到即止，每checkpoint最多4commits／25檔；exactrepo/ref/base/master/allowlist，protected及historical frozen evidence不可改；普通FF。WORK既有plane驗證manifest、parent-edge scope、tests、pinned secret scan、single writer、revocation/STOP及budgets，保留intent/outcome receipt和idempotent CAS。

不能把implementation single-use CONSUMED改成可重用grant。新型PUBLISH_CANDIDATE capability及protected policy/engine修改需要新的exact authority和independent review。既有engine是pure/read-only，durable publication adapter尚未實作；缺lease/coverage就STOP，不補第二套Controller。

遠端race需trusted pinned pre-push hook核對Git advertised OID／exact refs，普通push利用server old-OID檢查；不使用force-with-lease。Timeout先核對既有intent、receipt與remote，不盲重送。

Repository grant不等於Codex工具批准；[官方approval文件](https://learn.chatgpt.com/docs/agent-approvals-security)及[config reference](https://learn.chatgpt.com/docs/config-file/config-reference)明示auto_review不改sandbox。本輪没有新的push拒絕。若工具無法持續執行granted push，可由Owner另批Windows PowerShell／Task Scheduler pinned adapter，讀相同WORK grant/store，task只wake。未安裝或啟動任何task。Git guard依[pre-push介面](https://git-scm.com/docs/githooks)與[普通FF規則](https://git-scm.com/docs/git-push)設計。

下一合法工作是Owner bounded decision與focused independent review；不是繼續增加同類文件、重跑既有fixture或產品施工。決策審查後用Sol High實作；routine fixtures用Medium。模型未自行切換。


驗證：final targeted **11 passed**；full platform **507 passed**；generated contracts保持一致。驗證後僅將新增重要comment轉為繁體中文，AST完全相同；tested／final source hashes分別保存在evidence。原SOURCE01的513 fixture不重跑、不改寫。
