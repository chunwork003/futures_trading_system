# R06 — 分包閱讀與結果接收候選規格

狀態：READING AID ONLY；尚未完成 current intake，尚未移轉 resolver/compiler gate。

## 分包閱讀

`context_selection.v1.json` 明示 API path roots 與 schema roots。P01 為資料集檔案匯入，不實作 HTTP endpoints；載入資料集與錯誤契約，以及所有遞迴 schema refs。P02 為完整 API shell，保留所有 endpoint，不因縮小 context 移除登入、交易拒絕或錯誤契約。所有選取 schema 保留完整值；security、servers、extensions 與非 schema components 保留，其 refs 也必須閉合。

`p00_context_pack.py --selective` 另列 excluded paths/schemas，保存完整來源 Git blob，不能宣稱可還原被排除的完整 API。`expand_json` 對有 projection 的文件只還原該投影；無 projection 的文件維持完整值。非 schema components refs 須解析至完整保留的目標；外部 refs、未解析 refs、dynamic refs 或未知 roots 拒絕，不猜測展開。新 ref 型別需擴充並驗證 resolver，不能默默忽略。

投影只改閱讀內容，不改 scope、canonical contracts 或 compiler 的完整來源 budget gate。涉及被排除介面、跨模組 review、矛盾、scope change 時必讀完整來源。128 KiB 是 byte target，不是模型 token 保證。source hash 相同不代表投影語意已獨立驗收。

## 當前結果閱讀

`result_reading_index.v1.json` 綁定已接受 AUTO-IMP-002 前件與 P01/P02 最新已保存編譯。`p00_result_context.py` 核對 exact source bytes、目前檔案 blob、編譯內完整 candidate 值及 master 上的前件。它不以檔案 mtime、最大流水號或最新聊天判定權威。

呼叫端先 fresh 取得 remote master SHA，再傳 observed-master；工具為離線讀取，不把呼叫端輸入冒充網路 freshness attestation。master drift、candidate change、source drift 或角色缺失須重新 re-entry／重建索引。P01/P02 舊編譯即使 candidate 未改，也不能證明新 context 有效：標示 HISTORICAL_COMPILATION_RECOMPILE_CURRENT_CONTEXT_BEFORE_USE。接受前件不授權後件，消耗過的執行不允許重送。

## 完整 intake 的剩餘契約

下一階段仍需一個經審查的 current machine projection，明示 active execution/writer、pending result、pending review、STOP、latest delta 與 last accepted result。各項均需 exact identity、revision、source hash、lineage 與 supersedes 關係；無項目須有可驗證的 explicit none，不能從索引缺項推論 none。

WORK 必須先處理 STOP／安全阻塞，再核對 unfinished execution（只能依真實 invocation lineage resume），再 intake result→review→integration→acceptance，才選新工作。result 與 review 分離；作者不能自 ACCEPTED。receipt 的冪等 key 為 exact execution/result identity；重送相同內容可讀取既有 receipt，內容衝突阻塞；兩次讀取間 state 改變須重算，禁止沿用舊 dispatch 決定。

此版本 `complete_current_intake=false`；不自動掃描或解析所有歷史 prose，pending result/open review/STOP discovery 尚未實作。因此不能把索引通過作為 current legal work 的充分條件。既有 accepted WORK re-entry 必須保留，controller 仍未啟用。

## 遷移門檻

先量測兩套件新 pack；再完成上述 current projection/intake 與負向 eval；獨立 reviewer 確認不可遺漏義務；最後另以精確授權修改 resolver/compiler 接受的閱讀來源。任何步驟尚缺均保留原 gate，不能靠縮小數字宣告 P01/P02 可執行。
