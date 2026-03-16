def generate_final_report(df, output_path):
    # Sort by highest confidence and prioritize Guardian types over Non-AMP
    leads = df[df['Predicted_Type'] != "Non-AMP"].sort_values(by="Confidence", ascending=False)
    
    table_rows = ""
    for _, row in leads.head(15).iterrows():
        status_color = "#27ae60" if row['Cyclizable'] == 1 else "#2980b9"
        table_rows += f"""
        <tr>
            <td><strong>{row['Peptide_ID']}</strong></td>
            <td><span style="color: {status_color}; font-weight: bold;">{row['Predicted_Type']}</span></td>
            <td>{row['Confidence']:.2%}</td>
            <td>{row['Net_Charge_pH7.4']}</td>
            <td>{'✅ Yes' if row['Cyclizable'] == 1 else 'No'}</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Peptide-Guardian | Discovery Report</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; margin: 40px; background: #f4f7f6; color: #333; }}
            .card {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); max-width: 1000px; margin: auto; }}
            h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 25px; }}
            th {{ background: #3498db; color: white; padding: 12px; text-align: left; }}
            td {{ padding: 12px; border-bottom: 1px solid #eee; }}
            .badge {{ padding: 5px 10px; border-radius: 4px; font-size: 0.8em; background: #e8f4fd; color: #3498db; }}
            footer {{ margin-top: 40px; text-align: center; color: #7f8c8d; font-size: 0.8em; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🛡️ Peptide-Guardian Discovery Leads</h1>
            <p>The following sequences have been identified as high-confidence antimicrobial candidates based on the ensemble classification engine.</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Peptide ID</th>
                        <th>Predicted Specialty</th>
                        <th>Confidence</th>
                        <th>Net Charge</th>
                        <th>Cyclizable</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
            
            <footer>
                Confidential Report | Generated for Chiral Collaboration 2026
            </footer>
        </div>
    </body>
    </html>
    """
    with open(output_path, "w") as f:
        f.write(html)