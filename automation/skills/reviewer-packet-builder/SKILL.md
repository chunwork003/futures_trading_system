# Skill: reviewer-packet-builder

Status: SHADOW

Trigger:
COMPLETED_PENDING_REVIEW

Inputs:
work order, authorization, execution branch, execution_start_sha, claim_commit_sha, implementation_commit_sha, evidence_commit_sha, exact source scope, tests, scope verification, completion evidence

Build a minimal Independent Review packet containing:
- exact work/package identity
- exact SHA binding
- exact implementation and protected scope
- required semantic review questions
- mechanical evidence summary
- correction budget
- next-package restriction

Rules:
- Mechanical PASS != semantic PASS
- packet must not predeclare reviewer verdict
- packet must not grant merge, correction, or next-package authority

Output:
review packet + routing metadata for a fresh-context Independent Reviewer.
