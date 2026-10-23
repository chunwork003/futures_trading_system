# D1 中途決策紀錄（候選）

1. 產品正式技術方向：React + TypeScript → C# ASP.NET Core BFF → Python API/Quant Core → PostgreSQL。`D36.html` 是**只用於設計驗收**的離線原型，不是正式 React/C#。
2. 四層引用：`DataFlow.flowId` → `InfoModule.infoId + flowId` → `Module.moduleId + infoIds` → `Workspace.workspaceId + moduleIds`。DataFlow 可以被多個不同 INFO ID 共用；不能用顯示名稱當作 key。
3. DataFlow 資料分類及細項、schema / table / columns / join / query or function 定義分離。SQL 可以由表格互動選取形成候選，也可由人工填入，但只有受權後端在驗證、權限及成本限制下執行。瀏覽器端一律不執行 SQL。
4. 資訊模組修改：選既有 INFO，同名儲存先警告覆蓋；取消保留草稿並聚焦名稱；改名稱建立**新 INFO ID**，舊版留存。
5. 三種編輯器獨立。工作台編輯是選 MOD、預覽、拖曳、替換／移除；模組編輯是選 INFO、格線配置、預覽；資訊模組才配置 INFO、資料流及圖表。不要把按「＋」變成強制跳另一個頁籤。
6. 右欄候選與中央正式卡片應採**同一 Renderer**／同一引用資料；縮圖等比縮小而不更換內容。
7. 工作台／模組／資訊模組／資料流是實際常用工作流，建議正式 React 將「工作台設計」提為上方導覽功能候選；配色、啟動、快捷設定留在全域設定。須先核對既有正式 UI 身份。
8. D36 配色視覺比例：桌面左右 5%／30%／10%／50%／5%，色輪與色票下緣一致，七個 icon 對齊色輪；下排第 1、4、5 色票各自對應控制組。背景 75% 透明（不降低前景元件透明度）。
9. 所有新增的 Info、Flow、Mod、Workspace 都需有永久 ID，版本變動不得讓引用無訊息失效。
10. LAB/PAPER/LIVE、交易、資金與權限來源的權威，仍屬既有 Python/API/BFF/後端契約，UI 只能呈現合法投影。

**證據範圍**：歷次對話 Owner 決策＋D36 原型／D36 QA。以上是設計候選摘要，非契約批准或施工授權。
