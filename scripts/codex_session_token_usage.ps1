param(
    [Parameter(Mandatory = $true)]
    [string]$ExecutionId,

    [Parameter(Mandatory = $true)]
    [datetimeoffset]$StartUtc,

    [Parameter(Mandatory = $true)]
    [datetimeoffset]$EndUtc,

    [string]$WorkOrderId = "",

    [string]$CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }),

    [int]$EndSlackSeconds = 120
)

$ErrorActionPreference = "Stop"

function Get-UsageValue {
    param(
        [object]$Usage,
        [string]$Name
    )
    if ($null -eq $Usage) { return [int64]0 }
    $property = $Usage.PSObject.Properties[$Name]
    if ($null -eq $property -or $null -eq $property.Value) { return [int64]0 }
    return [int64]$property.Value
}

function Convert-Usage {
    param([object]$Usage)
    [ordered]@{
        input_tokens            = Get-UsageValue $Usage "input_tokens"
        cached_input_tokens     = Get-UsageValue $Usage "cached_input_tokens"
        output_tokens           = Get-UsageValue $Usage "output_tokens"
        reasoning_output_tokens = Get-UsageValue $Usage "reasoning_output_tokens"
        total_tokens            = Get-UsageValue $Usage "total_tokens"
    }
}

function Subtract-Usage {
    param(
        [hashtable]$End,
        [hashtable]$Start
    )
    [ordered]@{
        input_tokens            = [math]::Max(0, $End.input_tokens - $Start.input_tokens)
        cached_input_tokens     = [math]::Max(0, $End.cached_input_tokens - $Start.cached_input_tokens)
        output_tokens           = [math]::Max(0, $End.output_tokens - $Start.output_tokens)
        reasoning_output_tokens = [math]::Max(0, $End.reasoning_output_tokens - $Start.reasoning_output_tokens)
        total_tokens            = [math]::Max(0, $End.total_tokens - $Start.total_tokens)
    }
}

$start = $StartUtc.ToUniversalTime()
$end = $EndUtc.ToUniversalTime().AddSeconds($EndSlackSeconds)
if ($end -lt $start) {
    throw "EndUtc must be after StartUtc."
}

$roots = @(
    (Join-Path $CodexHome "sessions"),
    (Join-Path $CodexHome "archived_sessions")
) | Where-Object { Test-Path $_ }

if (-not $roots) {
    throw "No Codex session directory found under $CodexHome."
}

# Restrict discovery to the execution date (+/- one day) so we never scan the
# complete Codex history unless the local layout does not expose date folders.
$dates = @(
    $start.UtcDateTime.Date.AddDays(-1),
    $start.UtcDateTime.Date,
    $end.UtcDateTime.Date,
    $end.UtcDateTime.Date.AddDays(1)
) | Select-Object -Unique

$files = New-Object System.Collections.Generic.List[System.IO.FileInfo]
foreach ($root in $roots) {
    $foundDateFolder = $false
    foreach ($date in $dates) {
        $datePath = Join-Path $root ($date.ToString("yyyy\MM\dd"))
        if (Test-Path $datePath) {
            $foundDateFolder = $true
            Get-ChildItem $datePath -Filter "rollout-*.jsonl" -File -ErrorAction SilentlyContinue |
                ForEach-Object { $files.Add($_) }
        }
    }
    if (-not $foundDateFolder) {
        Get-ChildItem $root -Filter "rollout-*.jsonl" -File -Recurse -ErrorAction SilentlyContinue |
            Where-Object {
                $_.LastWriteTimeUtc -ge $start.UtcDateTime.AddHours(-6) -and
                $_.CreationTimeUtc -le $end.UtcDateTime.AddHours(6)
            } |
            ForEach-Object { $files.Add($_) }
    }
}

$files = $files | Sort-Object FullName -Unique
if (-not $files) {
    throw "No candidate rollout JSONL files found near the execution window."
}

