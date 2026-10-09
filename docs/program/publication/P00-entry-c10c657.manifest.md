# 精確 Git Publication Manifest

狀態：APPROVAL_REQUIRED / NOT_PUBLISHED。

- Repository：`chunwork003/futures_trading_system`
- Source / destination branch：`architecture/p00-v1-baseline` → `architecture/p00-v1-baseline`
- 完整 local HEAD：`c10c6570ef420e9aa23655942dddc5ae77a333c9`
- 預期 remote HEAD：`aa6c8f556e1653700f2be9205673bffb98a690a2`
- Manifest SHA256：`dc0c95314bfab69527148d9239a6911f2cb79252df92ed87c659bdd0b1895e47`
- 普通 fast-forward：true；force/rebase/merge/master修改：false。
- Commits：10；淨檔案：57；A/M/D：`{"A": 43, "M": 14}`。
- Protected scope：PASS（包含每個commit父邊及origin/master delta）；data未讀／未stage。
- Publication僅發布已提交候選；不包含acceptance、merge、controller activation或product authorization。

## Commits（完整 ancestry / parent deltas見同名JSON）

| 順序 | 完整SHA | 用途 |
|---|---|---|
| 1 | `afa1666bb0fe452dadac7b67e9627f3df1b832c2` | feat(p00): bind DTO stores and composite decision currentness contracts |
| 2 | `ca3e474687db3f484252d74a239ccc83d644658e` | docs(p00): preserve bound review packet and blocked publication checkpoint |
| 3 | `08a160ddb4280e9b76062bdd3dc5393bab906e71` | feat(p00): bind historical requirements and acceptance scope indexes |
| 4 | `fd8ebd83f6885d66e376695de9e5d5e3cf331e11` | docs(p00): preserve source index review and continuation checkpoint |
| 5 | `c3750af32f0297e48b146db1823dda8c421a26b8` | docs(p00): define engineering reuse evaluation and telemetry contracts |
| 6 | `dce1e5409314539ca2ac98ba26ea54e8e6b1ab80` | docs(p00): bind engineering review subject and continuation evidence |
| 7 | `3db5a658ff82a42c328ff67ff1c2a99bde2580aa` | docs(p00): bind bounded historical semantic and scope bridges |
| 8 | `28cdd2e4cab4639ee46f7de3032a340eb868f88a` | docs(p00): bind historical semantic review and continuation checkpoint |
| 9 | `9106fbbba4199bca838cee794343296716a39df7` | docs(p00): define source-bound reading claims and qualification gates |
| 10 | `c10c6570ef420e9aa23655942dddc5ae77a333c9` | docs(p00): pin reading audit evidence and next source obligation route |

## 全部檔案（before/after content SHA256與mode見JSON）

