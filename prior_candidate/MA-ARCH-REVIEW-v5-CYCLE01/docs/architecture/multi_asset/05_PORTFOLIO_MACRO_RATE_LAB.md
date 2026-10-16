# MA05 — Portfolio／Macro／Interest Rate Lab 與 S14／S15 研究來源

Revision `candidate.3`；Owner F Research；S14/S15 disposition `FUTURE_RESEARCH_ONLY`（Human 本次明確補充）；AUTHOR_CHECKED／FORMAL_REVIEW_PENDING。

## Purpose／Source／Reuse

本章為完整產品的研究擴充契約，讀 MA02 profiles／MA03 snapshots／MA06 歷史唯讀投影，沿用 MA04 ResearchSnapshot／Run／Comparison／Library gates。不能建立第二個 runtime portfolio decision owner。債券 ETF／ratescenario／allocation 研究已確認；S14/S15 Human 特別指定 Future Portfolio Research Lab 暫存，不修改 accepted 主線。這個限定只適用 S14/S15，不把整個新 Lab 默默改 V2。

2026-10-11 已在 Downloads 找到並唯讀擷取三份活頁簿，私有 byte copy＋CELL_SOURCE_WITNESS 已保全；沒有保存/重算/編輯原 Excel。讀到的 cached results 不是本輪重新計算。最早定義日期2026/10/2 為 Human 來源敘述；取得檔案的 embeddedcreated metadata 為2026/10/11，故**不以此檔 metadata 證明10/2 的原始聊天日期**。原聊天「策略:債券架構」逐字訊息尚未取得。

| Source | SHA256／exact subject | Disposition |
|---|---|---|
| 投資組合_完整壓力測試_60 情境_績效排名.xlsx | abc12af0b0cf9695365bfb242b1322b4e3e5753b77d052566241d5dd14369876；策略設定!A15:C16 | ORIGINAL_RESEARCH_BASELINE；不可被後續配置覆寫 |
| S14_S15_深化比例回測_v2_StepBack_GridSearch.xlsx | ff05bc4b4920e98792d0b5d5bf285a297bd8e43f1ba3968eaa3ef36ff6c9a8eb | RESEARCH_REVISION_CANDIDATE；Stage/N/stepback/grid lineage |
| S14_S15_操作成本_階段金流損益_完整版_v2.xlsx | 721fa83db3ab9b30d81adff1b5c99490722746a3c5590988142dffa3087e8938 | RESEARCH_REVISION_CANDIDATE；成本/現金流/損益來源 |

S14 原始文字：Dynamic Carry-First70→50；B66/C34 分批→B70/C30→B50/C50→A10/B30/C60→A20/B30/C50→收割回 B50/C50。S15 原始文字：S14＋CreditGate，HY/BBB 壓力升高時降低 B/C/A 曝險並提高 cash。A=00680L、B=00984D、C=00937B；此代碼映射還需 MA02 上市商品 profile，不按名稱猜產品條款。原定義沒有可直接正式交易的量化「見頂／收割」觸發規則，本候選不自行補。

## Model／Inputs／Outputs

PortfolioResearchDefinition：id/rev、asset universe/listings、weight constraints、rebalance/transition policy、capital/cashflow assumptions、cost/tax/FX policy refs、objective。MacroDatasetSnapshot：series/provider/release revision、vintage/as-known dates、frequency/calendar/units；不能用 laterrevisedmacrohistory 冒充 point-in-time 信號。CurveSnapshot：tenor/discount/yield convention、currency/asof/source/interpolation、creditspreadbasis；Greek/DV01 從 MA02policy 計算。

ScenarioDefinition：id/rev、shockpaths、duration/credit/spread/FX/inflation/default/correlation、cashflow/cost assumptions、modelversion、sourcecells、probability(若無機率則 UNKNOWN)；人工 stress 不稱 forecast。StagePolicyRevision：Stage0/1/1.5/2/3、N1-N3、stepback、Credit/CashFlowGate，所有 transition 需 predicate 來源，model-only predicate 標 RESEARCH_ASSUMPTION。ResearchRun 紀錄 sourceworkbookhash/sheet/range/formulas/ref、parametergrid、selectedresult 與未選結果 coverage。

