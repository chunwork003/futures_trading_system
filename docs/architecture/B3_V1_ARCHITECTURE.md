# B3 V1 Architecture — 唯一有效採納入口

狀態：**Human 已精確批准；已在本機工作樹物化為 Source-Bound Addendum**。不是新的全域架構取代，也不表示已發布到 Git master／main。

採納 Subject：`MA-ARCH-REVIEW-v9-SOURCE-CLOSURE-PAIR01`。[Owner Receipt](<D:/00_Learn/量化交易/Code/futures_trading_system/docs/program/decisions/B3-V1-DUAL-ADOPTION-20261015-v1.owner.v1.json>)，SHA256 `6330d4f2a22333cf3baeb1c1d558731bb896aaadd6b00a23ffd3dc2d82fac942`。

[Accepted Baseline Manifest](<D:/00_Learn/量化交易/Code/futures_trading_system/docs/architecture/adopted/B3_V1_ACCEPTED_BASELINE.v1.json>)，SHA256 `163e3c88cc09a7fc7f309a763f2cbc5ce41524306fb7e8af0910bea0018d3535`。原 A Scope `ff5fbb4b378dcb9aac91d4a0b55474a8ed9de944121593f7baa441c6f4bd1b01` 不變；B Policy Scope `6a92215477e06edd2a885846264e4d1b2ecffd72866a4b2e1f8dea756f1590e6` 從固定雙項包解析，沒有替代Scope。

## 有效內容與唯一責任

原 accepted Architecture 1.2.2／ADR／GAP08／Program V2／Capacity2.2、R01／R03／R04／R05／R07 exact semantics 保留。有效內容依 baseline 的694份直接Artifact membership、v9 Envelope／全量Manifest／Registry Head及明示typed closure選取，不依最新檔名，也不把7861份audit inventory都當同時有效契約。

原候選 `MASTER_INDEX.md`、`DESIGN_STATE`、各原始Candidate／Pending／v7標籤保留作歷史；其內舊source_revision不覆蓋外部已固定v9 successor。沒有修改原16章、19UI、95API、96Unit的bytes／永久身份／364條依賴；閱讀工程輸入時也必須帶必要companion及adapter。

## 16章固定入口

