param(
    [string]$StatusFile = '.tmp\CODEX_SCHEDULER_STATUS.json'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Fail([string]$Message) {
    Write-Host ('FAIL - ' + $Message) -ForegroundColor Red
    throw $Message
}
function Pass([string]$Message) {
    Write-Host ('PASS - ' + $Message) -ForegroundColor Green
}
function Read-Text([string]$Path) {
    if (-not (Test-Path $Path)) { throw "missing file: $Path" }
    return [System.IO.File]::ReadAllText((Resolve-Path $Path)
    )
}
function Get-Field([string]$Text, [string]$Name) {
    $escaped=[regex]::Escape($Name)
    $m=[regex]::Match($Text,"(?m)^\s*$escaped\s*=\s*([^\r\n]+)\s*$")
    if($m.Success){ return $m.Groups[1].Value.Trim().Trim('`') }
    return $null
}

Write-Host ''
Write-Host '=== CODEX LEVEL 3A RESULT INTAKE V1 ===' -ForegroundColor Cyan

if(-not (Test-Path $StatusFile)) {
    Fail "scheduler status missing: $StatusFile ; run scheduler -Mode Prepare before CODEX"
}

$Scheduled=Get-Content -Raw $StatusFile | ConvertFrom-Json
if(-not $Scheduled.dispatchable) { Fail 'scheduled task was not dispatchable' }

$Active=Read-Text 'docs/work/ACTIVE.md'
$Package=Get-Field $Active 'WORK_PACKAGE_ID'
$WriteScope=Get-Field $Active 'WRITE_SCOPE'
$ExpectedMessage=Get-Field $Active 'COMMIT_MESSAGE'

if(-not $Package -or -not $WriteScope) { Fail 'ACTIVE machine fields incomplete' }
if($Package -ne $Scheduled.package_id) { Fail 'ACTIVE package changed after dispatch' }

$Baseline=[string]$Scheduled.head
$Allowed=@($WriteScope.Split(';') | ForEach-Object { $_.Trim() } | Where-Object { $_ } | Sort-Object)

git fetch origin master --quiet
$Head=(git rev-parse HEAD).Trim()
$Origin=(git rev-parse origin/master).Trim()

if($Head -ne $Origin) { Fail 'HEAD/origin mismatch' }
if($Head -eq $Baseline) { Fail 'no runtime commit found after dispatch' }

git merge-base --is-ancestor $Baseline $Head
if($LASTEXITCODE -ne 0) { Fail 'dispatch baseline is not ancestor of runtime head' }

$Count=[int](git rev-list --count ($Baseline+'..'+$Head))
if($Count -ne 1) { Fail "expected exactly one runtime commit; actual=$Count" }
Pass 'one runtime commit'

if($ExpectedMessage) {
    $ActualMessage=(git log -1 --pretty=%s $Head).Trim()
    if($ActualMessage -ne $ExpectedMessage) {
        Fail "commit message mismatch actual=$ActualMessage"
    }
    Pass 'commit message'
} else {
    $ActualMessage=(git log -1 --pretty=%s $Head).Trim()
}

$Changed=@(git diff --name-only $Baseline $Head | Sort-Object)
$Outside=@($Changed | Where-Object { $_ -notin $Allowed })
if($Outside.Count -gt 0) {
    Write-Host 'Outside write scope:'
    $Outside | ForEach-Object { Write-Host ('  '+$_) }
    Fail 'runtime changed files outside ACTIVE WRITE_SCOPE'
}
Pass 'changed files within ACTIVE write scope'

$Unexpected=@(
    git status --porcelain |
    Where-Object {
        $_ -and
        ($_ -notmatch '^\?\? data[/\\]') -and
        ($_ -notmatch '^.. data[/\\]') -and
        ($_ -notmatch '^\?\? \.tmp[/\\]') -and
        ($_ -notmatch '^.. \.tmp[/\\]')
    }
)
if($Unexpected.Count -gt 0) {
    $Unexpected | ForEach-Object { Write-Host $_ }
    Fail 'unexpected working tree'
}
Pass 'working tree'

git diff --check $Baseline $Head
if($LASTEXITCODE -ne 0) { Fail 'git diff --check failed' }
Pass 'diff check'

New-Item -ItemType Directory -Force .tmp | Out-Null

$PacketPath='.tmp\CODEX_REVIEW_PACKET.md'
$JsonPath='.tmp\CODEX_REVIEW_PACKET.json'
$ChangedMd=($Changed | ForEach-Object { '- `'+$_+'`' }) -join "`n"

$Packet=@"
# CODEX Reviewer Intake Packet

Package: `$Package`
Dispatch baseline: `$Baseline`
Runtime candidate: `$Head`
Commit: `$ActualMessage`

Mechanical gates:
- HEAD == origin/master: PASS
- exactly one runtime commit: PASS
- changed files subset of ACTIVE WRITE_SCOPE: PASS
- git diff --check: PASS
- final working tree: clean except known data/.tmp

Changed files:
$ChangedMd

Semantic review remains required.
"@

$Obj=[ordered]@{
    package=$Package
    dispatch_baseline=$Baseline
    runtime_head=$Head
    commit_message=$ActualMessage
    changed_files=$Changed
    allowed_files=$Allowed
    one_commit=$true
    scope_pass=$true
    diff_check=$true
    origin_sync=$true
    semantic_review_required=$true
}

[System.IO.File]::WriteAllText((Join-Path (Get-Location) $PacketPath),$Packet,[System.Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllText((Join-Path (Get-Location) $JsonPath),($Obj|ConvertTo-Json -Depth 6),[System.Text.UTF8Encoding]::new($false))

Write-Host ''
Write-Host 'MECHANICAL_INTAKE_PASS / SEMANTIC_REVIEW_REQUIRED' -ForegroundColor Green
Write-Host "Prepared: $PacketPath"
Write-Host "Prepared: $JsonPath"
Write-Host ''
Write-Host '=== STOP ===' -ForegroundColor Yellow
