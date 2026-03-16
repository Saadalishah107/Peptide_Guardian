import pandas as pd
from pathlib import Path
from Bio import SeqIO
import requests, io, time, logging
import os

# Configure logging for better visibility in Silva logs
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def get_uniprot_data(query, target_count=5000):
    all_records = []
    # Using the current REST API format for UniProt
    url = f"https://rest.uniprot.org/uniprotkb/search?query={query}&format=fasta&size=500"
    
    while len(all_records) < target_count:
        try:
            # Add offset for pagination
            res = requests.get(f"{url}&offset={len(all_records)}", timeout=30)
            res.raise_for_status()
            
            batch = list(SeqIO.parse(io.StringIO(res.text), "fasta"))
            if not batch:
                break
            
            for r in batch:
                seq = str(r.seq).upper()
                # Scientific Filter: Standard Amino Acids only and meaningful length
                if all(a in "ACDEFGHIKLMNPQRSTVWY" for a in seq) and len(seq) >= 10:
                    all_records.append([r.id, seq])
                if len(all_records) >= target_count:
                    break
            
            logging.info(f"   Collected {len(all_records)}/{target_count}")
            time.sleep(1) # Polite delay to prevent API blocking
        except Exception as e:
            logging.error(f"⚠️ UniProt fetch interrupted: {e}")
            break
    return all_records

def run_node():
    # --- ROBUST PATHING SECTION ---
    # This ensures the script finds 'input.fasta' regardless of where 'silva .' is called from
    base_dir = Path(__file__).resolve().parent
    OUT_DIR = base_dir / "outputs"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    user_file = base_dir / "input.fasta"
    out_file = OUT_DIR / "cleaned_sequences.csv"
    
    records = []

    # --- MODE DETECTION ---
    if user_file.exists():
        print(f"🚀 PRODUCTION MODE DETECTED: Processing {user_file.name}")
        try:
            for r in SeqIO.parse(user_file, "fasta"):
                seq = str(r.seq).upper()
                # Apply the same cleaning rules as training data
                if all(a in "ACDEFGHIKLMNPQRSTVWY" for a in seq) and len(seq) >= 10:
                    # Label as 'Unknown' for downstream Node 3 prediction
                    records.append([r.id, seq, "Unknown"])
        except Exception as e:
            print(f"🛑 Error reading user FASTA: {e}")
            return
    else:
        print("🧪 TRAINING MODE: 'input.fasta' not found. Harvesting 20,000 sequences from UniProt...")
        categories = {
            "Antibacterial": "keyword:KW-0046 length:[10 TO 50]",
            "Antiviral": "keyword:KW-0044 length:[10 TO 50]",
            "Antifungal": "keyword:KW-0048 length:[10 TO 50]",
            "Non-AMP": "taxonomy_id:9606 NOT keyword:KW-0046 NOT keyword:KW-0044 NOT keyword:KW-0048 length:[10 TO 50]"
        }
        
        for label, q in categories.items():
            print(f"📡 Harvesting {label} category...")
            data = get_uniprot_data(q, target_count=5000)
            for r in data:
                records.append([r[0], r[1], label])
            
    # --- DATA INTEGRITY & SAVING ---
    if not records:
        print("⚠️ No data collected. Check internet connection or FASTA format.")
        return

    df = pd.DataFrame(records, columns=["Peptide_ID", "Sequence", "Label"])
    
    # BIAS FIX: Drop duplicates to prevent the model from "cheating"
    original_count = len(df)
    df = df.drop_duplicates(subset=['Sequence'])
    
    if len(df) < original_count:
        print(f"🧹 Removed {original_count - len(df)} duplicate sequences.")

    df.to_csv(out_file, index=False)
    print(f"✅ SUCCESS: {len(df)} sequences saved to {out_file.name}")

if __name__ == "__main__":
    run_node()