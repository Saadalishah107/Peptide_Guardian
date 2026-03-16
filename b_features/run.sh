#!/bin/bash
set -e
export PYTHONPATH=/tmp/packages:$PYTHONPATH
python3 node2_features.py
