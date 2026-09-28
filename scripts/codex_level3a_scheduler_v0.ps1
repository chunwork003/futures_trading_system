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
Write-Host '=== CODEX LEVEL 3A SCHEDULER V0 ===' -ForegroundColor Cyan

git fetch origin master --quiet
$Head = (git rev-parse HEAD).Trim()
$Origin = (git rev-parse origin/master).Trim()

if ($Head -ne $Origin) {
    Write-Host "NOT_DISPATCHABLE - HEAD/origin mismatch" -ForegroundColor Yellow
    Write-Host "HEAD=$Head"
    Write-Host "origin/master=$Origin"
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
$Work = Read-Text 'docs/CURRENT_WORK.md'
$Active = Read-Text 'docs/work/ACTIVE.md'

$RuntimeAuth = Get-Field $Current 'canonical_runtime_authorization'
$SourceAuth = Get-Field $Current 'runtime_source_modification_authorization'
$ReviewerState = Get-Field $Current 'reviewer_state'
$Wave = Get-Field $Current 'current_wave'

if (-not $RuntimeAuth) { $RuntimeAuth = 'UNKNOWN' }
if (-not $SourceAuth) { $SourceAuth = 'UNKNOWN' }
if (-not $ReviewerState) { $ReviewerState = 'UNKNOWN' }
if (-not $Wave) { $Wave = 'UNKNOWN' }

$Status = [ordered]@{
    timestamp = (Get-Date).ToString('o')
    head = $Head
    origin_master = $Origin
    current_wave = $Wave
    reviewer_state = $ReviewerState
    canonical_runtime_authorization = $RuntimeAuth
    runtime_source_modification_authorization = $SourceAuth
    dispatchable = $false
    reason = ''
}

if ($SourceAuth -eq 'NOT_AUTHORIZED' -or $SourceAuth -eq 'UNKNOWN') {
    $Status.reason = 'runtime source modification is not authorized'
}
elseif ($Active -notmatch [regex]::Escape($Head)) {
    $Status.reason = 'ACTIVE does not visibly bind current HEAD'
}
elseif ($Active -match '(?im)^\s*(Runtime Authorization|Runtime Source Modification Authorization)\s*[:：]\s*NOT_AUTHORIZED') {
    $Status.reason = 'ACTIVE contains an explicit not-authorized runtime gate'
}
else {
    $Status.dispatchable = $true
    $Status.reason = 'canonical source authorization and basic repository preflight passed'
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

HEAD = $Head
CURRENT_WAVE = $Wave
REVIEWER_STATE = $ReviewerState
SOURCE_AUTH = $SourceAuth

Authority:
- docs/CURRENT_STATE.md
- docs/work/ACTIVE.md
- exact authorization referenced by ACTIVE
- docs/CODEX_EXECUTION_WORKFLOW.md
- docs/AI_AUTOMATION_OPERATING_MODEL.md

Execute exactly one ACTIVE Work Package.
Search first.
Minimum sufficient read.
Counterexample first for high-risk assertions.
Do not widen write scope.
Do not change architecture semantics.
Obey tests/Git/STOP conditions in ACTIVE.
After commit/push/report: STOP for reviewer.

START.
"@

    [System.IO.File]::WriteAllText(
        (Join-Path (Get-Location) '.tmp\CODEX_NEXT_TASK.txt'),
        $Packet,
        [System.Text.UTF8Encoding]::new($false)
    )

    [System.IO.File]::WriteAllText(
        (Join-Path (Get-Location) '.tmp\CODEX_SCHEDULER_STATUS.json'),
        $Json,
        [System.Text.UTF8Encoding]::new($false)
    )

    Write-Host 'Prepared: .tmp\CODEX_NEXT_TASK.txt'
    Write-Host 'Prepared: .tmp\CODEX_SCHEDULER_STATUS.json'
}

Write-Host ''
Write-Host 'V0 never invokes CODEX automatically.' -ForegroundColor DarkGray