| 章ID | 固定章節 | raw SHA256 |
|---|---|---|
| MA01 | [MA01 — 範圍、來源、正式權威與採納路線](<C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/source-closure-pairing-20261015T005839Z/candidate/docs/architecture/multi_asset/01_SCOPE_SOURCE_AUTHORITY.md>) | `6e31510714d36abec3740e7f6613f52ce05929273887837d7047d03aa4f970c2` |
| MA02 | [MA02 — 多資產 Domain、商品生命週期與估值契約](<C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/source-closure-pairing-20261015T005839Z/candidate/docs/architecture/multi_asset/02_ASSET_DOMAIN.md>) | `1ae53791652c8ba11d52a7843a83323e1fba1579771a6147264bb6f269899fb8` |
| MA03 | [MA03 — Market Data、來源、資料品質與可重播版本](<C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/source-closure-pairing-20261015T005839Z/candidate/docs/architecture/multi_asset/03_MARKET_DATA.md>) | `5201c7f63f405b412b41d77ff8809e8c092b7eba4b78bef6421099b778655387` |
| MA04 | [MA04 — Research & Strategy Lab、Builder 與不可變研究版本](<C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/source-closure-pairing-20261015T005839Z/candidate/docs/architecture/multi_asset/04_RESEARCH_STRATEGY_LAB.md>) | `2dbd519a995eb62637cc6890c7b632c5314254002c9d69c799f9345a59ea201b` |
| MA05 | [MA05 — Portfolio／Macro／Interest Rate Lab 與 S14／S15 研究來源](<C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/source-closure-pairing-20261015T005839Z/candidate/docs/architecture/multi_asset/05_PORTFOLIO_MACRO_RATE_LAB.md>) | `a6c6bb5a019988db43eaad6bf6d219ae40aaa485945dce34f92c3431c1291367` |
| MA06 | [MA06 — Portfolio、Capital、Cash Flow、Accounting 與策略歸屬](<C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/source-closure-pairing-20261015T005839Z/candidate/docs/architecture/multi_asset/06_PORTFOLIO_CAPITAL_ACCOUNTING.md>) | `fed7b43efeb28cefe3129f9091716a8a2d34cf6238e7ed23a7ead99a59d10770` |
| MA07 | [MA07 — 唯一決策層、資本準入、跨資產風險與 Strategy Group 衝突](<C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/source-closure-pairing-20261015T005839Z/candidate/docs/architecture/multi_asset/07_DECISION_RISK.md>) | `583845af956691fc6a232fc3c48f1ea91a31e53520a2b3189575ef4fddf4ab13` |
| MA08 | [MA08 — OMS、PAPER／LIVE 隔離、故障恢復與 Fresh Re-entry](<C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/source-closure-pairing-20261015T005839Z/candidate/docs/architecture/multi_asset/08_OMS_PAPER_LIVE.md>) | `f879f341072fe6f4cedbb395bffdd7bde5c5b55971b45e247c774432d71f15b1` |
| MA09 | [MA09 — Broker Gateway 與具體 Shioaji Adapter](<C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/source-closure-pairing-20261015T005839Z/candidate/docs/architecture/multi_asset/09_BROKER_SHIOAJI.md>) | `cdfa2b7103e4167b4bd5ea33cb000238ea6e50dce9944d152cbdcfeb27b8cf7a` |
| MA10 | [MA10 — Web UI、ASP.NET BFF、Python API 與可施工畫面契約](<C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/source-closure-pairing-20261015T005839Z/candidate/docs/architecture/multi_asset/10_WEB_UI_API.md>) | `d39ddcf729bcac335867ae86f395dbaec3562ab248520aa87f381abe5ced59a0` |
| MA11 | [MA11 — URMS Permanent Identity、正規化編碼、雙樹與版本化關聯](<C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/source-closure-pairing-20261015T005839Z/candidate/docs/architecture/multi_asset/11_URMS_IDENTITY_RELATIONS.md>) | `60a385c4d6b103ac253902237e4098e90fc4a83c61b664f868b1624a813bba56` |
| MA12 | [MA12 — Git／PostgreSQL／Artifact Authority 與 Versioned Publication](<C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/source-closure-pairing-20261015T005839Z/candidate/docs/architecture/multi_asset/12_PUBLICATION_AUTHORITY.md>) | `827a16477e179754f49a141c92ed174e06f5fae37f8aa053e28c72467bf26d3f` |
| MA13 | [MA13 — Storage、Critical Capture、A／B 備份與可驗證恢復](<C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/source-closure-pairing-20261015T005839Z/candidate/docs/architecture/multi_asset/13_STORAGE_RECOVERY_SECURITY.md>) | `4ddfa15c7861fc6eca59248a4ca4f04c711d4d73c2d12fe10f9928c41b6a634f` |
| MA14 | [MA14 — 唯一 WORK、可替換施工契約與持續工程](<C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/source-closure-pairing-20261015T005839Z/candidate/docs/architecture/multi_asset/14_ENGINEERING_EXECUTION.md>) | `7f74a8f8d83010928371c3676b8ce001e78bc019527cc8e9d574d4b16be12332` |
| MA15 | [MA15 — 跨章節 Integration、客觀資格與獨立審查 Subject](<C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/source-closure-pairing-20261015T005839Z/candidate/docs/architecture/multi_asset/15_INTEGRATION_ACCEPTANCE.md>) | `eef5a35696a86fe0c0c2d091269fe941872a16a64681f72e4577ab0be29eda4b` |
| MA16 | [MA16 — 部署、環境、組態、Migration 邊界與可持續營運](<C:/Users/CHUNs/.codex/visualizations/2026/10/10/01a12634-1a08-7b51-bdfd-2d8ecbcc4889/source-closure-pairing-20261015T005839Z/candidate/docs/architecture/multi_asset/16_DEPLOYMENT_OPERATIONS.md>) | `7b0211cf4fd342b0700cce78699133c429bd9aa9c051d402e5ae77b7b31d891d` |

UI／API／Unit索引及完整必要引用均從 Accepted Baseline 的 effective membership 取得；WORK仍按固定Unit與Domain Producer編譯，不以Package聚合重算權重。

## 工程與保留資格

穩定SOP：[PROJECT_OPERATING_GUIDE](<D:/00_Learn/量化交易/Code/futures_trading_system/docs/PROJECT_OPERATING_GUIDE.md>)。動態狀態只看 [CURRENT_STATE](<D:/00_Learn/量化交易/Code/futures_trading_system/docs/CURRENT_STATE.md>)；Queue只看 [CURRENT_WORK](<D:/00_Learn/量化交易/Code/futures_trading_system/docs/CURRENT_WORK.md>)。

B3設計採納不等P00 Closure。R02／R06 qualification/adoption、R08 final review、C3→C5→C6與P00 0/8保持；P01／P02 baseline未接受不能READY。Compiler／Context／Intake的actual資格、Source Integration、exact Work Order／Writer／Capacity／Dispatch、SQL／Migration／Restore／Broker／PAPER／LIVE／Controller／Release各自保留。

目前正式Git來源仍是master；最終main政策已確認，整合未執行。本次僅合法docs本機物化，未Commit／Push／Merge，也不宣稱乾淨環境可從尚未發布的Git取得本機完整私有候選。
