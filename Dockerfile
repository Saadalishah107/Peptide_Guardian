# Use a stable, lightweight Python base
FROM python:3.11-slim

# Install system dependencies needed for some bio-packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Pre-install all libraries used in your 4 nodes
# This is what makes the pipeline "Instant"
RUN pip install --no-cache-dir \
    pandas \
    biopython \
    scikit-learn \
    requests \
    joblib \
    scipy \
    plotly

# Set the workspace (Silva mounts your code here)
WORKDIR /workspace