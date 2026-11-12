param(
    [string]$GameFolder,
    [switch]$DryRun,
    [switch]$Uninstall
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

function FileHash([string]$Path) {
    $stream = [IO.File]::OpenRead($Path)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($algorithm.ComputeHash($stream)).Replace('-', '').ToLowerInvariant() }
    finally { $stream.Dispose(); $algorithm.Dispose() }
}
function RequireHash([string]$Path, [string]$Expected) {
    if (!(Test-Path -LiteralPath $Path -PathType Leaf) -or (FileHash $Path) -ne $Expected) {
        throw "File does not match the supported version: $Path"
    }
}
function SaveHashes([string]$Root) {
    $result = @{}
    Get-ChildItem -LiteralPath $Root -File -Filter '*.sav' -Recurse | Where-Object {
        !$_.FullName.StartsWith((Join-Path $Root '.retro-trans-backup'), [StringComparison]::OrdinalIgnoreCase)
    } | ForEach-Object { $result[$_.FullName.Substring($Root.Length + 1)] = FileHash $_.FullName }
    return $result
}
function RequireSameSaves($Before, [string]$Root) {
    $after = SaveHashes $Root
    if ($after.Count -ne $Before.Count) { throw 'Save-file list changed; installation stopped.' }
    foreach ($name in $Before.Keys) {
        if (!$after.ContainsKey($name) -or $after[$name] -ne $Before[$name]) { throw "Save changed: $name" }
    }
}
function RequireClosed([string]$Exe) {
    $running = @(Get-Process -Name 'kiwame' -ErrorAction SilentlyContinue | Where-Object {
        $_.Path -and $_.Path.Equals($Exe, [StringComparison]::OrdinalIgnoreCase)
    })
    if ($running.Count) { throw 'Close Apathy Kiwame before applying or undoing this patch.' }
}
function FindGame {
    $candidates = @()
    try {
        $steam = (Get-ItemProperty -LiteralPath 'HKCU:\Software\Valve\Steam').SteamPath
        $libraries = @($steam)
        $vdf = Join-Path $steam 'steamapps\libraryfolders.vdf'
        if (Test-Path -LiteralPath $vdf) {
            foreach ($m in [regex]::Matches([IO.File]::ReadAllText($vdf), '"path"\s+"([^"\r\n]+)"')) {
                $libraries += $m.Groups[1].Value.Replace('\\', '\')
            }
        }
        foreach ($lib in ($libraries | Select-Object -Unique)) {
            $path = Join-Path $lib 'steamapps\common\Apathy_kiwame'
            if (Test-Path -LiteralPath (Join-Path $path 'kiwame.exe')) { $candidates += $path }
        }
    } catch { }
    if ($candidates.Count -eq 1) { return $candidates[0] }
    Add-Type -AssemblyName System.Windows.Forms
    $picker = New-Object System.Windows.Forms.FolderBrowserDialog
    $picker.Description = 'Select your Apathy Kiwame Steam folder (contains kiwame.exe and kiwame.tpatch).'
    if ($picker.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) { throw 'No game folder selected.' }
    return $picker.SelectedPath
}
function AppendFile([string]$Path, [IO.Stream]$Destination) {
    $inputFile = [IO.File]::OpenRead($Path)
    try { $inputFile.CopyTo($Destination, 1048576) } finally { $inputFile.Dispose() }
}

try {
    $manifest = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    if (!$GameFolder) { $GameFolder = FindGame }
    $gameRoot = (Resolve-Path -LiteralPath $GameFolder).Path.TrimEnd('\')
    $gameExe = Join-Path $gameRoot 'kiwame.exe'
    $official = Join-Path $gameRoot 'kiwame.tpatch'
    $markerPath = Join-Path $gameRoot 'kiwame-english-install.json'
    $backup = Join-Path $gameRoot ('.retro-trans-backup\stock-' + $manifest.steam_build)
    if ((Test-Path -LiteralPath (Join-Path $gameRoot 'package.nw'))) {
        throw 'An external package.nw patch is present. Restore the original game layout before using this standalone release. Keep your saves.'
    }
    RequireClosed $gameExe
    RequireHash $official $manifest.source_files.'kiwame.tpatch'.sha256
    $saved = SaveHashes $gameRoot
    if ($Uninstall) {
        if (!(Test-Path -LiteralPath $markerPath)) { throw 'No standalone patch installation record was found.' }
        $installed = Get-Content -LiteralPath $markerPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($installed.layout -ne 'embedded' -or $installed.version -ne $manifest.version) { throw 'Unsupported installed version; no files changed.' }
        RequireHash $gameExe $manifest.target_sha256
        RequireHash (Join-Path $backup 'kiwame.exe') $manifest.source_files.'kiwame.exe'.sha256
        RequireHash (Join-Path $backup 'kiwame.tpatch') $manifest.source_files.'kiwame.tpatch'.sha256
        Write-Host ('Restore original Steam build ' + $manifest.steam_build + '; preserve all current saves.')
    } else {
        if ((FileHash $gameExe) -eq $manifest.target_sha256) {
            Write-Host ('English patch v' + $manifest.version + ' is already installed. No files changed.')
            exit 0
        }
        RequireHash $gameExe $manifest.source_files.'kiwame.exe'.sha256
        if (Test-Path -LiteralPath $markerPath) { throw 'An existing installation record is present; no files changed.' }
        RequireHash (Join-Path $PSScriptRoot $manifest.patch_file) $manifest.patch_sha256
        RequireHash (Join-Path $PSScriptRoot 'xdelta3decode.exe') $manifest.decoder_sha256
        if (Test-Path -LiteralPath $backup) {
            RequireHash (Join-Path $backup 'kiwame.exe') $manifest.source_files.'kiwame.exe'.sha256
            RequireHash (Join-Path $backup 'kiwame.tpatch') $manifest.source_files.'kiwame.tpatch'.sha256
        }
        Write-Host ('Apply English patch v' + $manifest.version + ' to: ' + $gameRoot)
        Write-Host ('Supported Steam build: ' + $manifest.steam_build + '; preserve ' + $saved.Count + ' save files.')
    }
    if ($DryRun) { Write-Host 'Checks passed. Dry run: no files changed.'; exit 0 }
    $drive = New-Object IO.DriveInfo ([IO.Path]::GetPathRoot($gameRoot))
    if ($drive.AvailableFreeSpace -lt 4GB) { throw 'At least 4 GB free disk space is required for staging and backup.' }
    $stage = Join-Path $gameRoot ('.retro-trans-stage-' + [guid]::NewGuid().ToString('N'))
    if ([IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($stage)) -ne $gameRoot) { throw 'Invalid staging path.' }
    New-Item -ItemType Directory -Path $stage | Out-Null
    $nextExe = Join-Path $stage 'next.exe'
    $previousExe = Join-Path $stage 'previous.exe'
    if ($Uninstall) {
        Copy-Item -LiteralPath (Join-Path $backup 'kiwame.exe') -Destination $nextExe
        RequireHash $nextExe $manifest.source_files.'kiwame.exe'.sha256
        $nextHash = $manifest.source_files.'kiwame.exe'.sha256
    } else {
        if (!(Test-Path -LiteralPath $backup)) {
            New-Item -ItemType Directory -Path $backup -Force | Out-Null
            Copy-Item -LiteralPath $gameExe -Destination (Join-Path $backup 'kiwame.exe')
            Copy-Item -LiteralPath $official -Destination (Join-Path $backup 'kiwame.tpatch')
        }
        RequireHash (Join-Path $backup 'kiwame.exe') $manifest.source_files.'kiwame.exe'.sha256
        RequireHash (Join-Path $backup 'kiwame.tpatch') $manifest.source_files.'kiwame.tpatch'.sha256
        $source = Join-Path $stage 'source.bin'
        $stream = [IO.File]::Create($source)
        try { AppendFile $gameExe $stream; AppendFile $official $stream } finally { $stream.Dispose() }
        RequireHash $source $manifest.source_sha256
        & (Join-Path $PSScriptRoot 'xdelta3decode.exe') -d -s $source (Join-Path $PSScriptRoot $manifest.patch_file) $nextExe
        if ($LASTEXITCODE -ne 0) { throw 'Patch decoding failed. The installed game was not changed.' }
        RequireHash $nextExe $manifest.target_sha256
        $nextHash = $manifest.target_sha256
    }
    RequireClosed $gameExe
    RequireSameSaves $saved $gameRoot
    RequireHash $gameExe $(if ($Uninstall) { $manifest.target_sha256 } else { $manifest.source_files.'kiwame.exe'.sha256 })
    RequireHash $official $manifest.source_files.'kiwame.tpatch'.sha256
    # Both moves stay within the checked game/staging roots. Keep an immediate rollback.
    Move-Item -LiteralPath $gameExe -Destination $previousExe
    try {
        Move-Item -LiteralPath $nextExe -Destination $gameExe
        RequireHash $gameExe $nextHash
        RequireSameSaves $saved $gameRoot
        if ($Uninstall) {
            $retiredMarker = Join-Path $stage 'uninstalled-record.json'
            Move-Item -LiteralPath $markerPath -Destination $retiredMarker
        } else {
            $record = [ordered]@{version=$manifest.version;steam_build=$manifest.steam_build;layout='embedded';qa_runtime=$false;backup=$backup;originals=@{'kiwame.exe'=$manifest.source_files.'kiwame.exe'.sha256;'kiwame.tpatch'=$manifest.source_files.'kiwame.tpatch'.sha256};runtime_sha256=$manifest.target_sha256;save_files=$saved;installed=[DateTime]::UtcNow.ToString('o')}
            [IO.File]::WriteAllText($markerPath, ($record | ConvertTo-Json -Depth 8), [Text.UTF8Encoding]::new($false))
        }
    } catch {
        if (Test-Path -LiteralPath $gameExe) { Move-Item -LiteralPath $gameExe -Destination (Join-Path $stage 'failed.exe') }
        Move-Item -LiteralPath $previousExe -Destination $gameExe
        throw
    }
    # Delete only named temporary files; retain the verified original backup.
    Remove-Item -LiteralPath $previousExe -Force
    if (!$Uninstall) { Remove-Item -LiteralPath $source -Force }
    if ($Uninstall) { Remove-Item -LiteralPath (Join-Path $stage 'uninstalled-record.json') -Force }
    Remove-Item -LiteralPath $stage -Force
    Write-Host $(if ($Uninstall) { 'Original game restored. Current saves are unchanged.' } else { 'English patch installed and verified. Saves are unchanged. Launch through Steam normally.' })
} catch {
    Write-Error -Message $_.Exception.Message -ErrorAction Continue
    Write-Host 'No save files were edited. If staging failed, its folder is retained for inspection.'
    exit 1
}
