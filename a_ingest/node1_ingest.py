import csv, logging, requests, io, time
from pathlib import Path
from Bio import SeqIO
from urllib.parse import quote

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def get_filtered_uniprot_data(query, target_count=7500):
    all_records = []
    encoded_query = quote(query)
    standard_aas = set("ACDEFGHIKLMNPQRSTVWY")
    
    logging.info(f"🔍 Harvesting: {query}")
    
    while len(all_records) < target_count:
        size = 500
        url = f"https://rest.uniprot.org/uniprotkb/search?query={encoded_query}&format=fasta&size={size}&offset={len(all_records)}"
        
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            batch = list(SeqIO.parse(io.StringIO(response.text), "fasta"))
            if not batch: break
            
            valid_batch_count = 0
            for r in batch:
                seq = str(r.seq).upper()
                # REGEX-FREE FILTERING: Ensure sequence only contains standard 20 amino acids
                if all(amino in standard_aas for amino in seq) and len(seq) >= 10:
                    all_records.append([r.id, seq])
                    valid_batch_count += 1
                
                if len(all_records) >= target_count: break
            
            logging.info(f"   📥 Cleaned Progress: {len(all_records)}/{target_count}")
            if len(batch) < size: break # No more results available
            
            time.sleep(1) # API Courtesy
            
        except Exception as e:
            logging.error(f"⚠️ Connection glitch: {e}. Retrying...")
            time.sleep(5)
            continue
            
    return all_records

def run_node():
    # FIXED: Using a relative local path. Silva will collect this folder perfectly.
    OUT_DIR = Path("outputs")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUT_DIR / "cleaned_sequences.csv"
    
    TARGET_PER_SIDE = 7500 
    
    # 1. Positives (AMPs)
    pos_data = get_filtered_uniprot_data("antimicrobial AND length:[10 TO 50]", target_count=TARGET_PER_SIDE)
    
    # 2. Negatives (Human Non-AMPs)
    neg_data = get_filtered_uniprot_data("taxonomy_id:9606 NOT antimicrobial AND length:[10 TO 50]", target_count=TARGET_PER_SIDE)
    
    cleaned_rows = []
    for r in pos_data: cleaned_rows.append([r[0], r[1], 1])
    for r in neg_data: cleaned_rows.append([r[0], r[1], 0])
            
    with open(out_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Peptide_ID", "Sequence", "Label"])
        writer.writerows(cleaned_rows)
            
    logging.info(f"🏆 15k HARVEST COMPLETE: {len(cleaned_rows)} high-quality samples saved.")

if __name__ == "__main__":
    run_node()