#!/bin/bash
set -e
export PYTHONPATH=/tmp/packages:$PYTHONPATH
python3 node1_ingest.py
