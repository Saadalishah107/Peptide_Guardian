# Peptide_Guardian: High-Fidelity Peptide Discovery Pipeline

## Project Overview
**Peptide_Guardian** is an automated, containerized bioinformatics suite engineered for the high-throughput characterization and discovery of bioactive peptides. Previously developed under the working title **silva-test**, the pipeline has been promoted to a production-ready framework optimized for the **Silva March 2026 Engine**. It utilizes a four-node decoupled architecture to transform raw FASTA sequences into actionable, lab-ready lead lists with high-confidence scoring.

---

## System Architecture and Infrastructure

### Orchestration Environment
The pipeline is orchestrated as a **Directed Acyclic Graph (DAG)**, ensuring data hermeticity and strict dependency management. Each node is isolated within its own container environment but linked via the Silva relay system, where outputs from one node are staged as inputs for the next.

### Container Specification: `chiral-guardian:v1`
The pipeline operates within a standardized Docker environment defined by the following specifications:
* **Base Image:** `python:3.11-slim`
* **System Dependencies:** `build-essential` (required for Scipy/Scikit-learn C-extensions).
* **Python Stack:** `pandas`, `biopython` (ProtParam), `scikit-learn`, `joblib`, `plotly`, and `scipy`.
* **Execution Protocol:** Every node utilizes a `pre_run.sh` for environment validation and a `run.sh` with unbuffered logging (`-u`) to provide real-time telemetry to the Silva TUI.

---

## Detailed Node Specifications

### Node 1: Data Ingestion (`a_ingest`)
* **Primary Role:** Sequence Normalization and Sanitation.
* **Inputs:** * `input_files/input.fasta`: Raw peptide sequences in FASTA format.
    * `global_params.json`: Global configuration file specifying the target `input_file`.
* **Processing Logic:** The node parses the FASTA file, sanitizes sequences by converting to uppercase and removing non-amino acid characters, and generates unique `Peptide_ID` tracking codes (format: `P-XXXX`).
* **Outputs:** `cleaned_sequences.csv`.

### Node 2: Biophysical Profiling (`b_features`)
* **Primary Role:** Feature Engineering and ADMET Landscape Mapping.
* **Inputs:** `cleaned_sequences.csv` (Relayed from Node 1).
* **Processing Logic:** Extracts five primary biophysical descriptors:
    1. **Molecular Weight (MW)**: Calculated in Daltons.
    2. **Isoelectric Point (pI)**: Predicted pH at zero net charge.
    3. **Hydrophobicity (GRAVY)**: Grand Average of Hydropathy score.
    4. **Net Charge**: Calculated at physiological pH (7.4).
    5. **Cys_Count**: Quantification of Cysteine residues for cyclization potential.
* **Outputs:** `peptide_features.csv`, `screening_report.html`.

### Node 3: Ensemble Intelligence (`c_model`)
* **Primary Role:** Machine Learning Classification.
* **Inputs:** `peptide_features.csv` (Relayed from Node 2).
* **Processing Logic:** Executes a **Soft-Voting Ensemble** combining `RandomForestClassifier` and `ExtraTreesClassifier` (200 estimators each). 
* **Outputs:** `peptide_guardian_model.pkl`, `label_encoder.pkl`, `classification_report.html`.

### Node 4: Discovery Inference (`d_prediction`)
* **Primary Role:** Final Lead Scoring and Reporting.
* **Inputs:** `peptide_features.csv`, `peptide_guardian_model.pkl`, `label_encoder.pkl`.
* **Processing Logic:** Performs batch inference, filters by the `confidence_threshold` set in `global_params.json`, and ranks high-interest leads.
* **Outputs:** `guardian_leads.csv`, `final_discovery_report.html`.

---

## Artifact Harvesting and Deployment

The Silva Engine aggregates outputs from the isolated node directories into a centralized root `outputs/` folder upon completion.

| Artifact | Source Node | Scientific Utility |
| :--- | :--- | :--- |
| **guardian_leads.csv** | `d_prediction` | Primary lead list for in-vitro testing. |
| **final_discovery_report.html** | `d_prediction` | Presentation-ready summary with data export. |
| **peptide_guardian_model.pkl** | `c_model` | Trained weights for future batch inference. |
| **screening_report.html** | `b_features` | Initial biophysical screening and diversity audit. |

---

## References
1. **Cock, P. J., et al. (2009).** *Biopython: freely available Python tools for computational molecular biology and bioinformatics.* Bioinformatics.
2. **Pedregosa, F., et al. (2011).** *Scikit-learn: Machine Learning in Python.* JMLR.
3. **Kyte, J., & Doolittle, R. F. (1982).** *A simple method for displaying the hydropathic character of a protein.* JMB.
4. **Silva Architecture Documentation (2026).** *Standardized Orchestration for Containerized Bioinformatics Pipelines.*

**Lead Developer:** @Saadalishah107  
**Engine Version:** Silva March 2026  
**Project Status:** Active (Transitioned from `silva-test`)
