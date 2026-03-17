import pandas as pd
from pathlib import Path
from Bio.SeqUtils.ProtParam import ProteinAnalysis

def run_node():
    # Silva Rule: Inputs are staged directly in ./inputs/ based on your @job.toml
    input_path = Path("inputs/cleaned_sequences.csv")
    
    # Local fallback for manual testing outside of Docker
    if not input_path.exists():
        input_path = Path("cleaned_sequences.csv")

    if not input_path.exists():
        print(f"Error: Required input {input_path} not found.")
        return

    print(f"Loading relayed sequences from: {input_path}")
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
                "Sequence": seq_str, # Keep sequence for Node 4 report
                "MW": round(pa.molecular_weight(), 2),
                "pI": round(pa.isoelectric_point(), 2),
                "Hydrophobicity_GRAVY": round(pa.gravy(), 3),
                "Net_Charge_pH7.4": round(pa.charge_at_pH(7.4), 2),
                "Cys_Count": cys,
                "Cyclizable": 1 if cys >= 2 else 0,
                "Label": row.get('Label', 'Non-AMP')
            })
        except Exception:
            # Skip invalid sequences silently to keep logs clean
            continue
    
    #  CRITICAL FIX: Save directly to the root directory (no outputs/ folder)
    feature_file = "peptide_features.csv"
    pd.DataFrame(results).to_csv(feature_file, index=False)
    
    print(f"Success: Features staged at {feature_file}")
    
    # Visual reporting
    try:
        from html_generator import generate_screening_report
        # ✨ CRITICAL FIX: Pass root paths instead of outputs/
        generate_screening_report(
            csv_input=feature_file,
            output_html="screening_report.html"
        )
        print("Success: Screening report generated in root directory")
    except ImportError:
        print("Warning: html_generator.py not found, skipping HTML report.")
    except Exception as e:
        print(f"Warning: HTML generator failed: {e}")

if __name__ == "__main__":
    run_node()