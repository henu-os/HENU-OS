#!/usr/bin/env bash
# ==============================================================================
# HENU OS 3.0 Apps Repository Initializer Script
# Version: 3.0.0-alpha.1
# OS: Linux / Bash
# ==============================================================================

set -euo pipefail

APPS=(
    "ai" "hub" "assistant" "terminal" "settings" "update"
    "firewall" "cloud" "ide" "files" "backup" "monitor" "sdk"
)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
APPS_DIR="${WORKSPACE_ROOT}/apps"

echo "Initializing standalone applications structure under: ${APPS_DIR}"

LICENSE_CONTENT=$(cat << 'EOF'
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
EOF
)

GITIGNORE_CONTENT=$(cat << 'EOF'
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
EOF
)

for APP in "${APPS[@]}"; do
    APP_DIR="${APPS_DIR}/${APP}"
    DOCS_DIR="${APP_DIR}/docs"
    SRC_DIR="${APP_DIR}/src"

    echo "Creating repository files for app: henu-${APP}..."

    mkdir -p "${DOCS_DIR}"
    mkdir -p "${SRC_DIR}"

    echo "${LICENSE_CONTENT}" > "${APP_DIR}/LICENSE"
    echo "${GITIGNORE_CONTENT}" > "${APP_DIR}/.gitignore"

    # Write README.md
    cat << EOF > "${APP_DIR}/README.md"
# henu-${APP}

> **Component Type: Independent Application**  
> **System Scope: HENU OS 3.0 (v3.0.0-alpha.1)**

## Overview
This is the standalone **henu-${APP}** repository for HENU OS. It is compiled, packaged, and versioned independently of the core OS files to ensure clean updates and hot-fixes.

## Structure
- \`src/\`: Core source files of the application.
- \`docs/\`: User manual and developer guidelines specific to this application.
- \`LICENSE\`: Open-source licensing.
- \`.gitignore\`: Standard exclusion patterns for compilation and local build caches.

## Developer Setup
Please read the root documentation at [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md) for OS-wide development parameters.
EOF

    echo -e "# henu-${APP} Documentation\n\nDetails on app setup and usage will be populated here." > "${DOCS_DIR}/index.md"
    
    # Create Python src placeholder
    cat << 'EOF' > "${SRC_DIR}/main.py"
#!/usr/bin/env python3

def main():
    print("Initializing henu-app version 3.0.0-alpha.1")

if __name__ == '__main__':
    main()
EOF
    chmod +x "${SRC_DIR}/main.py"
done

echo "Application initializations successfully completed."
