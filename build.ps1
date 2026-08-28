# Packages the add-on into dist\context_search.ankiaddon
# (an .ankiaddon file is just a zip of the add-on folder *contents*)

$ErrorActionPreference = "Stop"

$root    = $PSScriptRoot
$src     = Join-Path $root "context_search"
$dist    = Join-Path $root "dist"
$staging = Join-Path $root "build_tmp"
$zip     = Join-Path $dist "context_search.zip"
$out     = Join-Path $dist "context_search.ankiaddon"

if (-not (Test-Path $src)) { throw "Source folder not found: $src" }

if (Test-Path $staging) { Remove-Item -Recurse -Force $staging }
New-Item -ItemType Directory -Path $staging | Out-Null
if (-not (Test-Path $dist)) { New-Item -ItemType Directory -Path $dist | Out-Null }

# copy everything except caches and the per-user state Anki writes
Get-ChildItem -Path $src -Recurse |
    Where-Object { $_.FullName -notmatch '__pycache__' -and $_.Name -ne 'meta.json' } |
    ForEach-Object {
        $target = Join-Path $staging $_.FullName.Substring($src.Length).TrimStart('\')
        if ($_.PSIsContainer) {
            New-Item -ItemType Directory -Path $target -Force | Out-Null
        } else {
            $parent = Split-Path $target -Parent
            if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
            Copy-Item $_.FullName $target -Force
        }
    }

if (Test-Path $zip) { Remove-Item -Force $zip }
if (Test-Path $out) { Remove-Item -Force $out }

Compress-Archive -Path (Join-Path $staging '*') -DestinationPath $zip -Force
Move-Item $zip $out
Remove-Item -Recurse -Force $staging

Write-Host "Built $out"
