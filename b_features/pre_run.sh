#!/bin/bash
set -e
# Install to /tmp/packages to avoid root permission issues
pip install --target=/tmp/packages requests biopython pandas