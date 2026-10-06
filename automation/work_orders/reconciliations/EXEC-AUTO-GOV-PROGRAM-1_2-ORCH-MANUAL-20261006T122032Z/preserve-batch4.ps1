[CmdletBinding()]
param([switch]$ConfirmNoActiveExecutor,[switch]$RestoreTracked)
$ErrorActionPreference='Stop'
if(-not $ConfirmNoActiveExecutor){throw 'STOP: active executor quiescence must be established before checkpoint/cleanup'}
$base='52f0b5da1d050a8876f9716b227055219f4fd070'
$scope=@('automation/prompts/CODEX_EXECUTOR_KERNEL.md','automation/prompts/WORK_ORCHESTRATOR_KERNEL.md','automation/skills/execution-cost-forecaster/SKILL.md','automation/skills/repo-reentry/SKILL.md','automation/skills/single-use-lifecycle-guard/SKILL.md','automation/specs/context_loading_policy.v1.yaml','scripts/execution_cost_reconcile.ps1','tests/automation/test_execution_cost_reconcile.py')
function Invoke-GitChecked { param([string[]]$Arguments)
  $gitArguments=@($Arguments)+@($args)
  $result=& git @gitArguments
  if($LASTEXITCODE -ne 0){throw ('git failed: '+($Arguments -join ' '))}
  return $result
}
$root=(Get-Location).ProviderPath
if((Invoke-GitChecked @('rev-parse','--show-prefix'))){throw 'STOP_RUN_FROM_REPOSITORY_ROOT'}
$head=(Invoke-GitChecked @('rev-parse','HEAD')).Trim()
$branch=(Invoke-GitChecked @('branch','--show-current')).Trim()
if($head -ne $base -or $branch -ne 'manual/WO-AUTO-GOV-PROGRAM-1_2-ORCH-01-REV5'){throw 'STOP_SOURCE_HEAD_OR_BRANCH_DRIFT'}
Invoke-GitChecked @('fetch','origin','master','manual/WO-AUTO-GOV-PROGRAM-1_2-ORCH-01-REV5') | Out-Null
if((Invoke-GitChecked @('rev-parse','origin/manual/WO-AUTO-GOV-PROGRAM-1_2-ORCH-01-REV5')).Trim() -ne $base){throw 'STOP_REMOTE_BRANCH_DRIFT'}
$changed=@(Invoke-GitChecked @('diff','--name-only','HEAD','--'))
if(@($changed | Where-Object {$_ -notin $scope}).Count){throw 'STOP_UNEXPECTED_TRACKED_DELTA'}
$untracked=@(Invoke-GitChecked @('ls-files','--others','--exclude-standard'))
$unexpected=@($untracked | Where-Object {$_ -notin $scope -and $_ -notlike 'data/*' -and $_ -notlike '.tmp/*'})
if($unexpected.Count){throw 'STOP_UNEXPECTED_UNTRACKED_DELTA'}
$stamp=(Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfffZ')
$dir=Join-Path $root ('.tmp/reconciliation-'+$stamp)
New-Item -ItemType Directory -Path $dir | Out-Null
$patch=Join-Path $dir 'Batch4.checkpoint.patch'
$savedIndex=$env:GIT_INDEX_FILE
$idx=Join-Path $dir 'snapshot.index'
$testIdx=Join-Path $dir 'verify.index'
try {
  $env:GIT_INDEX_FILE=$idx
  Invoke-GitChecked @('read-tree',$base) | Out-Null
  Invoke-GitChecked (@('add','--')+$scope) | Out-Null
  $actual=@(Invoke-GitChecked @('diff','--cached','--name-only',$base,'--'))
  if(@($actual | Where-Object {$_ -notin $scope}).Count -or $actual.Count -ne 8){throw 'STOP_EXPECTED_EXACT_EIGHT_FILE_CHECKPOINT'}
  # Git writes raw patch bytes directly; PS5.1 output redirection must not re-encode them.
  Invoke-GitChecked (@('diff','--cached','--binary','--full-index','--no-ext-diff','--output='+$patch,$base,'--')+$scope) | Out-Null
  $snapshotTree=(Invoke-GitChecked @('write-tree')).Trim()
  $env:GIT_INDEX_FILE=$testIdx
  Invoke-GitChecked @('read-tree',$base) | Out-Null
  Invoke-GitChecked @('apply','--check','--cached',$patch) | Out-Null
  Invoke-GitChecked @('apply','--cached',$patch) | Out-Null
  $reconstructedTree=(Invoke-GitChecked @('write-tree')).Trim()
  if($snapshotTree -ne $reconstructedTree){throw 'STOP_CHECKPOINT_RECONSTRUCTION_MISMATCH'}
} finally {
  if($null -eq $savedIndex){Remove-Item Env:GIT_INDEX_FILE -ErrorAction SilentlyContinue}
  else {$env:GIT_INDEX_FILE=$savedIndex}
}
$files=@()
foreach($p in $scope) {
  $file=Join-Path $root $p
  if(-not (Test-Path -LiteralPath $file -PathType Leaf)){throw ('STOP_MISSING_FILE '+$p)}
  $files+=@{path=$p;sha256=(Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant();bytes=(Get-Item -LiteralPath $file).Length}
}
$meta=@{schema_version='automation.checkpoint_evidence.v1';execution_id='EXEC-AUTO-GOV-PROGRAM-1_2-ORCH-MANUAL-20261006T122032Z';work_order_id='WO-AUTO-GOV-PROGRAM-1_2-ORCH-01';source_head=$base;patch_sha256=(Get-FileHash -LiteralPath $patch -Algorithm SHA256).Hash.ToLowerInvariant();patch_bytes=(Get-Item -LiteralPath $patch).Length;snapshot_tree=$snapshotTree;reconstructed_tree=$reconstructedTree;exact_scope=$scope;files=$files;checkpoint_validation='PASS';executor_quiescence='OPERATOR_ATTESTED';measurement='DETERMINISTIC_LOCAL_CHECKPOINT';created_at=(Get-Date).ToUniversalTime().ToString('o');cleanup_performed=$false}
$utf8=New-Object System.Text.UTF8Encoding($false)
if($RestoreTracked) {
  # No source fix. Only exact verified tracked restoration, no reset --hard or git clean.
  $tracked=@(Invoke-GitChecked (@('ls-files','--')+$scope))
  Invoke-GitChecked (@('restore','--source='+$base,'--staged','--worktree','--')+$tracked) | Out-Null
  $new='tests/automation/test_execution_cost_reconcile.py'
  if($new -notin $tracked) {
    $from=Join-Path $root $new
    $to=Join-Path $dir 'untracked-test-original.py'
    Move-Item -LiteralPath $from -Destination $to
    if((Get-FileHash -LiteralPath $to -Algorithm SHA256).Hash.ToLowerInvariant() -ne ($files | Where-Object {$_.path -eq $new}).sha256){throw 'STOP_UNTRACKED_BACKUP_HASH'}
  }
  if(@(Invoke-GitChecked @('diff','--name-only','HEAD','--')).Count){throw 'STOP_TRACKED_NOT_CLEAN'}
  $meta.cleanup_performed=$true
  $meta.tracked_restored_to=$base
}
[IO.File]::WriteAllText((Join-Path $dir 'Batch4.checkpoint.json'),($meta | ConvertTo-Json -Depth 20),$utf8)
Write-Output ('CHECKPOINT_DIRECTORY='+$dir)
Write-Output ('PATCH_SHA256='+$meta.patch_sha256)
Write-Output ('TRACKED_CLEAN='+$meta.cleanup_performed)
Write-Output 'STOP: publish checkpoint.patch + checkpoint.json as control-plane evidence; WORK must bind hashes/release old writer before any new lifecycle.'
