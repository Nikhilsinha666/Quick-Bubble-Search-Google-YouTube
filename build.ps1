# Packages the add-on into dist\context_search.ankiaddon
# (an .ankiaddon file is just a zip of the add-on folder *contents*)
#
# Entries are written with forward slashes on purpose: Compress-Archive on
# Windows PowerShell stores subfolders with backslashes, which breaks the
# add-on for macOS / Linux users (they end up with a file literally named
# "web\ctxsearch.js").

$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.IO.Compression | Out-Null
Add-Type -AssemblyName System.IO.Compression.FileSystem | Out-Null

$root = $PSScriptRoot
$src  = Join-Path $root "context_search"
$dist = Join-Path $root "dist"
$out  = Join-Path $dist "context_search.ankiaddon"

if (-not (Test-Path $src)) { throw "Source folder not found: $src" }
if (-not (Test-Path $dist)) { New-Item -ItemType Directory -Path $dist | Out-Null }
if (Test-Path $out) { Remove-Item -Force $out }

$files = Get-ChildItem -Path $src -Recurse -File |
    Where-Object { $_.FullName -notmatch '__pycache__' -and $_.Name -ne 'meta.json' }

if (-not $files) { throw "No files to package in $src" }

$zip = [System.IO.Compression.ZipFile]::Open($out, [System.IO.Compression.ZipArchiveMode]::Create)
try {
    foreach ($file in $files) {
        $relative = $file.FullName.Substring($src.Length).TrimStart('\', '/').Replace('\', '/')
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
            $zip, $file.FullName, $relative,
            [System.IO.Compression.CompressionLevel]::Optimal) | Out-Null
        Write-Host "  + $relative"
    }
}
finally {
    $zip.Dispose()
}

Write-Host "Built $out"
