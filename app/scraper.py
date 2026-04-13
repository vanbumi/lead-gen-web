import subprocess
import sys
import json
import os

def scrape_maps(keyword, limit=10, progress_callback=None):
    """
    Scrape Google Maps dengan memanggil CLI process terpisah
    Ini menghindari event loop conflict di Windows
    """
    
    if progress_callback:
        progress_callback(10, "Starting scraper process...")
    
    # Dapatkan path ke scraper_cli.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    scraper_cli_path = os.path.join(current_dir, "scraper_cli.py")
    
    try:
        # Panggil scraper sebagai process terpisah
        result = subprocess.run(
            [sys.executable, scraper_cli_path, keyword, str(limit)],
            capture_output=True,
            text=True,
            timeout=120  # 2 menit timeout
        )
        
        if progress_callback:
            progress_callback(90, "Processing results...")
        
        if result.returncode == 0 and result.stdout:
            leads = json.loads(result.stdout)
            if progress_callback:
                progress_callback(100, f"Found {len(leads)} leads!")
            return leads
        else:
            if progress_callback:
                progress_callback(100, "No leads found or error occurred")
            return []
            
    except subprocess.TimeoutExpired:
        if progress_callback:
            progress_callback(100, "Scraping timeout (took too long)")
        return []
    except Exception as e:
        if progress_callback:
            progress_callback(100, f"Error: {str(e)[:50]}")
        return []