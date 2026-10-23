# D36 待修項目及不應宣稱的完成狀態

| 門檻 | 現況 | 下一步 |
|---|---|---|
| 四層穩定 DTO/ID 與修訂語義 | 討論定義、原型 mock | 與既有 MA10/MA11、95 API / 19 UI / 96 Unit 核對 |
| DataFlow Schema/Table/Join 與 SQL/Function | D36 模擬／候選 | 實際後端 API、授權與 SQL sandbox 查驗 |
| INFO NxM／分格百分比／顯示型態 | 原型候選 | 模組化 React 編輯器、契約測試、障礙／尺寸測試 |
| MOD／Workspace 真正新增、替換、拖曳 | 原型多輪修正 | Idempotent persisted layout、前後端契約，回歸與取消還原 |
| 相同 Renderer 預覽 | 尚缺跨容器嚴格視覺等價 | 針對同一 fixture 做縮放與輸出一致性測試 |
| 色板 5 色／連動／可讀性／儲存 | D36 QA 有界通過 | Owner 人工驗收、完整鍵盤／色彩可讀性驗收 |
| Git 備份 | 遠端已知的舊原型，有 D36 尚未確認 | 以隔離設計分支 commit/push，保留 SHA256 |
| 正式 React／ASP.NET 實作 | 在既有 Repo 主要為設計契約 | 施工授權後依 accepted Unit 和 BFF boundary 實作 |

目前不得把 UI mock 及 QA PASS 當成 runtime authorization、PostgreSQL query success 或實際交易驗證。
