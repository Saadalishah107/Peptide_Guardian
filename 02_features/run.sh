#!/bin/bash
set -e
export HOME=/tmp
# Tell Python to look in the local user folder where we just installed things
export PATH=$HOME/.local/bin:$PATH
export PYTHONPATH=$HOME/.local/lib/python3.11/site-packages:$PYTHONPATH

python3 node2_features.py