# Build script for Atlas.ti NVDA Add-on (Windows PowerShell)
# Creates the .nvda-addon package (which is a zip file with special extension)
#
# Author: Christos Bouronikos
# Email: chrisbouronikos@gmail.com
# GitHub: https://github.com/ChristosBouronikos
# Donations: https://paypal.me/christosbouronikos

$ErrorActionPreference = "Stop"

Write-Host "Building Atlas.ti Accessibility NVDA Add-on..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Read name/version from addon/manifest.ini
$ManifestLines = Get-Content -Path "addon\\manifest.ini"
$AddonName = ($ManifestLines | Where-Object { $_ -match "^\s*name\s*=" } | Select-Object -First 1).Split("=", 2)[1].Trim().Trim('"')
$Version = ($ManifestLines | Where-Object { $_ -match "^\s*version\s*=" } | Select-Object -First 1).Split("=", 2)[1].Trim().Trim('"')
if (-not $AddonName -or -not $Version) {
  throw "name/version missing from addon/manifest.ini"
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
# Note: the repository files are README.md/CHANGELOG.md (uppercase); Windows
# is case-insensitive so this always worked here, but match the real
# filenames anyway to stay consistent with build.sh (which runs on
# case-sensitive Linux CI runners, where the wrong case fails silently).
New-Item -ItemType Directory -Path "addon\\doc\\en" -Force | Out-Null
New-Item -ItemType Directory -Path "addon\\doc\\el" -Force | Out-Null
Copy-Item -Path "README.md" -Destination "addon\\doc\\en\\readme.md" -Force
Copy-Item -Path "README.md" -Destination "addon\\doc\\el\\readme.md" -Force
Copy-Item -Path "CHANGELOG.md" -Destination "addon\\doc\\en\\changelog.md" -Force
Copy-Item -Path "CHANGELOG.md" -Destination "addon\\doc\\el\\changelog.md" -Force
Copy-Item -Path "docs\\windows_atlasti26_validation.md" -Destination "addon\\doc\\en\\windows-validation.md" -Force
Copy-Item -Path "docs\\windows_atlasti26_validation.md" -Destination "addon\\doc\\el\\windows-validation.md" -Force
Copy-Item -Path "docs\\atlasti26_ui_catalogue.json" -Destination "addon\\doc\\en\\atlasti26-ui-catalogue.json" -Force
Copy-Item -Path "docs\\release_1.3.0.md" -Destination "addon\\doc\\en\\release-1.3.0.md" -Force

# Copy necessary files (addon contents) to temp root
Copy-Item -Path "addon\\*" -Destination $TempDir -Recurse -Force

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
