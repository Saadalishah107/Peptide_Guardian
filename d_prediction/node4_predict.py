import pandas as pd
import joblib
from pathlib import Path

def run_node():
    FEATS_INPUT = Path("../b_features/outputs/peptide_features.csv")
    MODEL_PATH = Path("../c_model/outputs/peptide_guardian_model.pkl")
    ENCODER_PATH = Path("../c_model/outputs/label_encoder.pkl")
    OUT_DIR = Path("outputs")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if not FEATS_INPUT.exists():
        print(f"🛑 Error: No feature data found at {FEATS_INPUT}")
        return

    # 1. Load the Model and Dictionary
    model = joblib.load(MODEL_PATH)
    le = joblib.load(ENCODER_PATH)
    
    # 2. Load the features calculated in Node 2
    df = pd.read_csv(FEATS_INPUT)
    
    # Ensure we use the exact same feature columns as the training phase
    feature_cols = ['MW', 'pI', 'Hydrophobicity_GRAVY', 'Net_Charge_pH7.4', 'Cys_Count']
    X = df[feature_cols]

    print(f"🛡️ Peptide-Guardian: Scoring {len(df)} sequences for Chiral leads...")
    
    # 3. Generate Predictions
    preds = model.predict(X)
    probs = model.predict_proba(X)
    
    # Decode numeric labels back to strings (Antibacterial, etc.)
    df['Predicted_Type'] = le.inverse_transform(preds)
    df['Confidence'] = [round(max(p), 4) for p in probs]

    # 4. Save results
    df.to_csv(OUT_DIR / "guardian_leads.csv", index=False)

    # 5. Generate Final Interactive Report
    from html_generator import generate_final_report
    generate_final_report(df, OUT_DIR / "final_discovery_report.html")

    print(f"✅ SUCCESS: Lead discovery report generated.")

if __name__ == "__main__":
    run_node()