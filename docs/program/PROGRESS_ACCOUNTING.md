# R05 — 候選進度基線與證據規則

狀態：CANDIDATE / NOT FROZEN / NOT EXECUTION AUTHORITY。
`program_baseline.v1.json` 是目前已知 V1 **剩餘整合工程**的候選分母；不是從零重建產品的總工程量，也未涵蓋完整歷史需求。權重為相對工程判斷，不是天數。P01/P02 沿用 exact candidate 的既有權重，P03–P12 是待獨立審查的初估。P00 是設計 gate，不領取 runtime implementation 權重。

## 四種進度不能混用

| 指標 | 分母／證據 | 本次可報內容 |
|---|---|---|
| Product | 全歷史需求 registry、已驗收既有能力與剩餘工作 | UNCALIBRATED；歷史覆蓋尚未完整 |
| V1 engineering | 經獨立 baseline 審查凍結的 deliverable 權重 | UNCALIBRATED；候選 ledger 已建立，不能把候選 delta 零 credit 宣稱為產品 0% |
| Critical path | DAG 上尚未驗收的關鍵 package | 目前候選 chain 9 個，全部 V1 分組 13 個含 P00；不是 duration CPM |
| Automation | 可觀察行為的資格 evidence／promotion gates | UNQUALIFIED；inventory 的存在性標籤不等於自主運作資格 |

可部署流程另報 `0/6 verified journeys`：表示沒有已綁定、可驗證的 release evidence，並不證明現有所有功能都不可用。P00 R01–R08 closure 另計；不能拿文件數／測試數取代其閉合數。

## 凍結後的 gate 與 evidence intake 規格

每個穩定 deliverable 的 credit = weight × (2I + T + G + A)/5，使用有理數運算，顯示時才四捨五入。I 為 implementation，T 為 targeted tests，G 為 integration，A 為 independent acceptance；皆為 0/1。T/G 必須有 I；A 必須有 I/T/G。設計稿、測試規格或 mock 通過不能充作已實作整合證據。各 deliverable 的 integration gate 是其承諾邊界，不必等待全產品 release。

未來 intake 必須同時驗證：baseline revision、deliverable/contract revision、implementation subject SHA、證據 exact Git blob 或不可變 artifact hash、測試命令與環境、outcome、producer identity；acceptance 另需 reviewer identity、獨立性、exact reviewed subject 及 review disposition。package acceptance 需要全部所屬 deliverable A 與依賴 package acceptance。release journey 另綁 exact release manifest 與所需實際環境，不能跨版本拼接六條 PASS。

不同提交不自動使既有 evidence 全失效：需有明確 compatibility/impact 判斷。受到 contract/source/environment 變更影響者追加 invalidation event（理由、受影響 IDs、原 evidence、替代 evidence）；先撤除受影響 gate 及其衍生 gate，保留歷史。不得直接覆寫過去 acceptance。未知可信度一律不給 verified credit。

**本次 offline calculator 尚未實作上述 intake。** 它只驗證候選空 gate、DAG、權重與拆分規則；任何非空 gate、acceptance、journey evidence 或 invalidation 都拒絕處理，避免把任意 JSON 的 PASS 當成驗收。實作可信 intake 屬後續 R05/R02 工作，不是此工具已具備的能力。

## 分母守恆與變更

- Stable deliverable ID 與 weight 屬 baseline；package 是工作分組。拆分 allocation 必須唯一且加總等於原 weight；子工作不再領取一份父權重。
- Correction 指向原 deliverable、added_weight 必須為 0；correction 次數影響成本／風險／ETA，不增加進度。
- 同一 revision 不得新增／刪除／重命名 deliverable 或改權重。真正新需求需有來源、scope delta、獨立 baseline change 決定，升 revision 並保留前後分母與百分比 bridge；不能用 correction 偽裝 scope expansion。
- `validate_regrouping` 驗證同 revision 穩定 IDs、contract revisions 與權重不變。目前固定 P00–P12 grouping；新增可執行 package 或改 DAG 仍需另行審查，不由此 checker 自動許可。

## 工期與排程

P01–P12 合計初估 **71–111 effective engineering days**，不含尚未估妥的 P00；不是日曆 ETA，也不是並行無限的最長路徑工期。one writer、review 等待、correction、可用 quota 與外部環境都影響 elapsed time。P00/P01/P05/P06/P07/P08/P09/P11/P12 的 9 個節點是目前依賴假設；P03/research branch 可能改變 duration critical path。

ETA optimistic/base/conservative 保持 UNKNOWN，直到可取得同類 package 的實測 accepted throughput、耗時、correction/review 分布及可用 capacity。不得把每天 wake 次數當有效工作天，也不以既有 tests/commits 估計速度。外部 broker/live gate 與無關 V1 工作分開計算。

## 重現與剩餘工作

執行 `python -B scripts/p00_progress.py docs/program/program_baseline.v1.json` 可重算目前候選數字；無檔案寫入、網路或執行 side effect。tests/platform/test_p00_progress.py 驗證分母守恆、重複 ID、循環依賴、假 evidence、虛構 ETA 等負向情境。

R05 尚未閉合：完整歷史 requirement registry／accepted-core 對照、候選權重獨立審查、可信 evidence intake 與 invalidation、實測 throughput/ETA 仍缺。完整產品 completion 不在本次假裝給出數值。
