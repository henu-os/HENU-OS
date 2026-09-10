# ==============================================================================
# HENU OS 3.0 Branding Directory Initializer (Debian Architecture)
# ==============================================================================

$branding_dirs = @(
    "branding/logos/primary", "branding/logos/secondary", "branding/logos/wordmark", "branding/logos/monochrome", "branding/logos/svg", "branding/logos/png",
    "branding/wallpapers/official/fhd", "branding/wallpapers/official/2k", "branding/wallpapers/official/4k",
    "branding/wallpapers/login", "branding/wallpapers/lockscreen", "branding/wallpapers/plymouth", "branding/wallpapers/grub", "branding/wallpapers/installer",
    "branding/icons", "branding/fonts", "branding/themes", "branding/cursor", "branding/sounds", "branding/animations", "branding/plymouth", "branding/grub", "branding/gdm",
    "branding-package/debian"
)

foreach ($dir in $branding_dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "[CREATED] $dir" -ForegroundColor Green
    }
}
Write-Host "Branding directory layout initialized for Debian packaging." -ForegroundColor Cyan
