param(
    [ValidateSet('Status','Prepare')]
    [string]$Mode = 'Status'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Read-Text([string]$Path) {
    if (-not (Test-Path $Path)) { throw "missing required file: $Path" }
    return [System.IO.File]::ReadAllText((Resolve-Path $Path))
}

function Get-Field([string]$Text, [string]$Name) {
    $escaped = [regex]::Escape($Name)
    foreach ($pattern in @(
        "(?m)^\s*$escaped\s*=\s*([^\r\n]+)\s*$",
        "(?m)^\s*$escaped\s*[:：]\s*([^\r\n]+)\s*$"
    )) {
        $m = [regex]::Match($Text, $pattern)
        if ($m.Success) { return $m.Groups[1].Value.Trim().Trim('`') }
    }
    return $null
}

Write-Host ''
Write-Host '=== CODEX LEVEL 3A SCHEDULER V2 ===' -ForegroundColor Cyan

git fetch origin master --quiet
$Head = (git rev-parse HEAD).Trim()
$Origin = (git rev-parse origin/master).Trim()

if ($Head -ne $Origin) {
    Write-Host 'NOT_DISPATCHABLE - HEAD/origin mismatch' -ForegroundColor Yellow
    exit 2
}

$Dirty = @(
    git status --porcelain |
    Where-Object {
        $_ -and
        ($_ -notmatch '^\?\? data[/\\]') -and
        ($_ -notmatch '^.. data[/\\]') -and
        ($_ -notmatch '^\?\? \.tmp[/\\]') -and
        ($_ -notmatch '^.. \.tmp[/\\]')
    }
)

if ($Dirty.Count -gt 0) {
    Write-Host 'NOT_DISPATCHABLE - unexpected dirty tree' -ForegroundColor Yellow
    $Dirty | ForEach-Object { Write-Host $_ }
    exit 3
}

$Current = Read-Text 'docs/CURRENT_STATE.md'
$Active = Read-Text 'docs/work/ACTIVE.md'

$CurrentSourceAuth = Get-Field $Current 'runtime_source_modification_authorization'
$ReviewerState = Get-Field $Current 'reviewer_state'
$Wave = Get-Field $Current 'current_wave'

$PackageId = Get-Field $Active 'WORK_PACKAGE_ID'
$PackageStatus = Get-Field $Active 'STATUS'
$Priority = Get-Field $Active 'PRIORITY'
$PlanningBaseline = Get-Field $Active 'PLANNING_BASELINE'
$Authorization = Get-Field $Active 'AUTHORIZATION'
$ActiveSourceAuth = Get-Field $Active 'RUNTIME_SOURCE_AUTH'
$SideEffect = Get-Field $Active 'SIDE_EFFECT_CLASS'
$ReviewBarrier = Get-Field $Active 'REVIEW_BARRIER'
$ToolingMode = Get-Field $Active 'TOOLING_MODE'
$EfficiencyMetrics = Get-Field $Active 'EFFICIENCY_METRICS'

$Missing = @()
foreach ($pair in @(
    @('WORK_PACKAGE_ID',$PackageId),
    @('STATUS',$PackageStatus),
    @('PRIORITY',$Priority),
    @('PLANNING_BASELINE',$PlanningBaseline),
    @('AUTHORIZATION',$Authorization),
    @('RUNTIME_SOURCE_AUTH',$ActiveSourceAuth),
    @('SIDE_EFFECT_CLASS',$SideEffect),
    @('REVIEW_BARRIER',$ReviewBarrier),
    @('TOOLING_MODE',$ToolingMode),
    @('EFFICIENCY_METRICS',$EfficiencyMetrics)
)) {
    if (-not $pair[1]) { $Missing += $pair[0] }
}

$Status = [ordered]@{
    timestamp = (Get-Date).ToString('o')
    head = $Head
    origin_master = $Origin
    current_wave = $Wave
    reviewer_state = $ReviewerState
    package_id = $PackageId
    package_status = $PackageStatus
    priority = $Priority
    planning_baseline = $PlanningBaseline
    authorization = $Authorization
    canonical_source_auth = $CurrentSourceAuth
    active_source_auth = $ActiveSourceAuth
    side_effect_class = $SideEffect
    review_barrier = $ReviewBarrier
    tooling_mode = $ToolingMode
    efficiency_metrics = $EfficiencyMetrics
    dispatchable = $false
    reason = ''
}

if ($Missing.Count -gt 0) {
    $Status.reason = 'missing ACTIVE machine fields: ' + ($Missing -join ',')
}
elseif ($PackageStatus -ne 'READY_FOR_EXECUTION') {
    $Status.reason = 'ACTIVE package is not READY_FOR_EXECUTION'
}
elseif (-not (Test-Path $Authorization)) {
    $Status.reason = 'authorization file does not exist'
}
elseif ($CurrentSourceAuth -ne $ActiveSourceAuth) {
    $Status.reason = 'CURRENT and ACTIVE source authorization mismatch'
}
elseif ($CurrentSourceAuth -eq 'NOT_AUTHORIZED') {
    $Status.reason = 'runtime source modification is not authorized'
}
else {
    git merge-base --is-ancestor $PlanningBaseline $Head
    if ($LASTEXITCODE -ne 0) {
        $Status.reason = 'planning baseline is not an ancestor of current HEAD'
    }
    else {
        $Status.dispatchable = $true
        $Status.reason = 'machine preflight passed'
    }
}

$Json = $Status | ConvertTo-Json -Depth 5
Write-Host $Json

if (-not $Status.dispatchable) {
    Write-Host ''
    Write-Host ('NOT_DISPATCHABLE - ' + $Status.reason) -ForegroundColor Yellow
    exit 4
}

Write-Host ''
Write-Host 'DISPATCHABLE' -ForegroundColor Green

if ($Mode -eq 'Prepare') {
    New-Item -ItemType Directory -Force .tmp | Out-Null

    $Packet = @"
CODEX LEVEL 3A TRANSIENT HANDOFF

PACKAGE = $PackageId
HEAD = $Head
PLANNING_BASELINE = $PlanningBaseline
AUTHORIZATION = $Authorization
SOURCE_AUTH = $ActiveSourceAuth
SIDE_EFFECT_CLASS = $SideEffect
REVIEW_BARRIER = $ReviewBarrier
TOOLING_MODE = $ToolingMode
EFFICIENCY_METRICS = $EfficiencyMetrics

Authority:
1. docs/CURRENT_STATE.md
2. docs/work/ACTIVE.md machine block
3. $Authorization
4. docs/CODEX_EXECUTION_WORKFLOW.md
5. docs/AI_AUTOMATION_OPERATING_MODEL.md

Execute exactly one ACTIVE Work Package.
Counterexample first.
Search before read.
Minimum sufficient context.
Do not widen write scope.
Do not alter frozen architecture semantics.

Tooling:
- Obey TOOLING_MODE before the first edit.
- A known-failing patch route must not be tried before the selected controlled route.
- Report only unexpected failures inside the selected route as tooling retries.

Efficiency:
- Report actual changed-file count/list.
- Report approximate diff additions/deletions.
- Report semantic correction cycles.
- Report tooling retries.
- Report 5HR consumption when available.
- Pytest pass count is verification, not workload.

Use exact test/Git/STOP gates in authorization.
After one runtime commit + push + report: STOP.

START.
"@

    $PacketPath = Join-Path (Get-Location) '.tmp\CODEX_NEXT_TASK.txt'
    $StatusPath = Join-Path (Get-Location) '.tmp\CODEX_SCHEDULER_STATUS.json'

    [System.IO.File]::WriteAllText($PacketPath,$Packet,[System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::WriteAllText($StatusPath,$Json,[System.Text.UTF8Encoding]::new($false))

    Write-Host 'Prepared: .tmp\CODEX_NEXT_TASK.txt'
    Write-Host 'Prepared: .tmp\CODEX_SCHEDULER_STATUS.json'
}

Write-Host ''
Write-Host 'V2 prepares handoff only; it never invokes CODEX automatically.' -ForegroundColor DarkGray
