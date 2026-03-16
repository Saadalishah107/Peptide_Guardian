import pandas as pd
import os

def generate_screening_report(csv_input="outputs/peptide_features.csv", output_html="outputs/screening_report.html"):
    # Silva Rule: Ensure the standard collection folder exists
    os.makedirs("outputs", exist_ok=True)
    
    if not os.path.exists(csv_input):
        print(f"Error: {csv_input} not found.")
        return

    df = pd.read_csv(csv_input)
    
    # Identify top 5 cyclizable leads based on charge and hydrophobicity
    top_leads = df[df['Cyclizable'] == 1].copy()
    top_leads['score'] = top_leads['Net_Charge_pH7.4'] - abs(top_leads['Hydrophobicity_GRAVY'])
    top_leads = top_leads.sort_values(by='score', ascending=False).head(5)
    
    table_rows = "".join([
        f"<tr><td>{r['Peptide_ID']}</td><td>{r['MW']}</td><td>{r['Hydrophobicity_GRAVY']}</td><td>{r['Net_Charge_pH7.4']}</td><td>{r['Label']}</td></tr>" 
        for _, r in top_leads.iterrows()
    ])

    color_map = {"Antibacterial": "#3498db", "Antiviral": "#e74c3c", "Antifungal": "#f1c40f", "Non-AMP": "#bdc3c7"}
    # Use .get() to handle cases where labels might be missing or different
    df['Color'] = df['Label'].apply(lambda x: color_map.get(x, "#bdc3c7"))

    html_content = f"""
    <!DOCTYPE html><html><head><script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body{{font-family:sans-serif; margin:30px; background:#f4f7f6;}} 
        .box{{background:white; padding:20px; border-radius:10px; box-shadow:0 2px 10px rgba(0,0,0,0.1);}} 
        table{{width:100%; border-collapse:collapse; margin-top:20px;}} 
        th{{background:#3498db; color:white; padding:10px; text-align:left;}} 
        td{{padding:10px; border-bottom:1px solid #ddd;}}
    </style></head>
    <body><div class="box"><h1>Peptide-Guardian Screening</h1>
    <div id="scatter" style="height:500px;"></div>
    <div id="pie" style="height:400px;"></div>
    <h3>Top Balanced Leads (Cyclizable)</h3>
    <table><thead><tr><th>ID</th><th>MW</th><th>GRAVY</th><th>Charge</th><th>Type</th></tr></thead><tbody>{table_rows}</tbody></table>
    </div><script>
    Plotly.newPlot('scatter', [{{
        x: {df['Net_Charge_pH7.4'].tolist()}, 
        y: {df['Hydrophobicity_GRAVY'].tolist()}, 
        mode: 'markers', 
        marker: {{color: {df['Color'].tolist()}, size: 10}} 
    }}], {{
        title: 'ADMET Landscape (Charge vs Hydrophobicity)', 
        xaxis: {{title: 'Net Charge (pH 7.4)'}}, 
        yaxis: {{title: 'GRAVY (Hydrophobicity)'}} 
    }});
    
    Plotly.newPlot('pie', [{{
        values: {df['Label'].value_counts().tolist()}, 
        labels: {df['Label'].value_counts().index.tolist()}, 
        type: 'pie'
    }}], {{title: 'Functional Diversity Distribution'}});
    </script></body></html>
    """
    
    with open(output_html, "w") as f: 
        f.write(html_content)
    
    print(f"Success: Visual report generated at {output_html}")