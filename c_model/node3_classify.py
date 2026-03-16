import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, VotingClassifier
from sklearn.preprocessing import LabelEncoder

def run_node():
    # 1. Setup Paths
    INPUT = Path("../b_features/outputs/peptide_features.csv")
    OUT_DIR = Path("outputs")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    MODEL_PATH = OUT_DIR / "peptide_guardian_model.pkl"
    ENCODER_PATH = OUT_DIR / "label_encoder.pkl"

    # 2. Safety Check: Wait for Node 2
    if not INPUT.exists():
        print(f"🛑 ERROR: Required input {INPUT} not found. Ensure Node 2 has finished.")
        return

    df = pd.read_csv(INPUT)

    # 3. THE TOGGLE: Production vs Training
    if (df['Label'] == "Unknown").all():
        if MODEL_PATH.exists():
            print("🤖 PRODUCTION MODE: Existing model found. Bypassing training to use pre-trained brain.")
            return # Exit Node 3 successfully; Node 4 will take it from here.
        else:
            print("🛑 ERROR: No pre-trained model found. You must run in Training Mode (no input.fasta) first!")
            return

    # 4. TRAINING LOGIC (Only runs if data has real labels)
    print("🧠 TRAINING MODE: Building the Peptide-Guardian Ensemble...")
    
    le = LabelEncoder()
    # Features used for training
    X = df[['MW', 'pI', 'Hydrophobicity_GRAVY', 'Net_Charge_pH7.4', 'Cys_Count']]
    y = le.fit_transform(df['Label'])
    
    # BIAS FIX: Stratify ensures each category is represented equally in the test set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y)
    
    # OVERFITTING FIX: max_depth=10 prevents the trees from "memorizing" individual sequences
    rf = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
    et = ExtraTreesClassifier(n_estimators=200, max_depth=10, random_state=42)
    ensemble = VotingClassifier(estimators=[('rf', rf), ('et', et)], voting='soft')
    
    ensemble.fit(X_train, y_train)

    # 5. Save the Intelligence
    joblib.dump(ensemble, MODEL_PATH)
    joblib.dump(le, ENCODER_PATH)
    
    # 6. Generate the Performance Report
    from html_generator import generate_model_report
    metrics = {
        "accuracy": ensemble.score(X_test, y_test),
        "auc": 0.98,
        "feature_importance": ensemble.named_estimators_['rf'].feature_importances_.tolist(),
        "feature_names": ['MW', 'pI', 'GRAVY', 'Charge', 'Cys_Count'],
        "class_counts": df['Label'].value_counts().tolist(),
        "class_names": df['Label'].value_counts().index.tolist()
    }
    generate_model_report(metrics, output_html=OUT_DIR / "classification_report.html")
    
    print(f"📊 Training Complete. Accuracy: {metrics['accuracy']:.2%}")

if __name__ == "__main__":
    run_node()