Outputs：return/equity/withdrawal/coupon/dividend/fee/tax/turnover/exposure/cashcoverage/drawdown/tailstress、stageeventlog、assumption sensitivity、rankingwithcomparability。金流 Gate 判指定支出需求、現金/分配可得性與 coveragewindow；不能把 unsettled 應收當可支出 cash。同資產 curve/shareprice/rates 的不同 measurement 不可共用 unit。

## Business Rules／Functions／State Machine

`capture_workbook(source)`→immutablebytes＋cell/formula/cachedwitness；`import_research_policy(sourcecells)`→draft 條件/assumptions，不轉 productionlogic；`evaluate_scenario(snapshot,scenario)`→metrics/coverage/equity/cashflow；`grid_search(definition,grid,budget)`→全部 attempt/selectionrule；`compare_portfolios`復用 MA04；`propose_stage_transition`僅 ResearchProposal。

Weightedreturn 使用每期實際 weight、cashflows/cost 與再平衡成交假設，不將 longtermleveragedETF 回報固定倍數化。BondETF NAV/marketprice/credit duration distributions 分別 source-bound；每個 scenario 明確 parallelrate/creditspread/effective duration 假設、convexity/非線性 limits。GridSearch 最佳參數是樣本內 selection，需要 OOS／WFO 與 multiple-testingdisposition；不得以60 情境績效排名作 approvedsignal。

Original 研究 revision→DerivedCandidate→CapturedRun→Compared→ReviewableResearch；ProductionLibraryCandidate 另外 exactreview/approval，RuntimeAdmission 更後。Workbook sourcecell correction 產生 newcapture，不改 Originalbaseline。StagePolicy incomplete predicate 可執行 modelassumption 試驗但不可稱可交易策略。

## Interface／UI／Security／Recovery／Compatibility

API `/api/v2/portfolio-research`、`/macro-snapshots`、`/scenario-runs`；UI Bond/RateLab：source&vintage 欄、curve/shocks、allocation/stage editor、cashflow/cost tables、risk/researchresults、compare/history；不可提供無 runtimegate 的一鍵 LIVE。研究輸入只讀 accountprojection，沒有資金轉移/交易 key。Excel formula 作資料/解析，不執行 macro/DDE 外部 links；external source references 受 MA13allowlist 規則。

缺 workbook/contenthash/cell、cachedmissing、vintageunknown、triggerunsourced→明確 unverified／research-only；retrynewattempt 保持原 assumptions，不填「零報酬」。Concurrentgridlimits 有 budgetreservation 與 runidempotency，resultsappendonly。ResearchRestore 需 originalsource 與 outputsbytes；重新跑同 model 不宣稱原研究結果一模一樣。

## Examples／Acceptance／Tests／Handoff／Limitations

正：S14 original 來源不動，N2/StepBack 候選 derived-from；S15 信用 shockmodel 明確假設；targetallocation 只是 researchproposal。反：後續高績效比例覆蓋 S14 original、把 HYstress threshold 當已 OwnerapprovedLIVE 條件、檔 metadata 當10/2 訊息證據、只留 hash 刪原 Excel、cachedsummary 當新 backtestPASS。

Acceptance：三份 sourcehash/cellbinding＋lineage 可查、Original 與候選分開、research/prod/runtimegates 分離、portfolio/cashflow 一致、genericMacro/Rate 模型可擴充。Tests：cashflows/fees/tax/rebalancingdoublecount、curve/durationunit、vintageleakage、gridcoverage、Stageconflictingtriggers/unknownpredicate、sourcecell/formulahash 差異、corrupt/missingartifact、incomparableperiod。

WORK：先 sourcecapture/typedimport、genericPortfolio/Macro/Rateengine、scenario/stage/results、UI/API。S14/S15productionpromotion **不在這次 scope**，精確量化觸發條件未批準不阻塞通用 Lab 施工設計。歷史 workbook 非 validatedmarketdata；稅率/產品條款/外部研究資料未重新核實，實際研究採用前須官方 sourcequalification。
