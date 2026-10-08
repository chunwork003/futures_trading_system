# P02 Application Build / Test-host — 候選契約

狀態：DEFINED_CANDIDATE / NOT_ACCEPTED。P02 建立 Python HTTP → ASP.NET BFF → React 契約工作台；不是 durable research 完成，也不能 credit J1/J2。API shape owner 仍是 scripts/p00_build_contracts.py，登入語意沿用 V1_GENESIS_AUTH_CONTRACT.md。

## 建置矩陣與 lock ownership

2026-10-09 以官方資料核對後選定以下候選工具鏈；不是本機已安裝／已建置聲明。

| 層 | 固定候選 profile | 產物與驗收 |
|---|---|---|
| Python service | CPython 3.14.8、標準 GIL、x64 | service optional extra；保留 library requires-python >=3.11，不宣稱所有版本 service 相容 |
| BFF | .NET SDK 10.0.401、net10.0、ASP.NET runtime 10.0.12 | global.json exact SDK、rollForward=disable；NuGet locked restore |
| Web builder | Node 24.21.0；npm 使用該 official distribution 所附版本並記錄 exact version | package-lock + npm ci；不使用 floating create-vite@latest |
| Browser | Playwright 的 Chromium，revision 由 exact Playwright package 綁定 | browser binary revision/OS/hash 記錄；不拿使用者瀏覽器代替 fixture runner |
| 必要平台 | Windows x64 development；Linux x64 glibc build/test | 兩平台獨立 lock/wheel/integration evidence；不宣稱 ARM/macOS/Alpine 通過 |

新 direct dependency 家族：Python FastAPI 0.x、Uvicorn 0.x、Pydantic 2.x；HTTP 測試 httpx 0.x/pytest 9.x。Web React/ReactDOM 19.x、TypeScript 5.x、Vite 7.x、相容 @vitejs/plugin-react、@types/react、@types/react-dom、@playwright/test。BFF 使用 SDK shared framework，不另引入替代 auth 框架；測試使用 Microsoft.AspNetCore.Mvc.Testing 10.0.12、Microsoft.NET.Test.Sdk 與 xUnit stable。相依版本須符合 peer/runtime 約束，不能用 --force 或忽略 peer conflict。

P02 首次 authorized implementation 的 dependency compile 是建置工作：在這些家族內從 pypi.org、registry.npmjs.org、api.nuget.org 取得非 prerelease/non-yanked stable 候選，依當次 registry snapshot 選最高相容版本，保存解析時間、來源、完整 transitive exact versions/hashes。既有 quant 套件不為了 service 隨意升版；保持原已驗證集合優先，無可相容集合時回報 dependency conflict。重播只能使用鎖檔，不能每次重新找 latest。此政策定義選版規則；尚未解析的 exact package hashes 不填假值。

候選 allowlist 加入 .python-version、.node-version、global.json、requirements/service.in、requirements/service-win.lock、requirements/service-linux.lock、requirements/build-tools.lock、application/packages.lock.json、tests/application/packages.lock.json 與 test-host 自己的 lock。Python hash-locked install 在乾淨 venv，以 --require-hashes；本 repository package 使用 --no-deps 安裝，不重新解析 dependencies。NuGet restore --locked-mode；npm ci。Build tool 本身也鎖版本。首次 compile可寫 lock，之後測試不得隱式修改 lock。BUILD_RESOLUTION.json 保存工具版本、registry/lock hashes、platform、命令與結果，不含 secrets。

P02 不建立 production container image；P11 owns image digest、非 root runtime、憑證／volume／部署與 clean-machine install。P02 必須在上述兩種 native build lanes 證明 source/locks 可重播；P11 image只能消費已測 locks。不存在的 image digest 不編造，container conformance 不作為 P02 之前的循環 gate。

## Production factory 與 test-host 隔離

Python `create_app(settings, ports)` 不自行選取 fake provider。Production entrypoint 只註冊正式 port adapters；缺 durable research adapter 時 /health 的 process liveness可用，但 readiness degraded，authenticated domain calls回503 DEPENDENCY_UNAVAILABLE，絕不回假的 QUEUED/SUCCEEDED。未驗證身份仍先401/403，不透露 provider 細節。全域 dependency_overrides 不留在 production module。

測試 fixture provider、fixture repository、clock、injector 放 tests/service/ 與 tests/application/；production source不得 import tests，也不得認得 TEST_MODE、mock=true、fixture header等切換方式。Python 測試以 factory argument／測試生命週期 dependency override 注入，finally 清理；每個案例獨立 state。