| A/M/D | Path | after Git blob / deletion before blob |
|---|---|---|
| M | `automation/platform/AI_CONTEXT_BOOTSTRAP.md` | `f5c80a9bb914919ea99ea7291bb5b9846ffed5d4` |
| A | `automation/platform/CONTEXT_READING_RECEIPTS.md` | `3ab2b23bc6a306406a7ba7768f61945b7f93ddad` |
| A | `automation/platform/ENGINEERING_SYSTEM.md` | `c93f16a40391fe4aa94d980f6e9c753d5968c39c` |
| M | `automation/platform/PACKAGE_READING_OBLIGATIONS.md` | `25e510adca96173c9f5f84033394d801c2d226e3` |
| M | `automation/platform/README.md` | `f013156d3464b0a77975f456b73a5c275ad083c5` |
| M | `automation/platform/context_policy.v1.json` | `c4e51a81d6c613e187b7e3f9a904995b565785a2` |
| A | `automation/platform/context_reading_contract.v1.json` | `aa09d1d43107ef9283d99fcc1b8cba864b0afd7f` |
| A | `automation/platform/engineering_observation.schema.v1.json` | `a926cd547fbc141a5ae9dd5cc4cb0d1d9023d409` |
| A | `automation/platform/engineering_system.fixture.v1.json` | `ced07ae51b26fb6ba07ea6b7af95d2924c123382` |
| A | `automation/platform/engineering_system.v1.json` | `e801efeb3c9271d09c6806b1656a9fef8b0e7012` |
| A | `automation/platform/golden_evaluation.schema.v1.json` | `748b66cbd8bf62d45f598f7c824b78775be63850` |
| A | `automation/platform/reading_claim.schema.v1.json` | `8c1c2e2c7ce8b9945104ec4bf99ed9d28dba3211` |
| M | `docs/architecture/V1_CONTRACTS.md` | `1f92bef73591adccaedb9b3b73c86bf4cd71a29e` |
| A | `docs/architecture/V1_DECISION_RECOVERY_CUT.md` | `ddab30e3985cbf1be6d81b1347f7e34a45a1f1d7` |
| M | `docs/architecture/V1_DOMAIN_ADAPTERS.md` | `57aaa5bd817ec2c8f68ed7ad24d67aa40eef0884` |
| A | `docs/architecture/V1_DTO_STORE_MAP.md` | `339119557018c34345bd477ca71de7333e701be4` |
| M | `docs/architecture/V1_INCREMENTAL_PERSISTENCE.md` | `2b637ed5320d43754503a722a4b6573cc03ce9be` |
| A | `docs/architecture/contracts/decision_input_cut.fixture.v1.json` | `5fa13bce93a5de2202eb2a6f189407652a905e28` |
| A | `docs/architecture/contracts/decision_input_cut.schema.v1.json` | `9b2686b31f0a224d96fc4115b8306f2751a0c3eb` |
| A | `docs/architecture/contracts/dto_store_map.v1.json` | `7130d0ac10dc879c59eb3d83fe834e91c390ca3a` |
| A | `docs/program/HISTORICAL_REQUIREMENTS.md` | `30556578105f745690a92854e512085d9946423a` |
| A | `docs/program/HISTORICAL_SEMANTIC_BRIDGE.md` | `a62dcfc022c9d7150566efcdc893f22b962b9611` |
| M | `docs/program/P00_VALIDATION.md` | `148242038b78cdedff58431fa45702cf0024f6ef` |
| M | `docs/program/PROGRESS_ACCOUNTING.md` | `357f1750284bd1addf8a0bdca2d5728341b090a6` |
| A | `docs/program/accepted_core_reconciliation.v1.json` | `24add38424055a7ae79fdd9f8f0e520123b35978` |
| A | `docs/program/checkpoints/P00-R01-R05-20261009.evidence.v1.json` | `6c5bd122ed3c6046da5587dcf4f83987ab6e0456` |
| A | `docs/program/checkpoints/P00-R05-source-index-20261009.evidence.v1.json` | `48e656bbb2366fc1ee8a324e2c33f3a1a79b74a5` |
| A | `docs/program/checkpoints/P00-engineering-system-20261009.evidence.v1.json` | `cdf0c493a592c6edf82acc86f1d9975f177a607d` |
| A | `docs/program/checkpoints/P00-historical-semantics-20261010.evidence.v1.json` | `e1e2dba17bfb05ed71c98afaa2d4573df053faa6` |
| A | `docs/program/checkpoints/P00-reading-receipts-20261010.evidence.v1.json` | `9f4e81c9d27bf83abb67ffd0d98c179a6cb74a12` |
| A | `docs/program/context_packs/9106fbb/P01.reading-audit.json` | `042ccccdc18e35fec1683d571c6989a5ae71256f` |
| A | `docs/program/context_packs/9106fbb/P02.reading-audit.json` | `e2ead0df741fbfdae0d27607342db1da230a47df` |
| A | `docs/program/context_packs/9106fbb/reading-smoke.json` | `c0cf6aa2639076efeb85e0fbba58f0aec38d4aa9` |
| M | `docs/program/context_packs/README.md` | `25572bf0eba8fae684591c46ca00a83bf0c79d57` |
| M | `docs/program/current_truth.v1.json` | `8e09867f380c70118252a0b4fe71173066909be5` |
| A | `docs/program/historical_requirements.v1.json` | `397879b37830c7827b649dea77aef60324742fe9` |
| A | `docs/program/historical_semantic_bridge.v1.json` | `4c7364a6cb9d628a1b9c21455d1b6a81f3d337bc` |
| M | `docs/program/p00_status.v1.json` | `b4f789a24bb4fb6a227067a00cb9600a8391e6e2` |
| M | `docs/program/request_coverage.v1.json` | `68367190cf7bce6f0b1d5ef8d3a6fb88e474551d` |
| A | `docs/program/reviews/P00-R01-R05.review-request.v1.json` | `32e639e24606d11a6c5fedc0f357de4b6b67216e` |
| A | `docs/program/reviews/P00-R05-source-index.review-request.v1.json` | `e08eac43315238af046580fdc62d32b600c3fc1c` |
| A | `docs/program/reviews/P00-engineering-system.review-request.v1.json` | `32750555a7f26546ae8361f23f857f0c6466b9d2` |
| A | `docs/program/reviews/P00-historical-semantics.review-request.v1.json` | `f689bff3194ed30cd4074759a324aa21b9c6a96b` |
| A | `docs/program/reviews/P00-reading-receipts.review-request.v1.json` | `ee6789daa2be649663ce6352a17ed25e9bb8900f` |
| M | `docs/work/P00_BASELINE.md` | `575ae48194ef7cbdb2c4b0da12e9114a2c11c904` |
| A | `scripts/p00_adapter_contract.py` | `339baa22a460979997f151afb91d4d21d2491efc` |
| A | `scripts/p00_engineering.py` | `290d22fac92419e3b88fc50bff5b05a1d73b2fe7` |
| A | `scripts/p00_historical_core.py` | `78f51759d9d4b9efddc1c2f0f8fde2601af26149` |
| A | `scripts/p00_historical_semantics.py` | `92ce55fec940200c5d9e2404f1452f1515d8a45a` |
| A | `scripts/p00_reading.py` | `df80dd9db77f6503511d08d068651a2fd8faa4b4` |
| A | `scripts/p00_requirements.py` | `a59e97a108dfbec814270d2aac2eb49e6a903d48` |
| A | `tests/platform/test_p00_adapter_recovery_cut.py` | `e15ff2a73c42bf8520eae2a541c70086dc9d761d` |
| A | `tests/platform/test_p00_engineering.py` | `d40a0afb92ae362fd40047d7648acaaff348b3af` |
| A | `tests/platform/test_p00_historical_core.py` | `6f027e4fd8b51c4fea2cdf7dbf01bb9eb1f9ae1d` |
| A | `tests/platform/test_p00_historical_semantics.py` | `d69ef88df10ceda024703d56d729f3d27f9372c8` |
| A | `tests/platform/test_p00_reading.py` | `1516c99ca9384106ba7576c18d936010b069ecf9` |
| A | `tests/platform/test_p00_requirements.py` | `e8fb4fca24205e9cc82c0d9a6f460b398485d58b` |

## 驗證證據與核准界線

Exact checkpoint：`docs/program/checkpoints/P00-reading-receipts-20261010.evidence.v1.json`；Git blob `9f4e81c9d27bf83abb67ffd0d98c179a6cb74a12`。
測試／驗證摘要：`29_PASSED_42.90_SECONDS`；`469_PASSED_184.28_SECONDS`。
尚需使用者具體核准repository、目的分支、上述完整payload SHA與manifest SHA256。核准前不push；執行前重新fetch，如remote或payload變動須重建manifest。
