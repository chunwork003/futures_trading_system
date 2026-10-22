# 高階模型恢復後的 Catch-up Review Prompt

此文件只提供原 Review 責任的精確輸入；不是自動審查授權，不要求作者扮演獨立 Reviewer。Reviewer 以 fresh context 啟動，只有 qualified／independent 且原制度具備適用授權才進行正式判定。

```text
你擔任 futures_trading_system 的具資格 Independent Reviewer，承接已凍結B3的有界Stage/Catch-up Review。不要重新設計整個B3，也不要修改被審Subject。若你同時是該實作作者、繼承作者推理/自我評價上下文，先拒絕正式獨立角色，要求合格fresh reviewer。

Repository：D:\00_Learn\量化交易\Code\futures_trading_system
凍結交接：C:\Users\CHUNs\.codex\visualizations\2026\10\10\01a12634-1a08-7b51-bdfd-2d8ecbcc4889\ultra-b3-mvp-execution-handoff-v1
預編補充：C:\Users\CHUNs\.codex\visualizations\2026\10\10\01a12634-1a08-7b51-bdfd-2d8ecbcc4889\ultra-b3-precompiled-queue-addendum-v1

一、重新解析AGENTS/CURRENT_STATE/active manifest/policies/current program/CURRENT_WORK/unfinished/review/STOP。核對本次exact Review Grant、scope、reviewer資格與獨立性；沒有正式授權時只做允許的唯讀準備，不能自行稱Formal PASS。

二、讀ADDENDUM_MANIFEST、原native review queue、DEFERRED_REVIEW_LEDGER的真實entries及其exact reference。衍生ledger若與原native紀錄衝突，以原權威為準，停止受影響項目並記錄。不要把POC_RESULTS、entry_template、spec expected evidence或作者PASS當實際Unit Evidence；也不要將returned FIX_REQUIRED冒充單純延期。

三、對每個真實待審項固定：Unit/Revision/Source Subject、WO/Execution/Grant、Git/Diff/Result完整正文/ref/hash、測試與失敗、Operator/Producer/Consumer/Profile/Context/Continuity、成本、風險、原Required-before Gate、上游未驗證假設、direct/transitive/interface consumers、Stage/Wave/Independent/Human要求。缺不可替代正文/來源/授權就HOLD該項，不補造、不採信檔案數或PASS總數。

四、用原364-edge DAG找最早未審共享前置。先消除其下游共用假設，再在相互獨立根節點按安全/風險/影響排序。相同Contract Owner、版本、環境/Profile、review type且授權可涵蓋的exact subjects才做Cohesive Batch；每個Subject仍有單獨Verdict與證據，不合併身份/接受資格。578 Consumer及191 source-only規則保留，不能創造runtime依賴或整包barrier。

五、獨立重建最小Positive/Must-Reject Oracle，與固定實作/實際tests對照。核對required case IDs、source/DTO/schema/fixture/pair/reverse closure、Result ref/body digest、capital/order/fill等真正受影響不變條件。Source/Git/Profile/Environment變更先精確判定舊證據適用性，不全域重跑B3；必要環境試驗未獲授權時保留NOT_RUN，不假造真實資格。

六、逐項輸出原制度適用Verdict、Exact Evidence、反例、Risk、Root Cause、影響與最小Correction。已通過且未受影響的Accepted結果保留。若共享前置失敗或revision更動，依REVIEW_DEPENDENCY_IMPACT列出真正下游與接口重驗範圍；不要撤銷舊歷史Receipt或自動判下游已合格。

七、相同Root Cause合併成最少Cohesive Correction Candidate，包含精確source/preimage/allowlist/受保護bytes/positive/negative/regression與STOP。只準備候選，不修被審程式、不發Grant、不自動RF02。不因先前延期而追認未授權Coding合法。

八、正式Review完仍由既有WORK Intake/Integration/Human Acceptance各自依法處理。Review PASS != Integration PASS != materialized Acceptance，不能自行提升Machine State或credit。源碼未經正式接受前不能替代accepted dependency。若你沒有這些Owner權限，只提交exact decisions，不代簽。

最後輸出：每Unit exact verdict、跨Unit共享根因、影響/必需重驗、未取得Qualification、下一合法Candidate Frontier、真正可執行Frontier、最小Human決策與Durable Checkpoint。只有新的重大受保護架構矛盾才升級Architecture Owner；不因普通實作或未來環境缺失重開全B3。
```

**現在實際待審產品 entries = 0。** 本輪只驗證 catch-up 方法的合成世界；將來要補審多少，必須從原生實際結果讀取，不能從 96 個預編規格推算。
