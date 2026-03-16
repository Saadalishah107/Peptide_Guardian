import pandas as pd
from pathlib import Path
from Bio.SeqUtils.ProtParam import ProteinAnalysis

def run_node():
    INPUT = Path("../a_ingest/outputs/cleaned_sequences.csv")
    OUT_DIR = Path("outputs")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT)
    results = []
    for _, row in df.iterrows():
        try:
            pa = ProteinAnalysis(str(row['Sequence']))
            cys = str(row['Sequence']).count('C')
            results.append({
                "Peptide_ID": row['Peptide_ID'],
                "MW": round(pa.molecular_weight(), 2),
                "pI": round(pa.isoelectric_point(), 2),
                "Hydrophobicity_GRAVY": round(pa.gravy(), 3),
                "Net_Charge_pH7.4": round(pa.charge_at_pH(7.4), 2),
                "Cys_Count": cys,
                "Cyclizable": 1 if cys >= 2 else 0,
                "Label": row['Label']
            })
        except: continue
    
    pd.DataFrame(results).to_csv(OUT_DIR / "peptide_features.csv", index=False)
    # Trigger visual report
    from html_generator import generate_screening_report
    generate_screening_report()

if __name__ == "__main__":
    run_node()