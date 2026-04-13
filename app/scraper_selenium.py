from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

def scrape_maps_selenium(keyword, limit=10):
    """Scrape Google Maps using Selenium (lebih stabil di Windows)"""
    results = []
    
    # Setup Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Hapus ini jika ingin lihat browser
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    try:
        driver.get("https://www.google.com/maps")
        time.sleep(3)
        
        # Cari search box
        search_box = driver.find_element(By.ID, "searchboxinput")
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)
        time.sleep(5)
        
        # Scroll
        for i in range(6):
            driver.execute_script("window.scrollBy(0, 3000)")
            time.sleep(2)
        
        # Cari listing
        listings = driver.find_elements(By.CSS_SELECTOR, 'div[role="article"], div.Nv2PK, a.hfpxzc')
        
        for idx, item in enumerate(listings[:limit]):
            try:
                # Nama
                name_elem = item.find_element(By.CSS_SELECTOR, 'h3, div[role="heading"]')
                name = name_elem.text.strip()
                
                results.append({
                    "Name": name,
                    "Address": "-",
                    "Contact": "-",
                    "Website": "-",
                    "Message": ""
                })
                print(f"Found: {name}")
            except:
                continue
        
    finally:
        driver.quit()
    
    return results

if __name__ == "__main__":
    import sys
    keyword = sys.argv[1] if len(sys.argv) > 1 else "cafe"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    results = scrape_maps_selenium(keyword, limit)
    print(json.dumps(results))