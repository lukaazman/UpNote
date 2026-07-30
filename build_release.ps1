$ErrorActionPreference = "Stop"
$version = if ($args.Count -gt 0) { $args[0] } else { "1.0.0" }
$releaseDir = Join-Path $PSScriptRoot "release\UpNote-$version-windows"
if (Test-Path -LiteralPath $releaseDir) { Remove-Item -LiteralPath $releaseDir -Recurse -Force }
New-Item -ItemType Directory -Path $releaseDir | Out-Null
py -3.12 -m PyInstaller --noconfirm --clean --distpath $releaseDir --workpath (Join-Path $PSScriptRoot "build") (Join-Path $PSScriptRoot "UpNote.spec")
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed with exit code $LASTEXITCODE" }
Copy-Item -LiteralPath (Join-Path $PSScriptRoot "README.md") -Destination $releaseDir
$zipPath = Join-Path $PSScriptRoot "release\UpNote-$version-windows.zip"
if (Test-Path -LiteralPath $zipPath) { Remove-Item -LiteralPath $zipPath -Force }
Compress-Archive -Path (Join-Path $releaseDir "*") -DestinationPath $zipPath
Write-Host "Created $zipPath"