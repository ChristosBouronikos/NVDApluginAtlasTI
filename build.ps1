# Build script for Atlas.ti NVDA Add-on (Windows PowerShell)
# Creates the .nvda-addon package (which is a zip file with special extension)

$ErrorActionPreference = "Stop"

Write-Host "Building Atlas.ti Accessibility NVDA Add-on..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Read name/version from manifest.ini
$ManifestLines = Get-Content -Path "manifest.ini"
$AddonName = ($ManifestLines | Where-Object { $_ -match "^\s*name\s*=" } | Select-Object -First 1).Split("=", 2)[1].Trim()
$Version = ($ManifestLines | Where-Object { $_ -match "^\s*version\s*=" } | Select-Object -First 1).Split("=", 2)[1].Trim()
if (-not $AddonName -or -not $Version) {
  throw "name/version missing from manifest.ini"
}

$OutputFile = "$AddonName-$Version.nvda-addon"

# Clean up any previous build
Remove-Item -Path "*.nvda-addon" -Force -ErrorAction SilentlyContinue

Write-Host "Creating add-on package: $OutputFile" -ForegroundColor Yellow

# Create a temporary directory for the addon contents
$TempDir = Join-Path $env:TEMP "nvda-addon-build"
Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $TempDir | Out-Null

# Update documentation from root files
New-Item -ItemType Directory -Path "doc\en" -Force | Out-Null
New-Item -ItemType Directory -Path "doc\el" -Force | Out-Null
Copy-Item -Path "readme.md" -Destination "doc\en\readme.md" -Force
Copy-Item -Path "readme.md" -Destination "doc\el\readme.md" -Force
Copy-Item -Path "changelog.md" -Destination "doc\en\changelog.md" -Force
Copy-Item -Path "changelog.md" -Destination "doc\el\changelog.md" -Force

# Copy necessary files
Copy-Item -Path "manifest.ini" -Destination $TempDir
Copy-Item -Path "appModules" -Destination $TempDir -Recurse
Copy-Item -Path "globalPlugins" -Destination $TempDir -Recurse
Copy-Item -Path "locale" -Destination $TempDir -Recurse
Copy-Item -Path "doc" -Destination $TempDir -Recurse

# Remove any Python cache files
Get-ChildItem -Path $TempDir -Recurse -Include "*.pyc", "__pycache__", ".DS_Store" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Create the zip file and rename to .nvda-addon
$ZipPath = Join-Path $ScriptDir "$AddonName-$Version.zip"
Compress-Archive -Path "$TempDir\*" -DestinationPath $ZipPath -Force
Rename-Item -Path $ZipPath -NewName $OutputFile

# Clean up temp directory
Remove-Item -Path $TempDir -Recurse -Force

Write-Host ""
Write-Host "Build complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host "Output: $ScriptDir\$OutputFile" -ForegroundColor White
Write-Host ""
Write-Host "To install:" -ForegroundColor Yellow
Write-Host "1. Double-click the .nvda-addon file to install with NVDA"
Write-Host "   OR use NVDA Menu -> Tools -> Add-on Store -> Install from external source"
Write-Host ""
