#!/bin/bash
# Add the temporary packages to the Python path
export PYTHONPATH=/tmp/packages:$PYTHONPATH

# Run the prediction engine
python3 node4_predict.py