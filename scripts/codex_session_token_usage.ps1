param(
    [Parameter(Mandatory = $true)]
    [string]$ExecutionId,

    [Parameter(Mandatory = $true)]
    [datetimeoffset]$StartUtc,

    [Parameter(Mandatory = $true)]
    [datetimeoffset]$EndUtc,

    [string]$WorkOrderId = "",

    [string]$CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }),

    [int]$EndSlackSeconds = 120,

    [int]$CandidateWindowHours = 2,

    [string[]]$StrongMarker = @()
)

$ErrorActionPreference = "Stop"

function Get-SharedTextLines {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $stream = $null
    $reader = $null
    try {
        $share = [System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete
        $stream = [System.IO.File]::Open(
            $Path,
            [System.IO.FileMode]::Open,
            [System.IO.FileAccess]::Read,
            $share
        )
        $reader = New-Object System.IO.StreamReader -ArgumentList $stream
        while (-not $reader.EndOfStream) {
            $reader.ReadLine()
        }
    }
    finally {
        if ($null -ne $reader) {
            $reader.Dispose()
        }
        elseif ($null -ne $stream) {
            $stream.Dispose()
        }
    }
}

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

$windowStart = $start.UtcDateTime.AddHours(-1 * $CandidateWindowHours)
$windowEnd = $end.UtcDateTime.AddHours($CandidateWindowHours)

$files = $files |
    Sort-Object FullName -Unique |
    Where-Object {
        $_.LastWriteTimeUtc -ge $windowStart -and
        $_.CreationTimeUtc -le $windowEnd
    }

if (-not $files) {
    throw "No candidate rollout JSONL files found near the execution window."
}

$matchTerms = @($ExecutionId)
if ($WorkOrderId) { $matchTerms += $WorkOrderId }

$candidates = foreach ($file in $files) {
    $matched = $false
    try {
        foreach ($line in Get-SharedTextLines -Path $file.FullName) {
            foreach ($term in $matchTerms) {
                if ($line.Contains($term)) {
                    $matched = $true
                    break
                }
            }
            if ($matched) { break }
        }
    }
    catch [System.IO.IOException] {
        Write-Warning ("Skipping temporarily unreadable Codex rollout: " + $file.FullName)
        continue
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
    $markerCounts = [ordered]@{}
    foreach ($marker in $StrongMarker) {
        $markerCounts[$marker] = 0
    }

    try {
        foreach ($line in Get-SharedTextLines -Path $file.FullName) {
            foreach ($marker in $StrongMarker) {
                if ($line.Contains($marker)) {
                    $markerCounts[$marker] = [int]$markerCounts[$marker] + 1
                }
            }

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
    }
    catch [System.IO.IOException] {
        Write-Warning ("Skipping temporarily unreadable matching Codex rollout: " + $file.FullName)
        continue
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
        strong_marker_hits = $markerCounts
        strong_marker_all_matched = if ($StrongMarker.Count -eq 0) {
            $null
        } else {
            @($StrongMarker | Where-Object { [int]$markerCounts[$_] -gt 0 }).Count -eq $StrongMarker.Count
        }
        attribution = "LOCAL_SESSION_IDENTITY_PLUS_EXECUTION_TIME_WINDOW"
        note = "Metadata only. Raw transcript content is never emitted."
    }
}

if (-not $results) {
    throw "Matching session found, but no token_count event was available in the requested execution window."
}

$resultArray = @($results)
$strongMatches = if ($StrongMarker.Count -eq 0) {
    @()
} else {
    @($resultArray | Where-Object { $_.strong_marker_all_matched -eq $true })
}

$attributionStatus = if ($StrongMarker.Count -gt 0 -and $strongMatches.Count -eq 1) {
    "EXACT_SINGLE_STRONG_MARKER_MATCH"
}
elseif ($StrongMarker.Count -gt 0 -and $strongMatches.Count -gt 1) {
    "AMBIGUOUS_MULTIPLE_STRONG_MARKER_MATCHES"
}
elseif ($StrongMarker.Count -gt 0 -and $strongMatches.Count -eq 0) {
    "NO_STRONG_MARKER_MATCH"
}
elseif ($resultArray.Count -eq 1) {
    "EXACT_SINGLE_MATCH"
}
else {
    "AMBIGUOUS_MULTIPLE_MATCHES_REVIEW_REQUIRED"
}

[ordered]@{
    schema_version = "automation.local_codex_token_usage.v1"
    generated_at_utc = [datetimeoffset]::UtcNow.ToString("o")
    codex_home = $CodexHome
    candidate_window_hours = $CandidateWindowHours
    candidate_count = $resultArray.Count
    strong_markers = @($StrongMarker)
    strong_match_count = $strongMatches.Count
    attribution_status = $attributionStatus
    exact_candidate_session_id = if ($strongMatches.Count -eq 1) { $strongMatches[0].session_id } else { $null }
    candidates = $resultArray
} | ConvertTo-Json -Depth 20
