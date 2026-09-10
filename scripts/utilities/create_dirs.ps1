# ==============================================================================
# HENU OS 3.0 Workspace Directory Initializer (Debian Architecture)
# ==============================================================================

$folders = @(
    "apps", "configs", "scripts", "docs", "branding", "branding-package",
    "build", "build-engine", "desktop", "installer", "kernel", "packages", "testing", "ci",
    "build/iso", "build/deb", "build/cache/apt", "build/logs", "build/live-build",
    "branding-package/debian",
    "installer/calamares", "installer/debian-installer",
    "kernel/config", "kernel/patches", "kernel/modules", "kernel/scripts",
    "testing/qemu", "testing/virtualbox"
)

foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "[CREATED] $folder" -ForegroundColor Green
    }
}
Write-Host "HENU OS 3.0 Debian Workspace Structure Initialized." -ForegroundColor Cyan
