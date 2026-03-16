import pandas as pd
from pathlib import Path
from Bio.SeqUtils.ProtParam import ProteinAnalysis

def run_node():
    # Look directly into Node 1's output folder
    # THIS IS THE SILVA STANDARD PATH
    INPUT_FILE = Path("../01_ingest/outputs/cleaned_sequences.csv")
    OUT_DIR = Path("/workspace/02_features/outputs")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if not INPUT_FILE.exists():
        print(f"❌ Error: Could not find {INPUT_FILE}")
        return

    df = pd.read_csv(INPUT_FILE)
    results = []

    for _, row in df.iterrows():
        # Filter out non-standard AAs for BioPython
        clean_seq = "".join([c for c in row['Sequence'] if c in "ACDEFGHIKLMNPQRSTVWY"])
        if clean_seq:
            analyser = ProteinAnalysis(clean_seq)
            results.append({
                "ID": row['Peptide_ID'],
                "MW": round(analyser.molecular_weight(), 2),
                "pI": round(analyser.isoelectric_point(), 2)
            })

    pd.DataFrame(results).to_csv(OUT_DIR / "peptide_features.csv", index=False)
    print(f"✅ Successfully processed {len(results)} peptides!")

if __name__ == "__main__":
    run_node()