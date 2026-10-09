# Development Platform — P00 candidate

This directory contains proposed platform specifications and evidence indexes. It grants no runtime authorization and does not replace `docs/CURRENT_STATE.md` or accepted machine policies.

Read `docs/work/P00_BASELINE.md`, then `docs/program/p00_status.v1.json` for continuation. Reuse existing `automation/engine`, role kernels and seven shadow Skills; do not create a second operational controller.

- `capability_inventory.v1.json`: observed source artifacts with Git provenance. Maturity is provisional artifact-level classification, not measured operational reliability.
- `skill_registry.v1.json`: seven existing Skills, explicit lack of behavioral qualification and missing capability backlog.
- `OPERATING_MODEL.md`: proposed responsibility, safety and ranking rules.

- `AI_CONTEXT_BOOTSTRAP.md`: bounded resume and source precedence; preserves existing current-state authority.
- `context_policy.v1.json` / `scripts/p00_context.py`: exact Git context resolver, P00 only; no execution grant.
- `agent_registry.v1.json` / `tool_registry.v1.json`: typed candidate logical roles and tool effects, with matching JSON Schemas.
- `tests/platform/`: schema/isolation/negative Git fixtures; passing offline tests does not establish operational qualification.

Package/compiler and progress-ledger prototypes are indexed by `PACKAGE_COMPILER.md` and `docs/program/PROGRESS_ACCOUNTING.md`. Engineering-system candidate definitions are indexed below. Full golden-task behavioral evaluations, trusted telemetry/intake and current-projection migration validation remain pending. Until independently accepted, these are not enabled automation capabilities. API candidate authoring and generated contracts are indexed by `docs/architecture/V1_API_ARCHITECTURE.md`.

## R04 automation 候選索引

- `AUTOMATION_MINIMUM_AND_SCHEDULER.md`：minimum-useful取捨、adaptive ranking/wake、delegation與activation界線。
- `automation_mapping.v1.json`：003 Rev2～009每項source acceptance與CE/TEL/REENTRY來源綁定、處置與保留backlog。
- `scheduler_proposal.schema.v1.json`：只可產生非執行proposal，不是accepted route owner／controller。

原ProgramV2/Capacity2.2與blocked-lane-head規則保持不變；本候選不能授權scheduler activation。

## R03／R07 engineering system 候選索引

- `ENGINEERING_SYSTEM.md`／`engineering_system.v1.json`：原始十項必交付的template、generator、pattern、eval、golden、KPI、optimization、兩類telemetry與D0–D5 roadmap契約。
- `engineering_observation.schema.v1.json`：未量測保留null，共享帳戶quota不轉作actor cost；actual actor tokens與accepted weight等待可信intake。
- `golden_evaluation.schema.v1.json`：固定source／fixture／oracle／environment／case集合，self-declared outcome不產生qualification。
- `engineering_system.fixture.v1.json`／`scripts/p00_engineering.py`：只檢查來源、shape、反例與spec算術；九類shape examples全是NOT_RUN，不是九類真實golden執行。

本候選復用既有compiler／context／source index，不建立第二個controller。Authoring、工具資格、產品驗收與效果量測各自需要證據；完整歷史語意、R06原128KiB gate及獨立baseline review仍待完成。

## R06 reading claim compatibility 候選

`CONTEXT_READING_RECEIPTS.md`／`context_reading_contract.v1.json`／`reading_claim.schema.v1.json`／`scripts/p00_reading.py`復用原resolver/packer建立mandatory representation與session/source綁定。所有claim仍UNVERIFIED，不產生trusted acknowledgement、current-intake completeness或compiler gate migration；RQ01–RQ06及原128KiB總source gate保持。
