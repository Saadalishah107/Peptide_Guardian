# Peptide_Guardian: Ensemble-Driven Discovery for Cyclic and Bioactive Peptides

## Project Overview

Peptide_Guardian is an industrial-grade, containerized bioinformatics suite engineered for the high-throughput characterization, biophysical profiling, and discovery of bioactive peptides. 

Initially conceived as a proof-of-concept under the repository name **silva-test**, the project has been heavily refactored, renamed, and promoted to a production-ready framework optimized for the Silva March 2026 Challenge. The pipeline utilizes a decoupled, four-node Directed Acyclic Graph (DAG) architecture to transform uncharacterized FASTA sequences into a prioritized, multi-parameter-scored lead list, with a specialized focus on identifying Cyclic Peptide Scaffolds.

---

## Scientific Reasoning and Design Philosophy

In peptide drug discovery, the primary bottleneck is the transition from biological activity to chemical stability (developability). Peptide_Guardian addresses this by:

* **Structural Stability Identification:** The pipeline specifically evaluates Cysteine density to flag sequences capable of disulfide-bridge cyclization, hitting a critical theme of modern peptidomimetics.
* **Ensemble Machine Learning:** By utilizing a soft-voting ensemble of Random Forest and Extra Trees, the engine achieves higher robustness than single-model architectures, particularly on the diverse datasets typical of Antimicrobial Peptides (AMPs).
* **Biophysical ADMET Audit:** Leads are ranked not just on prediction confidence, but on their physiological suitability (Isoelectric point, Net Charge at pH 7.4, and GRAVY solubility scores).

---

## System Architecture and Orchestration

The pipeline is managed by the Silva Engine, enforcing strict data hermeticity. Each job operates in an isolated container. Data is passed between nodes via the Silva Relay System:

* **Staging:** The engine mounts the previous node's `outputs/` as the current node's `inputs/`.
* **Execution:** The node processes data and writes artifacts to its root workspace.
* **Harvesting:** Upon successful exit, the engine harvests artifacts and persists them in the global `outputs/` directory.

### Infrastructure: `chiral-guardian:v1`
* **Base Image:** `python:3.11-slim`
* **System Packages:** `build-essential` (required for C-extensions during Scipy/Scikit-learn compilation).
* **Execution Protocol:** All nodes implement `pre_run.sh` (dependency validation) and `run.sh` (unbuffered Python execution via `python -u` for real-time Silva TUI telemetry).

---

## Detailed Node Specifications & Data Schemas

### Node 1: Data Ingestion (`a_ingest`)
* **Objective:** Sequence normalization, sanitation, and metadata tracking.
* **Input 1:** `inputs/input.fasta` - Standard FASTA format file containing raw peptide sequences.
* **Input 2:** `global_params.json` - Dictates the target input filename and global parameters.
* **Processing:** Sanitizes sequences (stripping regex `[^A-Z]`), standardizes to uppercase, and assigns a persistent tracking code.
* **Output 1:** `cleaned_sequences.csv` - Structured data matrix containing `Peptide_ID` (e.g., P-0001), `Original_Header`, `Sequence`, and `Sequence_Length`.

### Node 2: Biophysical Profiling (`b_features`)
* **Objective:** Feature Engineering and ADMET (Absorption, Distribution, Metabolism, Excretion, and Toxicity) Landscape Mapping.
* **Input 1:** `inputs/cleaned_sequences.csv` - Relayed automatically from Node 1.
* **Processing:** Calculates Isoelectric Point (Bjellqvist method), GRAVY (hydropathy/solubility), Net Charge at pH 7.4, and a Boolean Cyclizability score (Cysteine count >= 2).
* **Output 1:** `peptide_features.csv` - Expanded data matrix ready for machine learning (adds `MW`, `pI`, `GRAVY`, `Charge`, `Cys_Count`, `Cyclizable`).
* **Output 2:** `screening_report.html` - Standalone Plotly dashboard visualizing the Charge vs. Hydrophobicity landscape.

### Node 3: Ensemble Intelligence (`c_model`)
* **Objective:** Predictive Classification via Soft-Voting Ensemble Learning.
* **Algorithm:** Combines a Random Forest Classifier and an Extra Trees Classifier (200 estimators each, `max_depth=10`, `random_state=42`).
* **Input 1:** `inputs/peptide_features.csv` - Relayed automatically from Node 2.
* **Output 1:** `peptide_guardian_model.pkl` - Serialized Scikit-learn `VotingClassifier` object.
* **Output 2:** `label_encoder.pkl` - Serialized `LabelEncoder` for inverse-transforming predictions back to biological classes.
* **Output 3:** `classification_report.html` - Model performance audit containing Validation Accuracy, AUC scores, and Feature Importance metrics.

