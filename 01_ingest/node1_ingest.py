import os
import csv
import json
import logging
import re
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def run_node():
    # INPUT: Where Silva mounts your files
    INPUT_DIR = Path("/workspace/01_ingest")
    # OUTPUT: Internal container memory (ALWAYS WRITABLE)
    INTERNAL_OUT = Path("/tmp/outputs")
    INTERNAL_OUT.mkdir(parents=True, exist_ok=True)
    
    WORKSPACE_OUT = Path("/workspace/01_ingest/outputs")

    cleaned_data = []
    stats = {"total": 0, "valid": 0}
    valid_aa = set("ACDEFGHIKLMNPQRSTVWYXBZJUO")

    logging.info("Step 1: Reading FASTA from Workspace...")
    fasta_files = list(INPUT_DIR.glob("*.fasta")) + list(INPUT_DIR.glob("*.fa"))
    
    for filepath in fasta_files:
        seq_id, seq_lines = None, []
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                if line.startswith(">"):
                    if seq_id:
                        full_seq = "".join(seq_lines).upper()
                        cleaned = "".join(c if c in valid_aa else "X" for c in full_seq)
                        cleaned_data.append([seq_id, cleaned, len(cleaned)])
                        stats["valid"] += 1
                    seq_id, seq_lines = line[1:], []
                    stats["total"] += 1
                else:
                    seq_lines.append(line)
            # Last record
            if seq_id:
                full_seq = "".join(seq_lines).upper()
                cleaned = "".join(c if c in valid_aa else "X" for c in full_seq)
                cleaned_data.append([seq_id, cleaned, len(cleaned)])
                stats["valid"] += 1

    # SAVE TO INTERNAL TMP (This cannot fail)
    csv_path = INTERNAL_OUT / "cleaned_sequences.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Peptide_ID", "Sequence", "Length"])
        writer.writerows(cleaned_data)
    
    with open(INTERNAL_OUT / "dataset_summary.json", "w") as f:
        json.dump(stats, f)

    logging.info(f"✅ Data saved to internal container memory: {csv_path}")

    # OPTIONAL: Try to copy to workspace (might fail on Fedora, but that's okay)
    try:
        import shutil
        WORKSPACE_OUT.mkdir(parents=True, exist_ok=True)
        shutil.copy(csv_path, WORKSPACE_OUT / "cleaned_sequences.csv")
        logging.info("Successfully mirrored to workspace.")
    except:
        logging.warning("Mirroring to workspace failed (Permission). Use the Shadow Rescue method.")

if __name__ == "__main__":
    run_node()