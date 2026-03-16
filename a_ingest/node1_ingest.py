import pandas as pd
import os
from pathlib import Path

def run_node():
    # Setup directory
    out_dir = Path("results")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Input file from local directory
    input_file = "input.fasta"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    print(f"Processing {input_file}...")
    
    sequences = []
    current_seq = ""
    
    with open(input_file, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if current_seq:
                    sequences.append(current_seq)
                current_seq = ""
            else:
                current_seq += line
        if current_seq:
            sequences.append(current_seq)

    # Simple cleaning and saving
    df = pd.DataFrame({"Sequence": sequences})
    df['Sequence'] = df['Sequence'].str.upper().str.replace(r'[^A-Z]', '', regex=True)
    
    output_path = out_dir / "cleaned_sequences.csv"
    df.to_csv(output_path, index=False)
    
    print(f"Success: {len(df)} sequences saved to {output_path}")

if __name__ == "__main__":
    run_node()