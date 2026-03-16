import os
import pandas as pd
from pathlib import Path
from Bio.SeqUtils.ProtParam import ProteinAnalysis

def run_node():
    print("--- Starting Node 2: Feature Extraction ---")
    
    # Check internal storage first (handoff), then workspace
    internal_in = Path("/tmp/outputs/cleaned_sequences.csv")
    workspace_in = Path("/workspace/01_ingest/outputs/cleaned_sequences.csv")
    
    input_file = internal_in if internal_in.exists() else workspace_in
    
    if not input_file.exists():
        print(f"❌ Error: Input not found in {internal_in} or {workspace_in}")
        return

    print(f"⚙️ Reading data from {input_file}")
    df = pd.read_csv(input_file)
    features = []
    
    for _, row in df.iterrows():
        seq = row['Sequence']
        clean_math = "".join([c for c in seq if c not in "XBZJUO"])
        mw, pi, gravy = None, None, None
        
        if clean_math:
            try:
                analysis = ProteinAnalysis(clean_math)
                mw = round(analysis.molecular_weight(), 2)
                pi = round(analysis.isoelectric_point(), 2)
                gravy = round(analysis.gravy(), 3)
            except: pass
            
        features.append({
            'Peptide_ID': row['Peptide_ID'], 'Sequence': seq,
            'Molecular_Weight': mw, 'Isoelectric_Point': pi, 'GRAVY': gravy
        })
        
    # SAVE TO INTERNAL TMP
    out_dir = Path("/tmp/outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "peptide_features.csv"
    
    pd.DataFrame(features).to_csv(out_file, index=False)
    print(f"✅ Features saved to internal memory: {out_file}")

if __name__ == "__main__":
    run_node()