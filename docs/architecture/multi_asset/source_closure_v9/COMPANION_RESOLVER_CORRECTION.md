# 既有 WORK Companion Source Boundary：v9

唯一信任入口是呼叫端從固定 Review Subject 取得的 exact head raw pin；不得自行尋找 latest。Head固定 Expected Spec、Actual catalog、operation／Unit index、base plans、API/UI及producer/consumer來源。Index固定每個companion的entity/revision/raw hash，傳入物件只能與已登錄bytes相同，不能自行刪選應驗操作。

純來源 API：

- `verify_operation(root, expected_head_pin, expected_subject, operation_id)`。
- `verify_effective_unit_inputs(root, expected_head_pin, expected_subject, unit_id, supplied_companion=None)`。
- `verify_all_inputs(root, expected_head_pin, expected_subject)`。

全部參數均採實際 Python 的 keyword-only 介面。單一驗證觀測內可共用固定bytes快取；負例改檔後必須建立新觀測。finish重新讀取全部 observed pins 檢查漂移；這不等於Filesystem、SQL或Git跨系統原子性資格。

Expected Required Pairs與Actual供應集合先比身份、版本、完整契約值，之後逐項解析；只有真讀回且通過標準/具名適配、producer/consumer、body/binding/capture閉包，才計為Actual Valid Resolved。成功報告列 `MISSING_PAIRS`、`INVALID_PAIRS`、`UNEXPECTED_PAIRS`、`VERSION_MISMATCHES`、`AMBIGUOUS_RESOLUTIONS`、`DUPLICATE_OR_CONFLICTING_PAIRS`、`UNREADABLE_BODIES`；任何錯誤fail-closed，錯誤碼與反例證據分開保存。

Unit固定原 unit／feature／base-plan revision、dependencies、mandatory inputs與必需operation/pair集合；保留讀取原109設計companion的bytes pins。Expected Test是規格，作者source-only probe是作者證據，Independent Review與後續Implementation Evidence另由原Owner/Intake處理。不得因模型切換、來源充分性或Reviewer Design Verdict自動取得施工權。

本修正不實作正式Work Order Compiler，不執行SQL、Broker、PAPER、Restore、Controller、Git Publication或產品Coding。
