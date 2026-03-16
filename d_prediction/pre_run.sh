#!/bin/bash

echo "--- Environment Ready for $(hostname) ---"

python3 -c "import pandas; import sklearn; print('Dependencies verified.')"