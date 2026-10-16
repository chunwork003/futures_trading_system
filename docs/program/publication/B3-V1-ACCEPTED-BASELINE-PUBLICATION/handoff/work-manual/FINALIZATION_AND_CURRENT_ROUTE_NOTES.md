# WORK／Manual 交接固定說明

本子工作區只完成來源繫結、工程規劃、操作手冊及候選施工 Packet。原生成程式在作者草稿期間進行兩次確定性檢查；第二次只補充既有人工備援路徑及壓縮 Markdown 顯示，完整 Unit／測試／相依 JSON 未刪減。`OUTPUT_MANIFEST.json` 為該草稿結束時的清單，從本次 finalization 起保留原 bytes，不再覆寫。

最新固定交付清單為 `OUTPUT_MANIFEST.final.v1.json`，明列該前身清單及此說明。此清單是本次交接產物的封存，不是 Architecture、P00、施工、Runtime 或派工授權；不聲稱新增 Fresh Independent Review。

## 現行 route 與 B3 計畫的邊界

本輪 Human 已明示允許 B3 分析／規劃及隔離候選輸出，因此不以 AUTO-IMP-003 作所有 B3 Planning 的前置障礙。B3 十二包排序是其內部 Unit DAG 的規劃投影，不修改現行 Automation lane。

真正施工前，既有 WORK／Owner 必須將選定 B3 工作合法接納至適用的 current eligible route，固定依賴結果、Work Order、exact scope、grant、成本及 Writer 資格。若選定包與正式 NEXT／queue／selected package 不一致，只能提出具來源的 route／queue amendment 候選並依原權威決定，不得靜默略過 AUTO-IMP-003、重排隊列或挪用舊授權。

`HUMAN_DIALOGUE` 為既有 MANUAL fallback，不是新 Compiler；人工可沿用既有 Work Package Template 編製候選。這使 Controller／CODEX 不可用時仍有合法備援途徑，但不取消 exact grant、source assembly、適用 Context／Companion／Result Adapter、閉 Schema 相容性、P00 相依及單 Writer。備援 Owner receipt 的原工作範圍不會轉授 B3。

PK01 的 MA01-U01 無 Unit 上游只是 DAG 事實，目前仍非施工 READY；MA01-U04／MA15-U04 等有具名 P00／profile 條件，按 Unit 判斷，不增加全包必須先全部 P00 Closed 的新規則。Mock 場景／Oracle 可規劃，Mock Implementation 仍需具體授權。

## 驗證與未執行

123／123 項檢查只涵蓋交接資料結構、34 個 PK01～PK03 Unit 投影、96 永久身份／364 依賴保留及 103 份所讀來源的 raw bytes SHA256 保護。未執行 Compiler、C3 Qualification、C5 Review、C6 Human 決策、產品 Build／Tests、SQL、Restore、Broker、PAPER、Controller、Git／Ref 寫入或派工。

Root 將建立的 `MASTER_HANDOFF_INDEX.json` 是受控外層導航入口；此子工作區不產生該 root 文件，不因在 Prompt 指向它而宣稱已驗證其尚未固定的 bytes。整體交付前由 root 驗證該入口及其對本固定清單的引用閉包。
