import pandas as pd
from pathlib import Path
from Bio.SeqUtils.ProtParam import ProteinAnalysis
import os

def find_file(filename, search_path=".."):
    for root, dirs, files in os.walk(search_path):
        if filename in files:
            return os.path.join(root, filename)
    return None

def run_node():
    out_dir = Path("results")
    out_dir.mkdir(parents=True, exist_ok=True)

    input_path = Path("inputs/cleaned_sequences.csv")
    
    if not input_path.exists():
        found = find_file("cleaned_sequences.csv")
        if found:
            input_path = Path(found)
        else:
            print(f"Error: Cannot find {input_path}")
            return

    print(f"Loading input: {input_path}")
    df = pd.read_csv(input_path)
    results = []
    
    print(f"Calculating biophysical features for {len(df)} sequences...")
    
    for _, row in df.iterrows():
        try:
            seq_str = str(row['Sequence'])
            pa = ProteinAnalysis(seq_str)
            cys = seq_str.count('C')
            results.append({
                "Peptide_ID": row.get('Peptide_ID', 'Unknown'),
                "MW": round(pa.molecular_weight(), 2),
                "pI": round(pa.isoelectric_point(), 2),
                "Hydrophobicity_GRAVY": round(pa.gravy(), 3),
                "Net_Charge_pH7.4": round(pa.charge_at_pH(7.4), 2),
                "Cys_Count": cys,
                "Cyclizable": 1 if cys >= 2 else 0,
                "Label": row.get('Label', 'Non-AMP')
            })
        except Exception as e:
            continue
    
    feature_file = out_dir / "peptide_features.csv"
    pd.DataFrame(results).to_csv(feature_file, index=False)
    
    print(f"Success: Features saved to {feature_file}")
    
    try:
        from html_generator import generate_screening_report
        # Passing explicit paths to ensure the generator uses 'results'
        generate_screening_report(
            csv_input=str(feature_file),
            output_html=str(out_dir / "screening_report.html")
        )
        print("Visual report successfully saved to results/screening_report.html")
    except Exception as e:
        print(f"Warning: Visual report failed: {e}")

if __name__ == "__main__":
    run_node()