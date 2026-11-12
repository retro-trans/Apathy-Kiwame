param(
    [Parameter(Mandatory = $true)][string]$GameFolder,
    [switch]$Stop
)

$ErrorActionPreference = 'Stop'
$folder = (Resolve-Path -LiteralPath $GameFolder).Path
$executable = Join-Path $folder 'kiwame.exe'
$qaScript = Join-Path $folder 'package.nw\debug-runtime.js'
if (!(Test-Path -LiteralPath $qaScript -PathType Leaf)) {
    throw 'Choose an isolated build prepared with --debug.'
}
$instances = @(Get-Process -Name kiwame -ErrorAction SilentlyContinue | Where-Object Path -EQ $executable)
if ($Stop) {
    for ($attempt = 0; $attempt -lt 10; $attempt++) {
        $instances = @(Get-Process -Name kiwame -ErrorAction SilentlyContinue | Where-Object Path -EQ $executable)
        $instances | Stop-Process -ErrorAction SilentlyContinue
        $instances | Wait-Process -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 100
    }
    if (Get-Process -Name kiwame -ErrorAction SilentlyContinue | Where-Object Path -EQ $executable) {
        throw 'The isolated QA copy did not stop.'
    }
    return
}
if ($instances) { throw 'This QA copy is already running.' }
$port = if ($env:KIWAME_QA_PORT) { [int]$env:KIWAME_QA_PORT } else { 9229 }
if ($port -lt 1024 -or $port -gt 65535) { throw 'Invalid QA port.' }
$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $port)
try { $listener.Start() } finally { $listener.Stop() }
$profile = Join-Path $folder 'qa-profile'
$previousAudioMute = $env:KIWAME_QA_AUDIO_MUTE
try {
$env:KIWAME_QA_AUDIO_MUTE = '1'
Start-Process -FilePath $executable -WorkingDirectory $folder -WindowStyle Hidden -PassThru -ArgumentList @(
    "--remote-debugging-port=$port",
    '--remote-debugging-address=127.0.0.1',
    "--user-data-dir=`"$profile`"",
    '--mute-audio'
) | Select-Object Id, Path
} finally {
    $env:KIWAME_QA_AUDIO_MUTE = $previousAudioMute
}
