# Raw34 Compiler Adapter — candidate.6

Current raw plan uses `EXECUTION_UNIT_PLAN_SCHEMA.candidate.v6.json` with all original 34 fields and closed nested shapes. The predecessor schema remains byte-identical at `EXECUTION_UNIT_PLAN_SCHEMA.json`.

`ENGINEERING_ADDENDUM.candidate.v6.md` is the exact successor contract for immutable complete request/context, source-only versus qualified dependency mode, version profile, HOLD and READY outputs. Compiler fixtures retain fixed Cycle01 input body/schema bytes as explicitly historical compatibility vectors; they do not compile the current candidate6 into an executable grant. Current plan6 must be separately bound and qualified by the existing WORK compiler, Reviewer/Intake and Owner gates. No original WORK compiler, accepted schema or receipt is replaced.


## Candidate 7 有界 successor

原closed schema5與C1/C2完整來源不可變；current plans使用EXECUTION_UNIT_PLAN_SCHEMA.candidate.v7.json以及PlanVerificationContract.cycle02_required_case_ids/PlanSecondaryIO.variant_rule具名形狀。raw→typed→raw每個欄值相等；unknown field拒絕。getArtifactContent所有consumer為ONE描述符union。

TrustedContextReceipt.context_artifact_ref必須指向真正projected artifact bytes；size以該原始bytes計算，最大131072。完整raw input provenance與context分離，不能把10MB原檔標成126KB。projection required closure/selector/source hashes固定；裁掉必要語義或UNKNOWN coverage仍HOLD。synthetic historical exercise不賦予R02/R06 adoption、current plan資格或派工權。

Legacy hash解碼需exact finite LEGACY_HASH_DOMAIN_ADAPTER.candidate.v7.json；無adapter或source/hash conflict=HOLD，不能以kind猜測公式。執行端切換保留unit/plan/source/evidence，同時fresh qualification與authority gate。
