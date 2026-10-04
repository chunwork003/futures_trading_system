# AUTO-IMP-001 QRF01 — Provider-Native Quota Admission

```text
RF_ID = AUTO-IMP-001-QRF01
BASELINE = addf17379223cf4807e7b773f6034134ff7478e9
STATUS = REVIEW_FIX_APPLIED_PENDING_RE_REVIEW
ACTIVE_POLICY = QuotaAdmissionPolicyV1 v1.0 FROZEN
CANDIDATE_POLICY = v1.1-candidate / NOT ACTIVE
AUTO-IMP-001 = AUTHORIZED / NOT EXECUTABLE
```

## Trigger

The current AUTO-IMP-001 planning forecast is expressed in tokens (`P90 = 36,000`), while the ChatGPT Work/Codex plan UI exposes included allowance as provider-native percentage remaining.

User-provided fresh UI evidence observed during this discussion:

```text
5-hour remaining = 100%
5-hour reset = 4h36m after observation
weekly remaining = 98%
weekly reset = 5d16h after observation
```

This evidence demonstrates high provider-reported headroom, but the screenshot is not reusable as future dispatch evidence; a fresh snapshot is required at reservation time.

## Official OpenAI research basis

Research date: 2026-10-04.

1. OpenAI Help — Understanding and counting tokens
   https://help.openai.com/zh-hant/articles/4936856-understanding-and-counting-tokens

   Token usage has input, output, cached-input and reasoning components. Output/reasoning usage is not fully predictable from visible output. Token/request limits are distinct from API rate/monthly/spending limits.

2. OpenAI Help — Reviewing API usage and costs
   https://help.openai.com/zh-hant/articles/10478918-reviewing-api-usage-and-costs

   API usage can be inspected through API response usage fields and the API Usage Dashboard. This is API activity and is not evidence for the included ChatGPT Work/Codex plan allowance.

3. OpenAI Help — Managing usage with GPT-6 Astra in Work and Codex
   https://help.openai.com/en/articles/20001516-managing-usage-with-gpt-6-astra-in-work-and-codex

   Work/Codex allowance does not correspond to a fixed number of messages or tasks. Consumption depends on model, task, context, reasoning and settings. When both five-hour and weekly windows apply, both require remaining allowance. Settings > Usage is the provider surface for current remaining allowance/reset time. Usage percentage means used or remaining according to its label.

4. OpenAI Help — Using Codex with your ChatGPT plan
   https://help.openai.com/zh-hant/articles/11369540-using-codex-with-your-chatgpt-plan

   Codex/Work may share plan allowance. The usage dashboard and Codex status surface are the supported places to inspect current allowance/reset information.

5. OpenAI Help — Using Credits for Flexible Usage in ChatGPT (Personal plans)
   https://help.openai.com/en/articles/12642688

   Purchased usage credits are separate from API credits and can apply after included plan allowance is exhausted when supported.

## Finding

There is no official fixed conversion from ChatGPT plan percentage remaining to tokens. Therefore:

```text
PERCENT_REMAINING -> TOKENS
```

must not be invented.

The policy must be unit-aware and provider-native.

## Proposed bootstrap normalized fallback

This is an INTERNAL GOVERNANCE PROPOSAL, not an OpenAI published threshold:

```text
package risk = LOW only
manual trigger only
automatic dispatch = DENIED
automatic package progression = DENIED
P90 planning class <= 40,000 tokens
five-hour remaining >= 80%
weekly remaining >= 80%
fresh evidence <= 10 minutes at reservation
control-plane reserve = 10 percentage points
recovery reserve = 10 percentage points
```

The token cap is a complexity class only; it is not converted into percentage allowance.

After three accepted bounded executions, review actual before/after provider percentage deltas. If one package consumes >20 percentage points of any window, disable the normalized fallback pending review.

## Current disposition

The observed `100% / 98%` would satisfy the proposed percentage thresholds if it were fresh at reservation time. It does NOT authorize dispatch before this policy candidate is independently reviewed and, if accepted, materialized as the active policy.

Next route:

```text
AUTOMATION_QUOTA_NORMALIZED_FALLBACK_RF_RE_REVIEW
```

## Independent Review Fix Applied

Independent narrow review returned `REVIEW_FIX_REQUIRED` with no Master Architecture contradiction and no architecture escalation.

Bounded corrections:

### RF01-01 Reserve arithmetic

`80%` is the only normalized admission floor.

```text
remaining_percent >= 80
```

Control-plane and recovery reserve intent are embedded in that floor. No additional `10 + 10` subtraction is permitted. This removes double-counting ambiguity.

### RF01-02 Applicable-window fail-closed

Each provider window must resolve to one of:

```text
APPLICABLE
NOT_APPLICABLE_WITH_POSITIVE_PROOF
UNKNOWN
```

UI absence does not prove non-applicability. `APPLICABLE` without fresh evidence and `UNKNOWN` both produce `RECHECK_REQUIRED`.

### RF01-03 Reservation-bound freshness

Quota evidence must be captured during the current execution-eligibility attempt and before the single-use reservation. The 10-minute value is only a hard TTL; TTL alone is not sufficient.

Evidence is invalidated by intervening Work/Codex usage, provider reset/window rollover, account/workspace changes, purchased-credit changes, model/executor-profile changes, provider limit-policy changes, or ambiguous/conflicting evidence.

## Re-review disposition

The candidate remains inactive. Active QuotaAdmissionPolicyV1 v1.0 remains frozen. AUTO-IMP-001 remains `AUTHORIZED` but `NOT_EXECUTABLE`.

Next route:

```text
AUTOMATION_QUOTA_NORMALIZED_FALLBACK_RF_RE_REVIEW
```
