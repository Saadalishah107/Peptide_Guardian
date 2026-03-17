import pandas as pd
import joblib
import json
from pathlib import Path

def load_params():
    """Load global parameters for dynamic filtering/thresholds."""
    params_path = Path("inputs/global_params.json")
    if params_path.exists():
        with open(params_path) as f:
            return json.load(f)
    return {}

def run_node():
    # Silva Rule: All staged dependencies live in ./inputs/
    feat_path = Path("inputs/peptide_features.csv")
    model_path = Path("inputs/peptide_guardian_model.pkl")
    encoder_path = Path("inputs/label_encoder.pkl")

    # Local fallback for manual testing outside of Docker
    if not feat_path.exists(): feat_path = Path("peptide_features.csv")
    if not model_path.exists(): model_path = Path("peptide_guardian_model.pkl")
    if not encoder_path.exists(): encoder_path = Path("label_encoder.pkl")

    if not (feat_path.exists() and model_path.exists() and encoder_path.exists()):
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

    #  CRITICAL FIX: Final Export directly to root directory
    lead_file = "guardian_leads.csv"
    df.to_csv(lead_file, index=False)

    # Generate Final Platform Report
    try:
        from html_generator import generate_final_report
        # CRITICAL FIX: Pass root path instead of outputs/
        generate_final_report(df, "final_discovery_report.html")
        print("Success: Final discovery report generated.")
    except ImportError:
        print("Warning: html_generator.py not found, skipping HTML report.")
    except Exception as e:
        print(f"Warning: Discovery visualization failed: {e}")

    print("Success: Workflow complete. Final leads saved to root directory.")

if __name__ == "__main__":
    run_node()