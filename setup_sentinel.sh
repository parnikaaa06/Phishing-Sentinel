#!/bin/bash

# Create the root directory
mkdir -p phishing-sentinel
cd phishing-sentinel

echo "Initializing Sentinel Suite Directory Structure..."

# 1. API (Golang)
mkdir -p api/cmd api/internal api/pkg
touch api/go.mod api/.env.example
echo "// Entry point for Go API" > api/cmd/main.go

# 2. Dashboard (React)
mkdir -p dashboard/src/components dashboard/src/hooks dashboard/src/pages
touch dashboard/tailwind.config.js dashboard/package.json
echo "// React Dashboard entry" > dashboard/src/App.jsx

# 3. Extension (Browser Extension)
mkdir -p extension/public extension/src/background extension/src/content extension/src/popup
touch extension/public/manifest.json extension/vite.config.ts
echo "// Content script for DOM analysis" > extension/src/content/index.ts

# 4. ML Service (Python)
mkdir -p ml-service/models ml-service/src
touch ml-service/requirements.txt
echo "# DOM feature extraction" > ml-service/src/preprocess.py
echo "# Model training" > ml-service/src/train.py

# 5. Shared & Documentation
mkdir -p docs deployments
touch README.md .gitignore docker-compose.yml

# Initialize a basic .gitignore
cat <<EOF > .gitignore
# Binaries
bin/
*.exe

# Dependencies
node_modules/
vendor/
__pycache__/
venv/

# Environment
.env
.env.local

# Build outputs
dist/
build/
*.pth
*.h5
EOF

echo "Done! Structure created in /phishing-sentinel"
ls -R