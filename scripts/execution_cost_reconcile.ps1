param(
    [Parameter(Mandatory = $true)]
    [string]$ForecastPath,

    [Parameter(Mandatory = $true)]
    [string]$ActualPath,

    [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"

function Read-JsonFile {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        throw "File not found: $Path"
    }
    return Get-Content $Path -Raw -Encoding UTF8 | ConvertFrom-Json
}

function Get-SeverityRank {
    param([string]$Name)
    switch ($Name) {
        "NORMAL" { return 0 }
        "WATCH" { return 1 }
        "HIGH" { return 2 }
        "CRITICAL" { return 3 }
        default { return -1 }
    }
}

function Compare-BandedMetric {
    param(
        [string]$Name,
        [double]$Actual,
        [object]$Band
    )

    $p50 = [double]$Band.p50
    $p75 = [double]$Band.p75
    $p90 = [double]$Band.p90

    $classification = if ($Actual -le $p75) {
        "NORMAL"
    }
    elseif ($Actual -le $p90) {
        "WATCH"
    }
    elseif ($Actual -le (1.25 * $p90)) {
        "HIGH"
    }
    else {
        "CRITICAL"
    }

    $p50Ratio = if ($p50 -gt 0) { $Actual / $p50 } else { $null }
    $p90Ratio = if ($p90 -gt 0) { $Actual / $p90 } else { $null }
    $ape = if ($p50 -gt 0) { [math]::Abs($Actual - $p50) / $p50 } else { $null }

    return [ordered]@{
        metric = $Name
        actual = $Actual
        p50 = $p50
        p75 = $p75
        p90 = $p90
        actual_to_p50_ratio = $p50Ratio
        actual_to_p90_ratio = $p90Ratio
        p50_absolute_percentage_error = $ape
        classification = $classification
    }
}

$forecast = Read-JsonFile $ForecastPath
$actual = Read-JsonFile $ActualPath

if ($forecast.schema_version -ne "automation.execution_cost_forecast.v1") {
    throw "Unsupported forecast schema: $($forecast.schema_version)"
}
if ($actual.schema_version -ne "automation.execution_cost_actual.v1") {
    throw "Unsupported actual schema: $($actual.schema_version)"
}

$comparisons = New-Object System.Collections.Generic.List[object]

$metricMap = @(
    @("reported_total_tokens", "reported_total_tokens"),
    @("uncached_input_tokens", "uncached_input_tokens"),
    @("output_tokens", "output_tokens"),
    @("reasoning_output_tokens", "reasoning_output_tokens"),
    @("five_hour_delta_pct", "five_hour_delta_pct"),
    @("weekly_delta_pct", "weekly_delta_pct"),
    @("actor_seconds", "actor_seconds")
)

foreach ($pair in $metricMap) {
    $forecastName = $pair[0]
    $actualName = $pair[1]
    $band = $forecast.forecast.PSObject.Properties[$forecastName].Value
    $value = $actual.actual.PSObject.Properties[$actualName].Value

    if ($null -eq $band -or $null -eq $value) { continue }
    if ($value -is [string]) { continue }
    if ($null -eq $band.p50 -or $null -eq $band.p75 -or $null -eq $band.p90) { continue }

    $comparisons.Add((Compare-BandedMetric -Name $actualName -Actual ([double]$value) -Band $band))
}

# Test-runtime metrics currently forecast only p90. They can still produce a direct p90 breach signal.
foreach ($name in @("targeted_seconds", "full_regression_seconds")) {
    $band = $forecast.forecast.PSObject.Properties[$name].Value
    $value = $actual.actual.PSObject.Properties[$name].Value
    if ($null -eq $band -or $null -eq $value -or $value -is [string] -or $null -eq $band.p90) { continue }

    $classification = if ([double]$value -le [double]$band.p90) { "NORMAL" } else { "HIGH" }
    $comparisons.Add([ordered]@{
        metric = $name
        actual = [double]$value
        p50 = $null
        p75 = $null
        p90 = [double]$band.p90
        actual_to_p50_ratio = $null
        actual_to_p90_ratio = if ([double]$band.p90 -gt 0) { [double]$value / [double]$band.p90 } else { $null }
        p50_absolute_percentage_error = $null
        classification = $classification
    })
}

$cyclePlan = $forecast.forecast.test_cycles
$cycleActual = $actual.actual.test_cycles
$cycleBreaches = New-Object System.Collections.Generic.List[string]

if ($null -ne $cyclePlan -and $null -ne $cycleActual) {
    if ([int]$cycleActual.pre_fix_cases -gt [int]$cyclePlan.pre_fix_cases_max) {
        $cycleBreaches.Add("PRE_FIX_CASES_OVER_PLAN")
    }
    if ([int]$cycleActual.complete_targeted_passes -gt [int]$cyclePlan.complete_targeted_passes_max) {
        $cycleBreaches.Add("TARGETED_PASSES_OVER_PLAN")
    }
    if ([int]$cycleActual.full_regression_passes -gt [int]$cyclePlan.full_regression_passes_max) {
        $cycleBreaches.Add("FULL_REGRESSION_PASSES_OVER_PLAN")
    }
}

$overall = "NORMAL"
foreach ($item in $comparisons) {
    if ((Get-SeverityRank $item.classification) -gt (Get-SeverityRank $overall)) {
        $overall = $item.classification
    }
}
if ($cycleBreaches.Count -gt 0 -and (Get-SeverityRank $overall) -lt (Get-SeverityRank "HIGH")) {
    $overall = "HIGH"
}

$cause = "WITHIN_EXPECTED_ENVELOPE"
$recommendations = New-Object System.Collections.Generic.List[string]

function Test-NumericMetric {
    param([object]$Value)

    if ($null -eq $Value) {
        return $false
    }

    [double]$parsed = 0
    return [double]::TryParse(
        [string]$Value,
        [System.Globalization.NumberStyles]::Any,
        [System.Globalization.CultureInfo]::InvariantCulture,
        [ref]$parsed
    )
}

$actualTotal = $actual.actual.reported_total_tokens
$actualUncached = $actual.actual.uncached_input_tokens
$cacheRatio = $actual.actual.cached_input_ratio
$totalP90 = $forecast.forecast.reported_total_tokens.p90
$uncachedP90 = $forecast.forecast.uncached_input_tokens.p90
$fiveHour = $actual.actual.five_hour_delta_pct
$fiveHourP90 = $forecast.forecast.five_hour_delta_pct.p90

$hasActualTotal = Test-NumericMetric $actualTotal
$hasActualUncached = Test-NumericMetric $actualUncached
$hasCacheRatio = Test-NumericMetric $cacheRatio
$hasTotalP90 = Test-NumericMetric $totalP90
$hasUncachedP90 = Test-NumericMetric $uncachedP90
$hasFiveHour = Test-NumericMetric $fiveHour
$hasFiveHourP90 = Test-NumericMetric $fiveHourP90

if (
    $hasActualTotal -and
    $hasActualUncached -and
    $hasCacheRatio -and
    $hasTotalP90 -and
    $hasUncachedP90 -and
    (([double]$actualTotal) -gt ([double]$totalP90)) -and
    (([double]$cacheRatio) -ge 0.90) -and
    (([double]$actualUncached) -le ([double]$uncachedP90))
) {
    $cause = "CONTEXT_REPLAY_DOMINATED"
    $recommendations.Add("REDUCE_MODEL_TOOL_TEST_ROUND_TRIPS")
    $recommendations.Add("KEEP_STABLE_CACHE_FRIENDLY_KERNEL")
    $recommendations.Add("DO_NOT_RELOAD_UNCHANGED_CONTEXT")
}
elseif (
    $hasActualUncached -and
    $hasUncachedP90 -and
    (([double]$actualUncached) -gt ([double]$uncachedP90))
) {
    $cause = "FRESH_CONTEXT_GROWTH"
    $recommendations.Add("TIGHTEN_POINTER_FIRST_CONTEXT")
    $recommendations.Add("REMOVE_UNRELATED_HISTORY")
    $recommendations.Add("SPLIT_OVERSIZED_WORK_ORDER")
}
elseif ($cycleBreaches.Count -gt 0) {
    $cause = "TEST_EXECUTION_DOMINATED"
    $recommendations.Add("MINIMUM_COUNTEREXAMPLE_BEFORE_FIX")
    $recommendations.Add("IMPACTED_SUBSET_UNTIL_CLEAN")
    $recommendations.Add("NO_EXTRA_FULL_SUITE_WITHOUT_NEW_DELTA")
}
elseif (
    $hasFiveHour -and
    $hasFiveHourP90 -and
    (([double]$fiveHour) -gt ([double]$fiveHourP90)) -and
    (($overall -eq "NORMAL") -or ($overall -eq "WATCH"))
) {
    $cause = "PROVIDER_OR_SHARED_WINDOW_ANOMALY"
    $recommendations.Add("CHECK_RESET_WINDOW_AND_COMPETING_CONSUMERS")
    $recommendations.Add("PRESERVE_RAW_QUOTA_SNAPSHOTS")
}
# Provider 中斷是 capacity/forecast feedback，不自動判定 source defect。
# 舊 actual 不含欄位時保持原有 reconciliation；新欄位只附加原始觀察。
$interruption = [ordered]@{}
foreach ($name in @('provider_limit_encountered', 'provider_pause_count', 'provider_pause_seconds',
    'resume_count', 'resumed_same_execution', 'capacity_forecast_at_start',
    'capacity_estimate_at_start', 'forecast_capacity_review_required')) {
    $property = $actual.actual.PSObject.Properties[$name]
    if ($null -ne $property) { $interruption[$name] = $property.Value }
}
$capacityReviewRequired = ($interruption.provider_limit_encountered -eq $true) -or
    ($interruption.forecast_capacity_review_required -eq $true) -or
    ($interruption.provider_pause_count -gt 0)
if ($capacityReviewRequired) {
    $recommendations.Add('WORK_FORECAST_CAPACITY_REVIEW_PRESERVE_SAME_EXECUTION')
}
$result = [ordered]@{
    schema_version = "automation.execution_cost_reconciliation.v1"
    forecast_path = $ForecastPath
    actual_path = $ActualPath
    work_order_id = $actual.work_order_id
    execution_id = $actual.execution_id
    forecast_confidence = $forecast.confidence
    overall_classification = $overall
    dominant_cause = $cause
    metric_comparisons = $comparisons.ToArray()
    cycle_breaches = $cycleBreaches.ToArray()
    recommendations = $recommendations.ToArray()
    feedback_required_for_next_work_forecast = (($overall -ne "NORMAL") -or $capacityReviewRequired)
    provider_interruption = $interruption
    forecast_capacity_review_required = $capacityReviewRequired
    provider_pause_is_source_defect = $false
    generated_at_utc = [datetimeoffset]::UtcNow.ToString("o")
}

$json = $result | ConvertTo-Json -Depth 20
if ($OutputPath) {
    $parent = Split-Path -Parent $OutputPath
    if ($parent -and -not (Test-Path $parent)) {
        New-Item $parent -ItemType Directory -Force | Out-Null
    }
    Set-Content -Path $OutputPath -Value $json -Encoding UTF8
}

$json
