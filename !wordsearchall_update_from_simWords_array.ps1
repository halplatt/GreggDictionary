param(
    [switch]$DryRun,
    [switch]$NoBackup
)

$script = Join-Path $PSScriptRoot '!update_wordsearchall_from_array.py'
$wordsFile = Join-Path $PSScriptRoot 'simwords\!words.array.js'
$jsonFile = Join-Path $PSScriptRoot '!wordsearchall.json'

$pyArgs = @($script, '--words-file', $wordsFile, '--json-file', $jsonFile)
if ($DryRun) { $pyArgs += '--dry-run' }
if ($NoBackup) { $pyArgs += '--no-backup' }

python @pyArgs
exit $LASTEXITCODE
