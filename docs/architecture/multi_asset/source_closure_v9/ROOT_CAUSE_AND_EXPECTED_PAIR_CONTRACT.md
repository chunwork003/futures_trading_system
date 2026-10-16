# Source Closure／Companion Complete Pairing：有界契約 v9

Subject：`MA-ARCH-REVIEW-v9-SOURCE-CLOSURE-PAIR01`。本文件是原 Architecture Owner 的單一有界修正候選，非正式 Architecture Adoption、P00 Closure 或施工授權。

## 問題、來源與責任

承接最新 v8 固定審核的 `SPECIAL01-OPS-CLOSURE-01` 與 `SCHEMA-SPECIAL01-CONSUMER-PAIR-01`。原 grammar／216 effective Schema、9 protected originals、交易／資本／PAPER／Registry 與原 R01/R03/R04/R05/R07 exact scope 均不重新設計。

原問題是只驗供應清單中的項目，沒有從 request／response／binding 的來源契約推導完整必需集合；單元 helper 又把 partial metadata 誤報為完整 source inputs bound。本次沿用既有 WORK versioned companion 邊界，不新增 Registry Owner、Compiler、Controller、Progress 或 Acceptance Engine。

## Expected 與 Actual 分離

`expected_contract.py` 只讀固定 case、source/body catalog、typed binding、原 producer/consumer map、v8 Schema compatibility 及明示 closure。不得讀取 Actual Resolver 成功輸出或舊 operation 的 resolution_ids 來決定必要需求。

同一 operation／case／完整五欄 source_ref／schema_ref 是一條 logical pair；相同來源的多份固定宣告合併為 provenance aliases，不重複計數。不同內容或 revision 不可當作同一別名。必要邊包含 case request/response/business body refs、catalog.contract_ref→source_ref、source→schema、binding.subject_ref→source_bindings 與明示 body closure。共享 read-cut 只固定其自身身份與schema，不藉 membership 選取整份 archive。

`EXPECTED_PAIR_POLICY.v9.json` 固定必需 input roles 與 companion identity 規則。Expected Pair 包含來源、版本、body/hash、Schema/dialect、相容方法、producer/consumer、Unit/fixture、成功與拒絕語義；它是既有權威資料的資格查詢投影，不是另一套全局 Registry。

Actual inventory 是待解析的具體 source bindings。只有實讀 source/schema/body/binding/capture 的固定 bytes，完成標準或 exact compatibility 驗證後，該 pair 才能進入 `ACTUAL_VALID_RESOLVED_PAIRS`。總數相等不充分，必須逐項相等；原36缺漏是必要回歸，不是完整需求的上限。

## 身份、版本與 Hash

Pair／operation／Unit 永久身份與修訂分開。207 successor／9 adapter 及原 source refs 不改名、不重發；新 companion 使用 v9 revision，原 v8 全部 bytes 保留。來源 snapshot version 與歷史 Schema origin subject 分開，不能由目錄或 hash-domain 猜版本。

原始 bytes SHA256、canonical object readback hash、源 ContractRef hash-domain 各自有明確責任。新 Pair companion identity 由 policy 的固定 namespace＋pair_id 推導；內容由外部 Actual catalog/head pin 固定，沒有自引用 Hash。順序為原來源→Policy/Expected→Actual→operation companions/index→Unit companions/index→外部信任 Head→全量 Bundle→外部 Envelope。

## 正例、反例與資格界線

固定43個正向 source worlds；逐項檢查缺件、錯版本／hash、producer/consumer錯配、重複、歧義、額外pair、同revision不同內容與不可讀正文。STANDARD Schema 先 metaschema 再 instance；216項 compatibility 沿用固定v8 adapter，無降級、無靜默補值或略過。二進位來源僅base64呈現供原schema驗證，raw hash仍綁原bytes，不執行Python Inbox內容。

成功只回 `SOURCE_INPUTS_VERIFIED_NOT_ELIGIBLE`。不能推導 SQL Indexed、A/B Protected、Actual Implementation Evidence、Dependency Qualification、Runtime、Release 或 Acceptance。R02/R06/R08、C3→C5→C6、P00 Stream Closure及 WORK/CODEX Execution Authority 均依原 Gate。

## 既有 Compiler／Context Consumer 的採納路由

本候選的 source-input 查核入口由外部 Exact Subject 的 `authority_head` 固定，再依 Head 取得 v9 operation／Unit companion，不得從舊 MASTER_INDEX 的歷史連結自行選最新檔。既有 WORK Compiler／Context adapter 若日後合法採納本 subject，必須傳入該 exact head pin、subject 與 unit_id，使用 `verify_effective_unit_inputs` 完整讀回並保留 source observation；不得只呼叫 v8 metadata-only helper，就宣稱本 subject 的來源已充分。這是既有 Compiler 的版本化輸入 adapter 契約，不是新的 Compiler 或派工實作。

原 v8 helper、索引與章節保持原始 bytes，僅供其固定歷史 subject 的重播及證據追溯；它們不能替代 v9 required-pair closure。若 caller 只有舊 Companion、缺少 v9 外部 Head、對不上版本或無法取得必要正文，應 HOLD／明示拒絕，不自動選擇 predecessor 或發放 Eligibility。正式採納前不得將此候選路由寫回正式 WORK current authority。

