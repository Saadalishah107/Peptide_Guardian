# Peptide_Guardian: Ensemble-Driven Discovery for Cyclic and Bioactive Peptides

## Project Overview
**Peptide_Guardian** is an industrial-grade, containerized bioinformatics suite engineered for the high-throughput characterization, biophysical profiling, and discovery of bioactive peptides. Developed as a submission for the Silva March 2026 Challenge, this framework focuses on bridging the gap between raw sequence data and developable drug leads. 

The pipeline utilizes a decoupled, four-node Directed Acyclic Graph (DAG) architecture to transform uncharacterized FASTA sequences into a prioritized, multi-parameter-scored lead list, with a specialized focus on identifying **Cyclic Peptide Scaffolds**.

---

## Scientific Reasoning and Design Philosophy
In peptide drug discovery, the primary bottleneck is often the transition from biological activity to chemical stability (developability). Peptide_Guardian addresses this by:

1. **Structural Stability Identification:** The pipeline specifically evaluates Cysteine density to flag sequences capable of disulfide-bridge cyclization, hitting a critical theme of modern peptidomimetics.
2. **Ensemble Machine Learning:** By utilizing a soft-voting ensemble of Random Forest and Extra Trees, the engine achieves higher robustness than single-model architectures, particularly on the diverse datasets typical of Antimicrobial Peptides (AMPs).
3. **Biophysical ADMET Audit:** Leads are ranked not just on prediction confidence, but on their physiological suitability (Isoelectric point, Net Charge at pH 7.4, and GRAVY solubility scores).

---

## System Architecture and Data Relay Logic

### Orchestration Environment
The pipeline is managed by the Silva Engine, enforcing strict data hermeticity. Each job operates in an isolated container. Data is passed between nodes via the Silva Relay System:
* **Staging:** The engine mounts the previous node's `outputs/` as the current node's `inputs/`.
* **Execution:** The node processes data and writes artifacts to its root directory.
* **Harvesting:** Upon successful exit, the engine harvests root artifacts and persists them in the global `outputs/` directory.

### Infrastructure: `chiral-guardian:v1`
* **Base Image:** `python:3.11-slim`
* **Dependencies:** `pandas`, `biopython` (ProtParam), `scikit-learn`, `joblib`, `plotly`, and `scipy`.
* **Standardization:** All nodes implement `pre_run.sh` (dependency validation) and `run.sh` (unbuffered Python execution).

---

## Detailed Node Specifications

### Node 1: Data Ingestion (`a_ingest`)
* **Objective:** Sequence normalization and sanitation.
* **Inputs:** `input_files/input.fasta`, `global_params.json`.
* **Processing:** Sanitizes sequences (stripping non-AA characters), standardizes to uppercase, and assigns unique `Peptide_ID` tracking codes (P-0001 to P-XXXX).
* **Outputs:** `cleaned_sequences.csv`.

### Node 2: Biophysical Profiling (`b_features`)
* **Objective:** Feature Engineering and ADMET Landscape Mapping.
* **Inputs:** `cleaned_sequences.csv`.
* **Descriptors:** * **Isoelectric Point (pI):** Predicted via Bjellqvist method.
    * **GRAVY:** Grand Average of Hydropathy score.
    * **Net Charge:** Calculated at physiological pH (7.4).
    * **Cyclizability:** Logic gate identifying sequences with Cysteine count $\ge$ 2.
* **Outputs:** `peptide_features.csv`, `screening_report.html` (Interactive Plotly Dashboard).

### Node 3: Ensemble Intelligence (`c_model`)
* **Objective:** Predictive Classification via Ensemble Learning.
* **Algorithm:** A Soft-Voting Ensemble combining a Random Forest Classifier and an Extra Trees Classifier (200 estimators each, max_depth=10).
* **Inputs:** `peptide_features.csv`.
* **Outputs:** `peptide_guardian_model.pkl`, `label_encoder.pkl`, `classification_report.html`.

### Node 4: Discovery Inference (`d_prediction`)
* **Objective:** High-Confidence Lead Ranking and Synthesis.
* **Inputs:** Features from Node 2, Model artifacts from Node 3.
* **Logic:** Applies the ensemble engine and filters by the `confidence_threshold` (e.g., 0.85) defined in `global_params.json`.
* **Reporting:** Generates `final_discovery_report.html` featuring a CSS-grid dashboard and an integrated **SheetJS** tool for client-side Excel export of top leads.
* **Outputs:** `guardian_leads.csv`, `final_discovery_report.html`.

---

## Artifact Harvesting Matrix

| Artifact | Source Node | Scientific Utility |
| :--- | :--- | :--- |
| **guardian_leads.csv** | Node 4 | Finalized ranked list for in-vitro synthesis. |
| **final_discovery_report.html** | Node 4 | Interpretable dashboard with client-side Excel export. |
| **peptide_guardian_model.pkl** | Node 3 | Serialized model for future batch inference. |
| **screening_report.html** | Node 2 | Visual audit of the sequence-activity landscape. |

---

## Execution Guide

1. **Verify Home Environment:**
   `export SILVA_WORKFLOW_HOME=/path/to/Peptide_Guardian`

2. **Run Pipeline:**
   `silva .`

3. **Monitor Real-time Logs:**
   `silva `

---

## References
1. **Cock, P. J., et al. (2009).** *Biopython: freely available Python tools for computational molecular biology and bioinformatics.*
2. **Pedregosa, F., et al. (2011).** *Scikit-learn: Machine Learning in Python.*
3. **Kyte, J., & Doolittle, R. F. (1982).** *A simple method for displaying the hydropathic character of a protein.*
4. **Silva Architecture Documentation (2026).** *Standardized Orchestration for Peptide Blueprinting.*

**Lead Developer:** @Saadalishah107  
**Submission Date:** March 2026  
**Theme Focus:** Cyclic Peptides | Multi-Step Discovery Workflows
