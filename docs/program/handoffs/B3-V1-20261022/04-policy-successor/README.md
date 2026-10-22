# B3 V1 Fresh Re-entry — 固定續作入口

本入口為2026-10-22的衍生導航與候選交付，不取代 Repository Current Authority。所有原件／已接受 Evidence 保持不變。本輪未產品Coding、正式Qualification、Git寫入或Controller啟用。

## 本輪實際完成

- GitHub19個分支／HEAD及各完整tree逐一讀取；最後重新確認19個HEAD均未變。default仍master。
- 原H六檔、Q119檔、最新原Review10檔固定Hash核對；141個原Source pin讀回相符。原96/95/19/364/578與MVP57/184/11的完整設計證據依既有獨立Review重用，不無故全量重審。
- 原F01/F02/F03由單一新的候選補充，不修改原Q/H/Policy/Schema。新Fresh-context來源語意複審為POLICY_ACCEPTABLE_FOR_OWNER_ADOPTION，剩餘政策語意Finding0。這不是Owner採納、native受控Reviewer資格、啟用或執行權。
- MA02-U01原始Unit／spec／9 Fixture／U01 accepted Result ref+canonical body／接受收據／三項產品Hash核對，保存scoped reuse提案及WO編譯輸入，沒有轉授U01資格。
- HEAD/branch/status/refs/index raw及受保護Sources測量均無漂移。新交付只在本隔離根目錄。

## 狀態分開

| 項目 | 結論 |
|---|---|
| B3 Architecture／Guide | 外部精確收據已採納；維持原scope |
| Accepted engineering Units | MA01-U01，1/96 |
| 96預編規格／MVP路徑 | 固定衍生規格，非96份Grant |
| 新政策source-only Review | POLICY_ACCEPTABLE_FOR_OWNER_ADOPTION；未Human採納 |
| 新政策33個oracle | 已逐項獨立語意判定；未執行測試／Qualification |
| 原6 Mock PoC | 重用已固定6/6離線證據；本輪不重跑、不冒充產品測試 |
| MA02-U01 | 只有Source/WO preparation；尚無限定適用性、實際使用資格、Coding Grant |
| U02 actual use | NOT_OBTAINED_HOLD_U02_QF01；原支線保留，不在57-Unit MVP closure |
| C3／C5／C6／P00 | NOT_QUALIFIED／NOT_AUTHORIZED_NOT_EXECUTED／PENDING_HUMAN／0/8 |
| 新產品Coding／Grant／Writer | 0／0／0；不自動派工 |
| Git整合／發布 | 未執行；本機新交付尚未發布 |
| Controller | 不需要新增；未啟動 |

## 最短導航

1. [Git與本機差額](GIT_PUBLICATION_AUDIT.md)；逐檔raw Hash／Git blob／命中分支見[GIT_PUBLICATION_AUDIT.json](GIT_PUBLICATION_AUDIT.json)，全部19分支witness及最後HEAD重核在同根。
2. [固定政策候選](candidate/POLICY_SUCCESSOR.candidate.1.md)；[Candidate Manifest](candidate/CANDIDATE_MANIFEST.json)；[33個設計Oracle](candidate/POLICY_ORACLES.json)。
3. [新獨立來源Review](fresh-review/FRESH_INDEPENDENT_POLICY_REVIEW_REPORT.md)；[逐Finding Ledger](fresh-review/FINDING_LEDGER.json)；[Review Manifest](fresh-review/REVIEW_OUTPUT_MANIFEST.json)。
4. [精確Owner決策請求](NEXT_MINIMUM_HUMAN_DECISION_REQUEST.md)及[Scope](POLICY_OWNER_ADOPTION_SCOPE.candidate.json)。不把舊Decision Scope擴張。
5. [MA02準備完整來源](MA02_U01_PREPARATION.candidate.json)、[WO編譯輸入候選](MA02_U01_WO_COMPILATION_INPUT.candidate.json)、[可直接複製到新對話的Prompt](MA02_U01_NEXT_PREPARATION_PROMPT.md)。
6. [結構Frontier](FRONTIER_DISPOSITION.json)與[真正Authority差額](NEXT_AUTHORITY_MATRIX.json)。全B3結構候選8項，MVP其中4項；真正可執行Frontier仍空。
7. [原Kernel最小補充導航](CONTINUATION_NAVIGATION.candidate.md)；原H/Q閱讀路徑不依聊天記憶，損壞的歷史根目錄literal以明示root mapping＋exact hash解析。
8. [最後Checkpoint](DURABLE_CHECKPOINT.json)與[整包Manifest](OUTPUT_MANIFEST.json)。

## 有界政策結論與限制

- F01只處理額外advisory；分類/條件/deadline/source未知就HOLD。原native pending／unfinished route及Mandatory Review絕不越過。
- F02採一次Owner批准有限的exact逐項決策容器；每Unit仍有獨立native WO/Auth／消耗／單Writer／budget。不是可重用parent Grant；未知未來內容仍需精確批准。
- F03縮限為禁止候選串接；不把未驗證上游傳成正式或候選下游實作資格。可唯讀分析與獨立合格工作，沒有Grant不Coding。

~~~mermaid
flowchart LR
  P[固定政策＋Fresh來源Review] --> O[Human精確政策採納]
  A[MA02已固定Source／U01 reuse提案] --> Q[MA02限定適用性＋使用資格]
  Q --> W[exact WO／預算／Writer eligibility]
  W --> G[Human Coding Grant]
  G --> E[原WORK與合格Executor]
  E --> R[強制Review／Intake／Acceptance]
~~~

政策採納不是MA02 Qualification或Coding Grant，也不必把新Batch政策當作單張Unit準備的前置依賴。Git文件發布可以獨立準備，但需新的public-safe exact allowlist與Git Grant；不得重用v3/NAV權限。main/master歷史整合另案。

## Ultra退出與回來的條件

已凍結的架構、96張規格與普通逐單規劃不再交回Ultra。一般WORK／GPT／VSCode／CODEX／LM可依固定來源持續唯讀／候選準備；有實際資格與Grant後才依原程序施工。工具切換不繼承前一Executor的Qualification、Writer或已消耗Invocation。

高階Reviewer只在原適用Stage Gate、風險／Consumer DAG合併的Catch-up批次、受保護權威／架構衝突時介入；合格獨立替代Reviewer可以承擔符合資格的Review，不永久綁定模型。未取得nativeReviewerProfile不冒充產品ReviewReceipt。

主要未完成項目均在NEXT_AUTHORITY_MATRIX具名：政策Owner決定、MA02路線／使用資格及後續Coding權限、新文件精確公開範圍與Git權限；Compiler真實Host/C3及未來Runtime資格仍HOLD其實際適用路線。沒有新的B3全域架構阻斷，不新增Controller。

外部模型API呼叫0；精確Token／計費不可觀測為UNKNOWN。33個設計Oracle與9個Fixture讀回不是33/9個實測通過。沒有背景工作在本次結束後繼續。

