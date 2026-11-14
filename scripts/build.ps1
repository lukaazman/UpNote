$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$version = if ($args.Count -gt 0) { $args[0] } else { "1.1.0" }
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    py -3.12 -m venv (Join-Path $root ".venv")
    & $python -m pip install -r (Join-Path $root "requirements.txt")
    if ($LASTEXITCODE -ne 0) { throw "pip install failed with exit code $LASTEXITCODE" }
}
$releaseDir = Join-Path $root "release\UpNote-$version-windows"
if (Test-Path -LiteralPath $releaseDir) { Remove-Item -LiteralPath $releaseDir -Recurse -Force }
New-Item -ItemType Directory -Path $releaseDir | Out-Null
& $python -m PyInstaller --noconfirm --clean --distpath $releaseDir --workpath (Join-Path $root "build") (Join-Path $PSScriptRoot "UpNote.spec")
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed with exit code $LASTEXITCODE" }
Copy-Item -LiteralPath (Join-Path $root "README.md") -Destination $releaseDir
$zipPath = Join-Path $root "release\UpNote-$version-windows.zip"
if (Test-Path -LiteralPath $zipPath) { Remove-Item -LiteralPath $zipPath -Force }
Compress-Archive -Path (Join-Path $releaseDir "*") -DestinationPath $zipPath
$exe = Get-Item (Join-Path $releaseDir "UpNote.exe")
Write-Host ("Created {0} (UpNote.exe {1:N1} MB)" -f $zipPath, ($exe.Length / 1MB))
