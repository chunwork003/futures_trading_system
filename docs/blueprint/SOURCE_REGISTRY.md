# External Source Registry

## 1. Purpose

集中管理：

- exchange rules。
- broker API semantics。
- framework / library official documentation。
- source verification date。
- source authority。
- change risk。

Runtime / architecture 不得因搜尋方便而自行採用未知 secondary source。

---

## 2. Authority Levels

| Tier | Meaning |
|---|---|
| S0 | regulator / exchange authority |
| S1 | official vendor / framework documentation |
| S2 | official source repository |
| S3 | internal ADR / architecture decision |
| S4 | secondary reference |

Broker / exchange / live-money semantics：

S0 / S1 優先。

S4 不得單獨作為 authoritative semantics。

---

## 3. Verification Rule

每個 source-sensitive Work Package：

必須列：

- Source IDs。
- Last Verified。
- 是否需要 revalidation。

以下通常屬 HIGH change risk：

- broker API。
- broker native model。
- exchange margin。
- exchange session / expiry rule。
- authorization / live safety API。
- framework major-version-specific behavior。

---

## 4. Sinopac / Shioaji

| Source ID | Tier | Scope | Host | Path | Change Risk | Last Verified |
|---|---|---|---|---|---|---|
| SRC-SINOPAC-LOGIN-001 | S1 | Login / Account | `sinotrade.github.io` | `/tutor/login/` | HIGH | 2026-09-25 |
| SRC-SINOPAC-CONTRACT-001 | S1 | Contract / product mapping | `sinotrade.github.io` | `/tutor/contract/` | HIGH | 2026-09-25 |
| SRC-SINOPAC-FUT-ORDER-001 | S1 | Futures / options orders | `sinotrade.github.io` | `/tutor/order/FutureOption/` | HIGH | 2026-09-25 |
| SRC-SINOPAC-POSITION-001 | S1 | Account positions | `sinotrade.github.io` | `/tutor/accounting/position/` | HIGH | 2026-09-25 |

### Current Known Usage

GAP-ACCOUNT-001：

- SRC-SINOPAC-LOGIN-001。
- SRC-SINOPAC-POSITION-001。
- SRC-SINOPAC-CONTRACT-001。

GAP-BROKER-001：

- SRC-SINOPAC-FUT-ORDER-001。
- SRC-SINOPAC-CONTRACT-001。

---

## 5. TAIFEX

| Source ID | Tier | Scope | Host | Path | Change Risk | Last Verified |
|---|---|---|---|---|---|---|
| SRC-TAIFEX-TX-001 | S0 | TX contract specification | `taifex.com.tw` | `/enl/eng2/tX` | MEDIUM | 2026-09-25 |
| SRC-TAIFEX-MTX-001 | S0 | MTX contract specification | `taifex.com.tw` | `/enl/eng2/mTX` | MEDIUM | 2026-09-25 |
| SRC-TAIFEX-CALENDAR-001 | S0 | Futures trading calendar | `taifex.com.tw` | `/enl/eng4/calendar` | HIGH | 2026-09-25 |
| SRC-TAIFEX-MARGIN-INDEX-001 | S0 | Index futures/options margin table | `taifex.com.tw` | `/enl/eng5/indexMargining` | HIGH | 2026-09-25 |
| SRC-TAIFEX-MARGIN-RULE-001 | S0 | Futures margin methodology | `taifex.com.tw` | `/enl/eng5/marginReqIndexFut?menuid1=12` | MEDIUM | 2026-09-25 |

Margin：

effective-dated。

不得把 current web value 當永久 constant。

---

## 6. Python / Data Stack

| Source ID | Tier | Scope | Host | Path | Version Policy |
|---|---|---|---|---|---|
| SRC-PYDANTIC-001 | S1 | Model / validation | `docs.pydantic.dev` | `/latest/` | project dependency major must remain v2-compatible |
| SRC-POLARS-001 | S1 | DataFrame / expression / IO | `docs.pola.rs` | `/` | use installed/project-compatible API |
| SRC-DUCKDB-001 | S1 | Analytical SQL / Python API | `duckdb.org` | `/docs/current/` | pin/verify before production-sensitive migration |
| SRC-PYARROW-001 | S1 | Arrow / Parquet Python | `arrow.apache.org` | `/docs/python/` | project-compatible release |
| SRC-PYTEST-001 | S1 | Test framework | `docs.pytest.org` | `/en/stable/` | stable docs |

---

## 7. Persistence / Application / UI

| Source ID | Tier | Scope | Host | Path | Version Policy |
|---|---|---|---|---|---|
| SRC-POSTGRES-001 | S1 | PostgreSQL | `postgresql.org` | `/docs/` | project major must be pinned before implementation |
| SRC-ASPNET-001 | S1 | ASP.NET Core | `learn.microsoft.com` | `/aspnet/core/` | project .NET version must be pinned before scaffold |
| SRC-REACT-LEARN-001 | S1 | React architecture / usage | `react.dev` | `/learn` | project major must be pinned before scaffold |
| SRC-REACT-REF-001 | S1 | React API reference | `react.dev` | `/reference/react` | project major must be pinned before scaffold |

---

## 8. Internal Architecture Sources

| Source ID | Tier | Scope | Path |
|---|---|---|---|
| SRC-ADR-001 | S3 | Trading core boundaries | `docs/adr/ADR-001-TRADING-CORE-BOUNDARIES.md` |
| SRC-ARCH-001 | S3 | System architecture | `docs/ARCHITECTURE.md` |
| SRC-BLUEPRINT-001 | S3 | V1 engineering blueprint | `docs/V1_SYSTEM_BLUEPRINT.md` |

---

## 9. Source Update Rule

若 official source semantics 改變：

1. 不直接 silent 改 runtime。
2. 記錄 source change。
3. 判斷是否影響 architecture / model / adapter。
4. 建立 GAP 或 Work Package。
5. targeted tests。
6. regression。
7. 更新 Last Verified。

如果 source 失效：

標：

    STALE_SOURCE

不得偷偷改用未審核 secondary source。
| SRC-ASPNET-WEBAPI-001 | S1 | ASP.NET Core Web API | `learn.microsoft.com` | `/aspnet/core/web-api/` | project .NET major must be pinned before scaffold |
| SRC-ASPNET-SIGNALR-001 | S1 | ASP.NET Core SignalR | `learn.microsoft.com` | `/aspnet/core/signalr/introduction` | project .NET major must be pinned before scaffold |
| SRC-ASPNET-SECURITY-001 | S1 | ASP.NET Core Security | `learn.microsoft.com` | `/aspnet/core/security/` | project .NET major must be pinned before scaffold |
| SRC-ASPNET-AUTHZ-001 | S1 | ASP.NET Core Authorization | `learn.microsoft.com` | `/aspnet/core/security/authorization/introduction` | project .NET major must be pinned before scaffold |
