import pandas as pd
import os
import time
from pathlib import Path
from Bio.SeqUtils.ProtParam import ProteinAnalysis

def run_node():
    # FIXED: Relative paths bridge the gap between Node A and Node B cleanly.
    INPUT_FILE = Path("../a_ingest/outputs/cleaned_sequences.csv")
    OUT_DIR = Path("outputs")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Resilient Wait Loop
    for attempt in range(10):
        if INPUT_FILE.exists():
            break
        print(f"⏳ Waiting for Node 1 data at {INPUT_FILE} (Attempt {attempt+1}/10)...")
        time.sleep(5)

    if not INPUT_FILE.exists():
        print(f"🛑 FATAL ERROR: Data not found at {INPUT_FILE}")
        # FIXED: Directory check now looks for 'a_ingest' instead of '01_ingest'
        print(f"Directory check: {os.listdir('../a_ingest/outputs/') if os.path.exists('../a_ingest/outputs/') else 'a_ingest outputs not found'}")
        return

    # Processing 15,000 Sequences
    print(f"✅ Connection Established: Screening {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    results = []

    print(f"🧬 Peptide-Guardian: Calculating ADMET & Cyclization metrics...")
    
    for _, row in df.iterrows():
        seq = str(row['Sequence']).upper()
        # Final safety scrub for non-standard residues
        clean_seq = "".join([c for c in seq if c in "ACDEFGHIKLMNPQRSTVWY"])
        
        if len(clean_seq) >= 10:
            try:
                analyser = ProteinAnalysis(clean_seq)
                cys_count = clean_seq.count('C')
                
                results.append({
                    "Peptide_ID": row['Peptide_ID'],
                    "MW": round(analyser.molecular_weight(), 2),
                    "pI": round(analyser.isoelectric_point(), 2),
                    "Hydrophobicity_GRAVY": round(analyser.gravy(), 3),
                    "Net_Charge_pH7.4": round(analyser.charge_at_pH(7.4), 2),
                    "Cys_Count": cys_count,
                    "Cyclizable": 1 if cys_count >= 2 else 0,
                    "Label": row['Label']
                })
            except:
                continue

    # Direct Save to Local Outputs
    feature_df = pd.DataFrame(results)
    out_path = OUT_DIR / "peptide_features.csv"
    feature_df.to_csv(out_path, index=False)
    
    print(f"✅ SUCCESS: {len(results)} features engineered and saved to sidebar!")

if __name__ == "__main__":
    run_node()