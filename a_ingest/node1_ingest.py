import pandas as pd
import os
import json
from pathlib import Path

def load_params():
    """Silva Guide Step 5.5: Load global parameters to find input filename."""
    global_params = {}
    # Silva mounts global_params.json into the inputs folder of the node
    params_path = Path("inputs/global_params.json")
    if params_path.exists():
        with open(params_path) as f:
            global_params = json.load(f)
    return global_params

def run_node():
    # Load parameters to see which file the user wants to process
    global_params = load_params()
    
    # Logic: 1. Check global_params, 2. Check ./inputs/, 3. Fallback to root
    filename = global_params.get("input_file", "input.fasta")
    
    # Priority path for Silva execution
    input_path = Path("inputs") / filename
    
    # Local fallback for manual testing
    if not input_path.exists():
        input_path = Path(filename)

    if not input_path.exists():
        print(f"Error: Input file '{filename}' not found in ./inputs/ or job root.")
        return

    print(f"Processing sequence data from: {input_path}")
    
    headers = []
    sequences = []
    current_seq = ""
    current_header = ""
    
    with open(input_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            if line.startswith(">"):
                if current_seq:
                    sequences.append(current_seq)
                    headers.append(current_header)
                current_header = line
                current_seq = ""
            else:
                current_seq += line
        if current_seq:
            sequences.append(current_seq)
            headers.append(current_header)

    # Structure data for the Peptide-Guardian pipeline
    df = pd.DataFrame({
        "Original_Header": headers,
        "Sequence": sequences
    })
    
    df.insert(0, 'Peptide_ID', [f"P-{i+1:04d}" for i in range(len(df))])
    df['Sequence'] = df['Sequence'].str.upper().str.replace(r'[^A-Z]', '', regex=True)
    
    # --- BUG FIX OVERRIDE: Assign Label based on FASTA header ---
    def assign_label(header):
        header_lower = header.lower()
        if 'unknown' in header_lower:
            return 'Unknown'
        elif 'non-amp' in header_lower or 'decoy' in header_lower:
            return 'Non-AMP'
        else:
            return 'AMP' # Defaults known sequences (Magainin, etc.) to AMP

    df['Label'] = df['Original_Header'].apply(assign_label)
    # Extracts the clean peptide name (e.g., Magainin_2 from >seq_01|Magainin_2)
    df['Peptide_Name'] = df['Original_Header'].apply(lambda x: x.split('|')[-1] if '|' in x else x)
    # ------------------------------------------------------------
    
    #  CRITICAL FIX: Save directly to the root directory (no outputs/ folder)
    output_file = "cleaned_sequences.csv"
    df.to_csv(output_file, index=False)
    
    print(f"Success: {len(df)} sequences staged for feature engineering.")

if __name__ == "__main__":
    run_node()