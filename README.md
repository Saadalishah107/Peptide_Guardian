# Peptide_Guardian: Ensemble-Driven Discovery for Cyclic and Bioactive Peptides

## Project Overview
**Peptide_Guardian** is an industrial-grade, containerized bioinformatics suite engineered for the high-throughput characterization, biophysical profiling, and discovery of bioactive peptides. 

Initially conceived as a proof-of-concept under the repository name **silva-test**, the project has been heavily refactored and promoted to a production-ready framework optimized for the **Silva March 2026 Challenge**. The pipeline utilizes a decoupled, four-node Directed Acyclic Graph (DAG) architecture to transform uncharacterized FASTA sequences into a prioritized, multi-parameter-scored lead list, with a specialized focus on identifying **Cyclic Peptide Scaffolds**.

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
* **Execution:** The node processes data and writes artifacts to its root directory.
* **Harvesting:** Upon successful exit, the engine harvests root artifacts and persists them in the global `outputs/` directory.

### Infrastructure: `chiral-guardian:v1`
* **Base Image:** `python:3.11-slim`
* **System Packages:** `build-essential` (required for C-extensions during Scipy/Scikit-learn compilation).
* **Execution Protocol:** All nodes implement `pre_run.sh` (dependency validation) and `run.sh` (unbuffered Python execution via `python -u` for real-time Silva TUI telemetry).

---

## Detailed Node Specifications & Data Schemas

### Node 1: Data Ingestion (`a_ingest`)
* **Objective:** Sequence normalization, sanitation, and metadata tracking.
* **Inputs:** * `inputs/input.fasta`: Standard FASTA format file containing raw peptide sequences.
  * `global_params.json`: Dictates the target input filename.
* **Processing:** Sanitizes sequences (stripping regex `[^A-Z]`), standardizes to uppercase, and assigns a persistent tracking code.
* **Outputs:** * `cleaned_sequences.csv`: Structured data matrix.
  * *Columns:* `Peptide_ID` (e.g., P-0001), `Original_Header`, `Sequence`, `Sequence_Length`.

### Node 2: Biophysical Profiling (`b_features`)
* **Objective:** Feature Engineering and ADMET (Absorption, Distribution, Metabolism, Excretion, and Toxicity) Landscape Mapping.
* **Inputs:** * `inputs/cleaned_sequences.csv` (Relayed from Node 1).
* **Mathematical Descriptors:** * **Isoelectric Point (pI):** Predicted via the Bjellqvist method (pKa at 25°C).
  * **GRAVY:** Grand Average of Hydropathy score for solubility assessment.
  * **Net Charge:** Calculated at physiological pH (7.4) for cell-penetration potential.
  * **Cyclizability:** Boolean logic gate identifying sequences with `Cysteine count >= 2`.
* **Outputs:** * `peptide_features.csv`: Expanded data matrix ready for machine learning.
  * *Added Columns:* `MW`, `pI`, `GRAVY`, `Charge`, `Cys_Count`, `Cyclizable`.
  * `screening_report.html`: Standalone Plotly dashboard visualizing the Charge vs. Hydrophobicity landscape.

### Node 3: Ensemble Intelligence (`c_model`)
* **Objective:** Predictive Classification via Soft-Voting Ensemble Learning.
* **Algorithm:** Combines a Random Forest Classifier and an Extra Trees Classifier (200 estimators each, `max_depth=10`, `random_state=42`).
* **Inputs:** * `inputs/peptide_features.csv` (Relayed from Node 2).
* **Outputs:** * `peptide_guardian_model.pkl`: Serialized Scikit-learn `VotingClassifier` object.
  * `label_encoder.pkl`: Serialized `LabelEncoder` for inverse-transforming predictions back to biological classes.
  * `classification_report.html`: Model performance audit containing Validation Accuracy, AUC scores, and Feature Importance metrics.

### Node 4: Discovery Inference (`d_prediction`)
* **Objective:** High-Confidence Lead Ranking and Final Reporting.
* **Inputs:** * `inputs/peptide_features.csv` (Features from Node 2).
  * `inputs/peptide_guardian_model.pkl` & `label_encoder.pkl` (Model artifacts from Node 3).
  * `global_params.json` (For dynamic thresholding).
* **Logic:** Applies the trained ensemble to the feature matrix. Filters leads strictly exceeding the `confidence_threshold` (e.g., `0.85`).
* **Outputs:** * `guardian_leads.csv`: Final target list for in-vitro synthesis.
  * *Columns:* `Peptide_ID`, `Sequence`, `Predicted_Class`, `Confidence_Score`, `Cyclizable`.
  * `final_discovery_report.html`: CSS-grid dashboard with integrated `SheetJS` logic, allowing client-side Excel (.xlsx) export of the final lead list.

---

## Configuration & Local Development

### Global Parameters
Execution thresholds are controlled without touching source code via `global_params.json` located in the root directory:
```json
{
    "input_file": "input.fasta",
    "confidence_threshold": 0.85
}
```

### Python Dependencies (`requirements.txt`)
To run the analysis scripts outside of the Docker/Silva environment for debugging, use the included requirements:
```text
pandas
biopython
scikit-learn
plotly
joblib
scipy
requests
```
Install via: `pip install -r requirements.txt`

---

## Execution Guide

1. **Verify Home Environment:**
   ```bash
   export SILVA_WORKFLOW_HOME=/path/to/Peptide_Guardian
   ```
2. **Run Pipeline:**
   ```bash
   silva .
   ```
3. **Monitor Real-time Logs:**
   ```bash
   silva 
   ```

---

## References
1. **Cock, P. J., et al. (2009).** *Biopython: freely available Python tools for computational molecular biology and bioinformatics.*
2. **Pedregosa, F., et al. (2011).** *Scikit-learn: Machine Learning in Python.*
3. **Kyte, J., & Doolittle, R. F. (1982).** *A simple method for displaying the hydropathic character of a protein.*
4. **Silva Architecture Documentation (2026).** *Standardized Orchestration for Peptide Blueprinting.*

**Lead Developer:** @Saadalishah107  
**Submission Date:** March 2026  
**Theme Focus:** Cyclic Peptides | Multi-Step Discovery Workflows
