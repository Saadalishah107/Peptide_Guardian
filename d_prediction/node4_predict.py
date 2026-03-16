import pandas as pd
import joblib
import os
from pathlib import Path

def find_file(filename, search_path=".."):
    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)
    return None

def run_node():
    out_dir = Path("results")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Define required inputs
    feat_path = Path("inputs/peptide_features.csv")
    model_path = Path("inputs/peptide_guardian_model.pkl")
    encoder_path = Path("inputs/label_encoder.pkl")

    # Search logic for multiple inputs
    if not feat_path.exists():
        found = find_file("peptide_features.csv")
        if found: feat_path = Path(found)
    
    if not model_path.exists():
        found = find_file("peptide_guardian_model.pkl")
        if found: model_path = Path(found)
            
    if not encoder_path.exists():
        found = find_file("label_encoder.pkl")
        if found: encoder_path = Path(found)

    # Final validation before proceeding
    if not all([feat_path.exists(), model_path.exists(), encoder_path.exists()]):
        print("Error: One or more required inputs are missing.")
        if os.path.exists("inputs"):
            print(f"Available in inputs: {os.listdir('inputs')}")
        return

    print("Loading model and feature data...")
    try:
        model = joblib.load(model_path)
        le = joblib.load(encoder_path)
        df = pd.read_csv(feat_path)
    except Exception as e:
        print(f"Failed to load data: {e}")
        return
    
    feature_cols = ['MW', 'pI', 'Hydrophobicity_GRAVY', 'Net_Charge_pH7.4', 'Cys_Count']
    X = df[feature_cols]

    print(f"Scoring {len(df)} sequences for Chiral leads...")
    
    preds = model.predict(X)
    probs = model.predict_proba(X)
    
    df['Predicted_Type'] = le.inverse_transform(preds)
    df['Confidence'] = [round(max(p), 4) for p in probs]

    lead_file = out_dir / "guardian_leads.csv"
    df.to_csv(lead_file, index=False)

    try:
        from html_generator import generate_final_report
        generate_final_report(df, str(out_dir / "final_discovery_report.html"))
        print("Final discovery report generated.")
    except Exception as e:
        print(f"Report generation failed: {e}")

    print(f"Success: Results saved to {out_dir}")

if __name__ == "__main__":
    run_node()