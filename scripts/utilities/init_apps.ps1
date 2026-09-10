# ==============================================================================
# HENU OS 3.0 Apps Repository Initializer Script
# Version: 3.0.0-alpha.1
# OS: Windows (PowerShell)
# ==============================================================================

$apps = @(
    "ai", "hub", "assistant", "terminal", "settings", "update",
    "firewall", "cloud", "ide", "files", "backup", "monitor", "sdk"
)

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspaceRoot = Resolve-Path "$scriptPath\..\.."
$appsDir = "$workspaceRoot\apps"

Write-Host "Initializing standalone applications structure under: $appsDir" -ForegroundColor Cyan

# MIT License content template
$licenseContent = @"
MIT License

Copyright (c) 2026 HENU OS Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"@

# Gitignore content template
$gitignoreContent = @"
# Local application build files and caches
bin/
obj/
dist/
build/
*.log
*.tmp
node_modules/
__pycache__/
*.pyc
.vs/
.vscode/
.DS_Store
"@

foreach ($app in $apps) {
    $appDir = Join-Path $appsDir $app
    $docsDir = Join-Path $appDir "docs"
    $srcDir = Join-Path $appDir "src"
    
    Write-Host "Creating repository files for app: henu-$app..." -ForegroundColor Green
    
    # Create directories
    $null = New-Item -ItemType Directory -Path $appDir -Force
    $null = New-Item -ItemType Directory -Path $docsDir -Force
    $null = New-Item -ItemType Directory -Path $srcDir -Force
    
    # Write LICENSE and .gitignore
    Set-Content -Path (Join-Path $appDir "LICENSE") -Value $licenseContent -Force
    Set-Content -Path (Join-Path $appDir ".gitignore") -Value $gitignoreContent -Force
    
    # Write README.md
    $readmeContent = @"
# henu-$app

> **Component Type: Independent Application**  
> **System Scope: HENU OS 3.0 (v3.0.0-alpha.1)**

## Overview
This is the standalone **henu-$app** repository for HENU OS. It is compiled, packaged, and versioned independently of the core OS files to ensure clean updates and hot-fixes.

## Structure
- `src/`: Core source files of the application.
- `docs/`: User manual and developer guidelines specific to this application.
- `LICENSE`: Open-source licensing.
- `.gitignore`: Standard exclusion patterns for compilation and local build caches.

## Developer Setup
Please read the root documentation at [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md) for OS-wide development parameters.
"@
    Set-Content -Path (Join-Path $appDir "README.md") -Value $readmeContent -Force
    
    # Create basic placeholder files in docs/ and src/
    Set-Content -Path (Join-Path $docsDir "index.md") -Value "# henu-$app Documentation`n`nDetails on app setup and usage will be populated here." -Force
    Set-Content -Path (Join-Path $srcDir "main.py") -Value "#!/usr/bin/env python3`n`ndef main():`n    print('Initializing henu-$app version 3.0.0-alpha.1')`n`nif __name__ == '__main__':`n    main()`n" -Force
}

Write-Host "Application initializations successfully completed." -ForegroundColor Green
