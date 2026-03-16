import csv, logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def run_node():
    # Use relative paths to match the Chiral standard perfectly
    BASE_DIR = Path(".")
    OUT_DIR = Path("outputs")
    
    # Ensure the outputs directory exists
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    cleaned_data = []
    fasta_files = list(BASE_DIR.glob("*.fasta")) + list(BASE_DIR.glob("*.fa"))
    
    logging.info(f"Found {len(fasta_files)} FASTA files.")

    for filepath in fasta_files:
        seq_id, seq_lines = None, []
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith(">"):
                    if seq_id:
                        cleaned_data.append([seq_id, "".join(seq_lines).upper()])
                    seq_id, seq_lines = line[1:], []
                else:
                    seq_lines.append(line)
            if seq_id: # Last one
                cleaned_data.append([seq_id, "".join(seq_lines).upper()])

    # Save directly to the output folder
    out_file = OUT_DIR / "cleaned_sequences.csv"
    with open(out_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Peptide_ID", "Sequence"])
        writer.writerows(cleaned_data)
    
    logging.info(f"✅ Ingested {len(cleaned_data)} sequences to {out_file}")

if __name__ == "__main__":
    run_node()