### Node 4: Discovery Inference (`d_prediction`)
* **Objective:** High-Confidence Lead Ranking and Final Reporting.
* **Input 1:** `inputs/peptide_features.csv` - Features relayed from Node 2.
* **Input 2:** `inputs/peptide_guardian_model.pkl` & `label_encoder.pkl` - Model artifacts relayed from Node 3.
* **Input 3:** `global_params.json` - Parsed for dynamic confidence thresholding.
* **Processing:** Applies the trained ensemble to the feature matrix. Filters leads strictly exceeding the user-defined `confidence_threshold`.
* **Output 1:** `guardian_leads.csv` - Final target list for in-vitro synthesis containing `Peptide_ID`, `Sequence`, `Predicted_Class`, `Confidence_Score`, and `Cyclizable`.
* **Output 2:** `final_discovery_report.html` - CSS-grid dashboard with integrated SheetJS logic, allowing client-side Excel (.xlsx) export of the final lead list.

---

## Configuration & Environment Setup

### Global Parameters
Execution thresholds are controlled without touching source code via `global_params.json` located in the root directory:
```json
{
    "input_file": "input.fasta",
    "confidence_threshold": 0.85
}

```

### Container Environment
This project does not rely on local Python virtual environments or a `requirements.txt` file. All dependencies (Pandas, Biopython, Scikit-learn, Plotly, etc.) are packaged directly into the node execution container. 

Before running the pipeline locally, you must compile the execution environment from the provided Dockerfile:
```bash
podman build -t chiral-guardian:v1 .
```
*(Note: If your system uses Docker, substitute `podman` with `docker` in the command above).*

### Execution Guide

**1. Verify Workspace Path:**
Ensure your orchestrator is pointing to the correct directory:
```bash
export SILVA_WORKFLOW_HOME=/path/to/Peptide_Guardian
```

**2. Run Pipeline:**
```bash
PODMAN_USERNS=keep-id silva .
```
*(The user namespace flag ensures rootless Podman maps container write-permissions accurately to your local host).*

---

## Troubleshooting & Execution Environments

This pipeline is optimized for seamless execution within **GitHub Codespaces**. Codespaces utilizes a Docker daemon that natively maps the container's internal root user to the workspace user, allowing frictionless volume mounting and file generation. 

If you are executing the pipeline locally on a Linux machine using **rootless Podman**, you may encounter strict user namespace isolation errors. Reference the solutions below to resolve local execution blocks.

### 1. Error: `os error 2` (No such file or directory)
* **Cause:** The project was renamed from `silva-test` to `Peptide_Guardian`, but shell environment variables or bash aliases are still pointing to the old directory path. Furthermore, the Silva orchestrator requires a base `.tmp` directory to exist before spawning execution workspaces.
* **Solution:** 1. Update your shell alias (e.g., in `~/.bashrc`) to: `alias silva="TMPDIR=/home/$USER/Peptide_Guardian/.tmp silva"`
  2. Create the missing temporary directory manually: `mkdir -p .tmp`

### 2. Error: `403 denied` (Failed to pull image)
* **Cause:** The pipeline is attempting to pull the `chiral-guardian:v1` image from a remote registry, but the image is designed to be built locally from the provided Dockerfile.
* **Solution:** Build the image locally before running the orchestrator:
  ```bash
  podman build -t chiral-guardian:v1 .
  ```

### 3. Error: `PermissionError: [Errno 13] Permission denied`
* **Cause:** Rootless Podman maps the internal container user to a restricted sub-UID on your host machine. When the Python scripts (e.g., `node1_ingest.py`) attempt to write output CSVs back to the host-mounted workspace, your local OS blocks the write operation. This does not happen in Codespaces due to unified UID mapping.
* **Solution:** Pass the user namespace override flag to Podman via the Silva orchestrator. This maps your local user ID directly to the container environment, granting it the same write permissions as your host profile:
  ```bash
  PODMAN_USERNS=keep-id silva .
  ```

---

## References
* Cock, P. J., et al. (2009). Biopython: freely available Python tools for computational molecular biology and bioinformatics.
* Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python.
* Kyte, J., & Doolittle, R. F. (1982). A simple method for displaying the hydropathic character of a protein.
* Silva Architecture Documentation (2026). Standardized Orchestration for Peptide Blueprinting.

**Lead Developer:** @Saadalishah107  
**Submission Date:** March 2026  
**Theme Focus:** Cyclic Peptides | Multi-Step Discovery Workflows  

