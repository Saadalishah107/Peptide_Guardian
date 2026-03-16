import pandas as pd
import joblib
import os
import json
from pathlib import Path

def find_file(filename, search_path=".."):
    """Guide Step 9: Robust file discovery fallback."""
    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)
    return None

def load_params():
    """Load global parameters for dynamic filtering/thresholds."""
    params_path = Path("inputs/global_params.json")
    if params_path.exists():
        with open(params_path) as f:
            return json.load(f)
    return {}

def run_node():
    # Silva Rule: Standard outputs folder for final collection
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Silva Rule: All staged dependencies live in ./inputs/
    feat_path = Path("inputs/peptide_features.csv")
    model_path = Path("inputs/peptide_guardian_model.pkl")
    encoder_path = Path("inputs/label_encoder.pkl")

    # Robust discovery for Silva distributed environments
    paths = [feat_path, model_path, encoder_path]
    for i, p in enumerate(paths):
        if not p.exists():
            found = find_file(p.name)
            if found: paths[i] = Path(found)

    feat_path, model_path, encoder_path = paths

    if not all(p.exists() for p in paths):
        print("Error: Required artifacts (features or model) missing from ./inputs/")
        return

    print("Loading discovery engine and feature matrix...")
    try:
        model = joblib.load(model_path)
        le = joblib.load(encoder_path)
        df = pd.read_csv(feat_path)
    except Exception as e:
        print(f"Failed to load prediction artifacts: {e}")
        return
    
    # Feature engineering alignment
    feature_cols = ['MW', 'pI', 'Hydrophobicity_GRAVY', 'Net_Charge_pH7.4', 'Cys_Count']
    X = df[feature_cols]

    print(f"Scoring {len(df)} sequences for candidate discovery...")
    
    # Prediction Execution
    preds = model.predict(X)
    probs = model.predict_proba(X)
    
    # Decode and Score
    df['Predicted_Type'] = le.inverse_transform(preds)
    df['Confidence'] = [round(max(p), 4) for p in probs]

    # Optional: Apply threshold from global_params if present
    params = load_params()
    threshold = params.get("confidence_threshold", 0.0)
    if threshold > 0:
        df = df[df['Confidence'] >= threshold]
        print(f"Applied filtering: {len(df)} leads remaining (threshold > {threshold})")

    # Final Export
    lead_file = out_dir / "guardian_leads.csv"
    df.to_csv(lead_file, index=False)

    # Generate Final Platform Report
    try:
        from html_generator import generate_final_report
        generate_final_report(df, str(out_dir / "final_discovery_report.html"))
        print("Success: Final discovery report generated.")
    except Exception as e:
        print(f"Warning: Discovery visualization failed: {e}")

    print(f"Success: Workflow complete. Final leads saved to {out_dir}")

if __name__ == "__main__":
    run_node()