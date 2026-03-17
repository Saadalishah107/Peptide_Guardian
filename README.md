# Peptide_Guardian: High-Fidelity Peptide Discovery Pipeline

## Project Overview
**Peptide_Guardian** is an industrial-grade, containerized bioinformatics suite engineered for the high-throughput characterization, biophysical profiling, and discovery of bioactive peptides. 

Originally developed under the working title **silva-test**, this framework has been promoted to a production-ready discovery engine optimized for the **Silva March 2026 Orchestration Standard**. The pipeline utilizes a four-node Directed Acyclic Graph (DAG) architecture to transform raw, uncharacterized FASTA sequences into a prioritized, multi-parameter-scored lead list ready for in-vitro validation.

---

## System Architecture and Data Relay Logic

### Orchestration Environment
The pipeline is managed by the Silva Engine, which enforces strict data hermeticity. Each node operates within an isolated container environment. Data is passed between nodes via a "Relay System":
1. **Staging**: The engine mounts the previous node's `outputs/` as the current node's `inputs/`.
2. **Execution**: The node processes data and writes artifacts to its root directory.
3. **Harvesting**: Upon successful exit code 0, the engine harvests all root artifacts and persists them in the global `outputs/` directory for downstream consumption.

### Computational Infrastructure: `chiral-guardian:v1`
The pipeline is built upon a high-performance Docker image:
* **Operating System**: `python:3.11-slim` for a minimal security attack surface.
* **Build Tools**: `build-essential` included for compiling Scikit-learn and Scipy C-extensions.
* **Core Libraries**: 
    * **Biopython**: Specifically the `ProtParam` module for molecular weight and pI calculations.
    * **Scikit-learn**: Powering the Soft-Voting Ensemble (Random Forest & Extra Trees).
    * **Plotly**: Generating interactive, browser-based biophysical dashboards.
    * **SheetJS**: Integrated into the final report for client-side Excel generation.
    * **Pandas**: Optimized for large-scale peptide sequence matrices.

---

## Detailed Node Specifications

### Node 1: Data Ingestion (`a_ingest`)
* **Objective**: Source normalization and sequence sanitation.
* **Logic**: Utilizing `global_params.json`, the node locates the target FASTA. It implements a custom parser that:
    * Sanitizes sequences by stripping non-amino acid characters and whitespace.
    * Standardizes sequence case to Uppercase.
    * Assigns a persistent `Peptide_ID` (format: `P-0001` to `P-XXXX`) to maintain traceability.
* **Inputs**: `input_files/input.fasta`, `global_params.json`.
* **Outputs**: `cleaned_sequences.csv`.

### Node 2: Biophysical Profiling (`b_features`)
* **Objective**: Feature Engineering and ADMET Landscape Mapping.
* **Mathematical Descriptors**:
    * **Isoelectric Point (pI)**: Predicted using the Bjellqvist method (pKa values determined at 25°C).
    * **GRAVY (Grand Average of Hydropathy)**: Calculated based on the Kyte-Doolittle scale to assess solubility.
    * **Net Charge**: Calculated at physiological pH (7.4) to determine cell-membrane interaction potential.
    * **Molecular Weight (MW)**: Full-precision calculation based on monoisotopic mass.
    * **Cyclizability Flag**: A logic-gate identifying sequences with a Cysteine count $\ge$ 2.
* **Reporting**: Generates `screening_report.html`, featuring a 3D-interactive ADMET landscape using Plotly to visualize Charge vs. Hydrophobicity.
* **Inputs**: `cleaned_sequences.csv`.
* **Outputs**: `peptide_features.csv`, `screening_report.html`.

### Node 3: Ensemble Intelligence (`c_model`)
* **Objective**: Predictive Classification via Soft-Voting Ensemble Learning.
* **Algorithm Architecture**: 
    1. **Random Forest Classifier**: 200 estimators, `max_depth=10`, `random_state=42`. Focuses on robust decision boundaries.
    2. **Extra Trees Classifier**: 200 estimators, `max_depth=10`, `random_state=42`. Adds randomization to reduce variance.
    3. **Voting Mechanism**: Soft-voting combines predicted class probabilities of both models to increase classification confidence.
* **Model Training**: Utilizes a stratified 80/20 train-test split to ensure class representation.
* **Reporting**: Generates `classification_report.html` documenting Accuracy, AUC, and Feature Importance (Scientific Drivers).
* **Inputs**: `peptide_features.csv`.
* **Outputs**: `peptide_guardian_model.pkl`, `label_encoder.pkl`, `classification_report.html`.

### Node 4: Discovery Inference (`d_prediction`)
* **Objective**: High-Confidence Lead Ranking and Final Synthesis.
* **Discovery Logic**: Applies the finalized model to the feature matrix. It implements a **Confidence Threshold Filter** (configured in `global_params.json`). 
* **Key Features**: 
    * **Specialty Prediction**: Decodes numeric labels back to biological classes (e.g., AMP, Non-AMP).
    * **Advanced Reporting**: The `final_discovery_report.html` uses an embedded CSS grid and `SheetJS`. It highlights cyclizable leads in green for high structural stability.
    * **Excel Export**: A one-click "Download Lead List" button for immediate lab transition.
* **Inputs**: `peptide_features.csv`, `.pkl` artifacts from Node 3.
* **Outputs**: `guardian_leads.csv`, `final_discovery_report.html`.

---

## Artifact Harvesting Summary

The Silva Engine aggregates outputs from the isolated node directories into a centralized root `outputs/` folder.

| Artifact | Origin | Scientific Utility |
| :--- | :--- | :--- |
| **guardian_leads.csv** | Node 4 | The finalized discovery list for laboratory synthesis. |
| **final_discovery_report.html** | Node 4 | The master dashboard with interactive leads and Excel export. |
| **peptide_guardian_model.pkl** | Node 3 | The serialized "Golden Model" for future batch predictions. |
| **screening_report.html** | Node 2 | Early-stage visual audit of sequence diversity and biophysical distribution. |

---

## Deployment and Execution

### 1. Configuration
Modify `global_params.json` at the project root:
```json
{
    "input_file": "input.fasta",
    "confidence_threshold": 0.85
}
```

### 2. Execution via Silva CLI
Trigger the automated pipeline:
```bash
silva .
```

### 3. Real-Time Telemetry
Monitor unbuffered terminal output and node health:
```bash
silva 
```

---

## References

1. **Cock, P. J., et al. (2009).** *Biopython: freely available Python tools for computational molecular biology and bioinformatics.* Bioinformatics, 25(11), 1422-1423.
2. **Pedregosa, F., et al. (2011).** *Scikit-learn: Machine Learning in Python.* Journal of Machine Learning Research, 12, 2825-2830.
3. **Kyte, J., & Doolittle, R. F. (1982).** *A simple method for displaying the hydropathic character of a protein.* Journal of Molecular Biology, 157(1), 105-132.
4. **Silva Architecture Documentation (2026).** *Standardized Orchestration for Containerized Bioinformatics Pipelines.* Internal Technical Specification.

---

**Lead Developer**: @Saadalishah107  
**Engine Version**: Silva March 2026  
**Project Status**: Active (Transitioned from silva-test)
