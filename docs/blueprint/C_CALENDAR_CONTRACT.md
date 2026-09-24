# C — Calendar / Contract

## Status

BUILDING / PROVISIONAL until Blueprint baseline acceptance。

---

## Domain Purpose

提供 trading date、session、holiday、contract lifecycle、listed contract resolution 與 roll/expiry 規則。

主要 current package：

- `trading_calendar/`

Canonical interval：

    [open, close)

Operational timezone interpretation：

    Asia/Taipei

---

## Capability Groups

| Group | Name | Responsibility |
|---|---|---|
| C100 | Trading Calendar | trading date / business day |
| C200 | Trading Session | day/night session 與 interval |
| C300 | Holiday / Exception | holiday、補假、特殊交易日 |
| C400 | Contract Lifecycle | listed contract dates / series |
| C500 | Listed / Continuous Resolution | listed contract / continuous mapping |
| C600 | Expiry / Roll | last trading day、expiry session、roll transition |
| C700 | Calendar / Contract Verification | source consistency / validation |

---

## Engineering Leaves

| ID | Name | Purpose | Lifecycle | Weight | Maps |
|---|---|---|---|---:|---|
| C110 | Trading Date Calendar | 判定合法 trading date | ACCEPTED | 3 | C01 |
| C120 | Business-Day Query | previous / next / valid trading day 查詢 | ACCEPTED | 2 | C01 |
| C130 | Calendar Source Refresh | official calendar source 可更新與驗證 | IMPLEMENTED | 2 | C01,C03 |
| C210 | Session Identity | 定義 day / night 等 session identity | ACCEPTED | 2 | C02 |
| C220 | Session Interval Resolution | timestamp → canonical session interval | ACCEPTED | 3 | C02 |
| C230 | Open-Close Interval Rule | 所有 session 採 `[open, close)` | ACCEPTED | 2 | C02 |
| C240 | Timezone-Aware Inbound Boundary | operational timestamp 禁止 naive time ambiguity | DESIGNED | 4 | C02,C03 |
| C310 | Holiday Calendar | official market holiday 可判定 | IMPLEMENTED | 3 | C03 |
| C320 | One-Off Calendar Exception | 補假／臨時休市等 exception 可表示 | IMPLEMENTED | 3 | C03 |
| C330 | Official Calendar Revalidation | calendar high-change source 需定期 reverify | DESIGNED | 2 | C03 |
| C410 | Contract Date Model | listing / last trade / settlement / month | ACCEPTED | 3 | C04 |
| C420 | Monthly / Quarterly Series | 月契約與季月契約 lifecycle | ACCEPTED | 2 | C04 |
| C430 | Weekly Contract Series | weekly futures/contract series 可表示 | IMPLEMENTED | 3 | C04,C05 |
| C440 | Listed Contract Repository | canonical listed contract lookup | ACCEPTED | 3 | C04 |
| C450 | Contract Generation | 根據規則產生可交易 listed contract set | ACCEPTED | 3 | C04 |
| C510 | Listed Contract Resolution | market date / symbol → listed contract | IMPLEMENTED | 3 | C05 |
| C520 | Continuous Contract Mapping | research continuous series 對 listed contract mapping | IMPLEMENTED | 4 | C05 |
| C530 | Roll Policy | continuous roll transition rule | DESIGNED | 4 | C05 |
| C610 | Last Trading Day | contract last trading date/time rule | IMPLEMENTED | 3 | C04,C05 |
| C620 | Expiry-Day Session Exception | 到期日 session 與一般日不同時需 canonical rule | DESIGNED | 4 | C03,C05 |
| C630 | Roll Transition | old listed → new listed transition 可重現 | DESIGNED | 4 | C05 |
| C710 | Calendar Validation | official source 與 internal calendar consistency | IMPLEMENTED | 2 | C01,C03 |
| C720 | Contract Lifecycle Validation | generated contract date/order/lifecycle validation | ACCEPTED | 2 | C04 |

---

## Connections

| From | To | Contract |
|---|---|---|
| C100 | C200 | valid trading date |
| C200 | D400 | TradingSessionRef |
| C300 | C100/C200 | holiday / exception override |
| C400 | D200 | ContractSpec source |
| C500 | B/F | research listed/continuous contract resolution |
| C600 | D/E/F/G/H | expiry / roll boundary |

---

## External Sources

- SRC-TAIFEX-CALENDAR-001：official trading calendar。
- SRC-TAIFEX-TX-001：TX contract / session / expiry specification。
- SRC-TAIFEX-MTX-001：MTX contract / session / weekly/monthly specification。

Calendar、session、expiry 屬 HIGH / MEDIUM change-risk semantics；不得用 blog 取代 official source。

---

## Current Follow-Up GAP Mapping

- C240 → GAP-07-TIME-001。
- C320/C330 → production calendar completeness。
- C620 → GAP-07-SESSION-EXPIRY。
- session duplication → GAP-07-SESSION-001。
- C520/C530/C630 → Continuous roll follow-up。

---

## Invariants

- Canonical session interval 永遠 `[open, close)`。
- exchange-local interpretation 使用 Asia/Taipei。
- operational timestamps 最終必須 timezone-aware。
- listed contract identity 不等同 continuous symbol。
- expiry-day special rules 不得散落在 strategy / backtest / broker 各自實作。
- official calendar / contract spec change 不得 silent 改 business semantics。

---

## Domain Acceptance

- C01～C05 全部有 leaf mapping。
- trading date / session / contract / roll responsibility 分離。
- official source IDs 完整。
- deferred timezone / expiry / roll work 有明確 leaf 與 GAP。
