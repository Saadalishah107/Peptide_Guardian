#!/bin/bash
set -e
echo "--- Preparing Node 2 Environment ---"
# Install with --user and set the home to /tmp to ensure it persists in this session
export HOME=/tmp
pip install --user --no-cache-dir pandas biopython
echo "✅ Dependencies installed."