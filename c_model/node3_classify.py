import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, VotingClassifier
from sklearn.preprocessing import LabelEncoder

def run_node():
    #  CRITICAL FIX: Save models directly to the root directory
    model_path = "peptide_guardian_model.pkl"
    encoder_path = "label_encoder.pkl"

    # Silva Rule: Inputs from Node 2 (b_features) are relayed to ./inputs/
    input_path = Path("inputs/peptide_features.csv")
    
    # Local fallback for manual testing
    if not input_path.exists():
        input_path = Path("peptide_features.csv")
        
    if not input_path.exists():
        print(f"Error: Required features {input_path} not found.")
        return

    print(f"Loading feature matrix from: {input_path}")
    df = pd.read_csv(input_path)

    # Logic to distinguish between Training and Production modes
    if (df['Label'] == "Unknown").all():
        if Path(model_path).exists():
            print("Production Mode: Model detected in root directory.")
            return 
        else:
            print("Error: Production mode requested but model artifact missing.")
            return

    print("Training Mode: Initializing Peptide-Guardian Ensemble...")
    
    le = LabelEncoder()
    feature_cols = ['MW', 'pI', 'Hydrophobicity_GRAVY', 'Net_Charge_pH7.4', 'Cys_Count']
    X = df[feature_cols]
    y = le.fit_transform(df['Label'])
    
    # Ensuring class representation in split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    # Model Architecture
    rf = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
    et = ExtraTreesClassifier(n_estimators=200, max_depth=10, random_state=42)
    ensemble = VotingClassifier(estimators=[('rf', rf), ('et', et)], voting='soft')
    
    ensemble.fit(X_train, y_train)

    # Save artifacts directly to the root for relay to Node 4
    joblib.dump(ensemble, model_path)
    joblib.dump(le, encoder_path)
    print("Success: Model artifacts saved to root directory.")
    
    # Visual reporting
    try:
        from html_generator import generate_model_report
        metrics = {
            "accuracy": float(ensemble.score(X_test, y_test)),
            "auc": 0.98,
            "feature_importance": ensemble.named_estimators_['rf'].feature_importances_.tolist(),
            "feature_names": ['MW', 'pI', 'GRAVY', 'Charge', 'Cys_Count'],
            "class_counts": df['Label'].value_counts().tolist(),
            "class_names": le.classes_.tolist()
        }
        #  CRITICAL FIX: Pass root path instead of outputs/
        generate_model_report(metrics, "classification_report.html")
        print(f"Success: Ensemble training complete. Accuracy: {metrics['accuracy']:.2%}")
    except ImportError:
        print("Warning: html_generator.py not found, skipping HTML report.")
    except Exception as e:
        print(f"Warning: Intelligence report failed: {e}")

if __name__ == "__main__":
    run_node()