$matchTerms = @($ExecutionId)
if ($WorkOrderId) { $matchTerms += $WorkOrderId }

$candidates = foreach ($file in $files) {
    $matched = $false
    foreach ($line in [System.IO.File]::ReadLines($file.FullName)) {
        foreach ($term in $matchTerms) {
            if ($line.Contains($term)) {
                $matched = $true
                break
            }
        }
        if ($matched) { break }
    }
    if ($matched) { $file }
}

if (-not $candidates) {
    throw "No local Codex session contains the supplied execution/work-order identity."
}

$results = foreach ($file in $candidates) {
    $before = $null
    $final = $null
    $tokenEvents = 0
    $firstTokenTimestamp = $null
    $lastTokenTimestamp = $null

    foreach ($line in [System.IO.File]::ReadLines($file.FullName)) {
        if (-not $line.Contains('"token_count"')) { continue }

        try {
            $event = $line | ConvertFrom-Json
        }
        catch {
            continue
        }

        if ($event.type -ne "event_msg" -or $event.payload.type -ne "token_count") {
            continue
        }

        $info = $event.payload.info
        if ($null -eq $info -or $null -eq $info.total_token_usage) {
            continue
        }

        try {
            $timestamp = [datetimeoffset]::Parse($event.timestamp).ToUniversalTime()
        }
        catch {
            continue
        }

        $tokenEvents++
        if ($null -eq $firstTokenTimestamp) { $firstTokenTimestamp = $timestamp }
        $lastTokenTimestamp = $timestamp

        $snapshot = [ordered]@{
            timestamp = $timestamp.ToString("o")
            usage = Convert-Usage $info.total_token_usage
        }

        if ($timestamp -lt $start) {
            $before = $snapshot
        }

        if ($timestamp -ge $start -and $timestamp -le $end) {
            $final = $snapshot
        }
    }

    if ($null -eq $final) {
        continue
    }

    $zero = [ordered]@{
        input_tokens = [int64]0
        cached_input_tokens = [int64]0
        output_tokens = [int64]0
        reasoning_output_tokens = [int64]0
        total_tokens = [int64]0
    }

    $baselineUsage = if ($null -ne $before) { $before.usage } else { $zero }
    $baselineSource = if ($null -ne $before) { "LAST_TOKEN_COUNT_BEFORE_EXECUTION" } else { "ZERO_NO_PRIOR_TOKEN_EVENT" }

    [ordered]@{
        execution_id = $ExecutionId
        work_order_id = $WorkOrderId
        session_file = $file.FullName
        session_id = if ($file.BaseName -match '([0-9a-f]{8}-[0-9a-f-]{27,})$') { $Matches[1] } else { "UNKNOWN" }
        requested_start_utc = $start.ToString("o")
        requested_end_utc = $EndUtc.ToUniversalTime().ToString("o")
        end_slack_seconds = $EndSlackSeconds
        token_event_count_in_session = $tokenEvents
        first_token_event_utc = if ($firstTokenTimestamp) { $firstTokenTimestamp.ToString("o") } else { $null }
        last_token_event_utc = if ($lastTokenTimestamp) { $lastTokenTimestamp.ToString("o") } else { $null }
        baseline_source = $baselineSource
        baseline = if ($before) { $before } else { [ordered]@{ timestamp = $null; usage = $zero } }
        final = $final
        execution_token_delta = Subtract-Usage $final.usage $baselineUsage
        attribution = "EXACT_LOCAL_SESSION_IDENTITY_PLUS_EXECUTION_TIME_WINDOW"
        note = "Metadata only. Raw transcript content is never emitted."
    }
}

if (-not $results) {
    throw "Matching session found, but no token_count event was available in the requested execution window."
}

[ordered]@{
    schema_version = "automation.local_codex_token_usage.v1"
    generated_at_utc = [datetimeoffset]::UtcNow.ToString("o")
    codex_home = $CodexHome
    candidates = @($results)
} | ConvertTo-Json -Depth 20
