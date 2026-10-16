# 既有 WORK Compiler 的 v8 Schema Companion

唯一有效輸入配對：exact v7 Unit Plan / plan revision / raw或既有semantic hash ＋96_UNIT_SCHEMA_COMPANION_INDEX中同unit_id的v8 companion revision/hash＋其固定Schema catalog與operation wrappers。缺 companion、錯 subject、unknown profile、同 revision 異內容或缺 reference closure 皆 HOLD，不可退回單獨v7 plan。

原 plan 34欄、typed lossless及允許修改範圍不變；新欄位只在 versioned companion，不修改 closed schema。WORK 在既有依賴/資格判定前組合此effective contract；編譯產物須列 unit_id、base_plan_revision_id、schema_companion_revision_id、catalog rawhash、wrappers rawhash及 architecture subject。相依結果仍需既有 qualified result/reuse binding。

預期測試與預期compilation plan不是 actual implementation evidence；執行模型切換不改 unit/feature/進度/acceptance。作者source tests、Reviewer design verdict、Owner採納、execution授權與runtime qualification分離。舊109 companion仍固定為原provenance；新增schema companion必須載入，不能假稱原hash已變更。
