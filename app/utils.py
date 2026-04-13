import os
import pandas as pd
from datetime import datetime
import re

def ensure_output_folder():
    """Buat folder output/ jika belum ada"""
    if not os.path.exists("output"):
        os.makedirs("output")
    return "output"

def clean_filename(keyword):
    """
    Bersihkan keyword untuk jadi nama file
    Contoh: "cafe di bandung" → "cafe_di_bandung"
    """
    clean = keyword.lower()
    clean = clean.replace(" ", "_")
    clean = re.sub(r'[^a-z0-9_]', '', clean)
    clean = re.sub(r'_+', '_', clean)
    clean = clean.strip('_')
    return clean

def generate_filename(keyword, extension=".xlsx"):
    """
    Generate filename profesional
    Contoh: cafe_di_bandung_leads_20260112_143022.xlsx
    """
    keyword_clean = clean_filename(keyword)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{keyword_clean}_leads_{timestamp}{extension}"
    return filename

def save_to_excel(data, keyword):
    """Simpan ke Excel dengan filename dari keyword"""
    ensure_output_folder()
    
    columns = ['Name', 'Address', 'Contact', 'Website', 'Message']
    
    if not data:
        df = pd.DataFrame(columns=columns)
    else:
        df = pd.DataFrame(data)
        for col in columns:
            if col not in df.columns:
                df[col] = "-"
    
    df = df[columns]
    
    filename = generate_filename(keyword, ".xlsx")
    filepath = os.path.join("output", filename)
    
    try:
        from openpyxl.utils import get_column_letter
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Leads', index=False)
            
            # Auto-adjust column width
            worksheet = writer.sheets['Leads']
            for column in worksheet.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        return filepath
    except Exception as e:
        print(f"Error saving Excel: {e}")
        return None