ASP.NET 仍使用真正 Identity password hasher、cookie handler、antiforgery、Origin validation、session middleware。In-memory test user/session stores與 fake clock 只能由 WebApplicationFactory／獨立 tests/application/TestHost/TestHost.csproj 的 composition root 注入；不使用「永遠已登入」authentication handler來通過 U01/U04。Production assembly不得參考 test assembly，不透過 reflection/plugin scanning載入任意身份provider。

Browser suite由 tests/browser 的 supervisor啟動 test-only Python host與 test-only BFF host，loopback ephemeral ports、每run獨立 HTTPS test certificate/key/fixture credentials、private temporary directory。瀏覽器信任限定該run憑證；不關閉 TLS verification，不以 ignoreHTTPSErrors=true 通關。Origin 必須與實際 test-host origin精確一致。Production使用原定 HTTPS localhost:7443；測試port覆寫由 test composition root傳入，不改正式 default。Cleanup失敗回報且不得刪除非該run目錄。

正式 publish artifact 必須排除 tests、fixture secrets、test-host assemblies/entrypoints。測試另執行普通啟動 binary，注入惡意 TEST_MODE/header後仍不得載入 fixture；以 process/package依賴檢查佐證，不能只 grep 類名。Harness顯示明顯 TEST FIXTURE標示，不能出現在production response DTO中；正式schema不新增 test_mode authority欄位。

## Identity / provider ownership 與交接

P02只驗證真middleware搭配test stores的身份路徑。正式 user/session repository、持久化 key ring、bootstrap operator、restart/revocation durability由 P03一起整合 application-owned PostgreSQL schema；P11完成安裝與備份環境。這使 P04 durable research UI 不必等到最後才有可用登入。N owns identity/session，M owns research operation，兩者同機部署不共享 domain state authority。

BFF每次請求重新驗證session與permission，移除caller actor/role/servicecredential headers；只向固定configured Python base URI傳server credential及trusted subject。URI不得由browser指定；redirect不自動轉送credential。Python只接受內部credential與合法actor context，cookies不能替代service auth。登入/登出、timeout、CSRF、鎖定門檻沿用已定義契約；測試失敗不得弱化正式路徑。

`ResearchPort` 方法只接收已驗證command/actor/envelope並回schema定義的receipt/operation/results；`IdentityStorePort` 負責user lookup、password metadata、session lookup/revoke及security stamp。BFF沒有第二個job queue，不在UI/BFF重新算 quant/risk，不在fake provider模擬真canonical READY。

## U01-U08 與 build acceptance

U01：fixture dataset/strategy→submit同key→poll→result，重送同receipt；U02：clock跨過idle/absolute expiry→401→UI login且保存operation ID；U03：ordinary start缺durable provider→503/degraded；U04：login缺CSRF／錯Origin／spoof actor拒絕；U05：Python cookie-only拒絕；U06：ordinary artifact無test host且切換輸入無效；U07：mutation timeout→保留key/revision，先查receipt，不產生新command；U08：LIVE/BROKER_PAPER在server拒絕。

每個驗收需Python/BFF/browser分層 evidence；測試替身PASS不能算real PG、real trading或release journeyPASS。P02 real builds與fixtures是implementation acceptance，不要求在authoring前執行。若本機缺SDK/browser，不安裝到未授權全域環境；使用已授權isolated環境或記錄該lane未驗證，不以schema tests代替。

## 官方來源與查核界線

查核日期：2026-10-09。以下支援版本選擇與工具機制，未證明本repo整合相容。

- [Python releases](https://www.python.org/downloads/)：3.14.8 release listing。
- [.NET 10 downloads](https://dotnet.microsoft.com/en-us/download/dotnet/10.0)：SDK10.0.401與runtime10.0.12。
- [Node download](https://nodejs.org/en/download)：24.21.0 LTS。
- [Vite guide](https://vite.dev/guide/)：Node requirements；選擇Vite7家族為本專案候選，不宣稱它是最新major。
- [ASP.NET integration tests](https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests?view=aspnetcore-10.0)：test-host與WebApplicationFactory。
- [FastAPI dependency overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/)：test override機制；隔離規則由本專案另行約束。

Python package discovery須把 service* 納入，保留原量化package列表；production wheel不得包含tests。TestHost獨立子目錄／csproj／packages.lock.json，避免與Workspace.ContractTests共用預設lock檔而互相覆寫。
