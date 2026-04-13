#!/usr/bin/env python
"""
Scraper CLI - Dipanggil sebagai process terpisah
Usage: python scraper_cli.py "keyword" limit
"""
import sys
import json
import time
from playwright.sync_api import sync_playwright

def scrape_maps_cli(keyword, limit=10):
    """Scrape Google Maps - Versi CLI untuk dipanggil dari subprocess"""
    results = []
    
    print(f"DEBUG: Starting scrape for '{keyword}' with limit {limit}", file=sys.stderr)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("DEBUG: Opening Google Maps...", file=sys.stderr)
        page.goto("https://www.google.com/maps")
        time.sleep(3)
        
        # Search
        print(f"DEBUG: Searching for '{keyword}'...", file=sys.stderr)
        page.keyboard.press("/")
        time.sleep(1)
        page.keyboard.type(keyword)
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(5)
        
        # Scroll
        print("DEBUG: Scrolling...", file=sys.stderr)
        for i in range(6):
            page.mouse.wheel(0, 3000)
            time.sleep(2)
        
        # Ambil listing - MULTIPLE SELECTORS
        print("DEBUG: Looking for listings...", file=sys.stderr)
        
        listing_selectors = [
            'div[role="article"]',
            'div.Nv2PK',
            'a.hfpxzc',
            'div[jsaction*="mouseup"]',
            'div[class*="Nv2PK"]',
            'div[role="feed"] > div',
            '[data-item-id]',
            'div[class*="section-result"]'
        ]
        
        listings = []
        for selector in listing_selectors:
            try:
                temp = page.query_selector_all(selector)
                print(f"DEBUG: Selector '{selector}' -> {len(temp)} items", file=sys.stderr)
                if temp and len(temp) > 0:
                    listings = temp
                    print(f"✅ Using selector: {selector}", file=sys.stderr)
                    break
            except Exception as e:
                print(f"DEBUG: Selector '{selector}' error: {e}", file=sys.stderr)
                continue
        
        if not listings:
            print("DEBUG: No listings found! Saving screenshot...", file=sys.stderr)
            page.screenshot(path="debug_no_listings.png")
            print("DEBUG: Screenshot saved as debug_no_listings.png", file=sys.stderr)
            browser.close()
            return results
        
        print(f"DEBUG: Found {len(listings)} total listings, extracting first {limit}", file=sys.stderr)
        
        # Ekstrak data
        for idx, item in enumerate(listings[:limit]):
            print(f"DEBUG: Processing item {idx+1}/{limit}", file=sys.stderr)
            
            try:
                # NAMA
                name = "-"
                name_selectors = ['h3', 'div[role="heading"]', '.fontHeadlineSmall', 'div[class*="fontHeadline"]', 'span[class*="fontHeadline"]']
                for ns in name_selectors:
                    try:
                        elem = item.query_selector(ns)
                        if elem:
                            name = elem.inner_text().strip()
                            if name and len(name) > 2:
                                print(f"DEBUG: Found name: {name[:50]}", file=sys.stderr)
                                break
                    except:
                        continue
                
                if name == "-":
                    # Coba ambil dari attribute
                    name = item.get_attribute('aria-label')
                    if not name:
                        name = f"Business {idx+1}"
                
                # Klik untuk detail (optional, untuk dapat alamat dll)
                try:
                    item.click()
                    time.sleep(1.5)
                except:
                    pass
                
                # ALAMAT
                address = "-"
                address_selectors = [
                    'button[aria-label*="Address"] div',
                    'div[aria-label*="Address"]',
                    '[data-item-id*="address"]',
                    'div[class*="address"]',
                    'div[class*="W4Efsd"]'
                ]
                for addr_sel in address_selectors:
                    try:
                        addr_elem = page.query_selector(addr_sel)
                        if addr_elem:
                            address = addr_elem.inner_text().strip()
                            if address and len(address) > 5:
                                break
                    except:
                        continue
                
                # CONTACT (Phone)
                contact = "-"
                try:
                    phone_elem = page.query_selector('button[data-item-id*="phone"], a[href^="tel:"]')
                    if phone_elem:
                        phone = phone_elem.get_attribute('aria-label') or phone_elem.inner_text()
                        if phone:
                            phone = phone.replace("Phone", "").strip()
                            contact = f"Phone: {phone}"
                except:
                    pass
                
                # WEBSITE
                website = "-"
                try:
                    web_elem = page.query_selector('a[data-item-id*="website"], a[aria-label*="Website"]')
                    if web_elem:
                        website = web_elem.get_attribute('href')
                        if website and website.startswith('/'):
                            website = "https://www.google.com" + website
                except:
                    pass
                
                results.append({
                    "Name": name,
                    "Address": address,
                    "Contact": contact,
                    "Website": website,
                    "Message": ""
                })
                
                print(f"DEBUG: Added: {name[:40]}", file=sys.stderr)
                time.sleep(0.5)
                
            except Exception as e:
                print(f"DEBUG: Error processing item: {e}", file=sys.stderr)
                continue
        
        browser.close()
    
    print(f"DEBUG: Total results: {len(results)}", file=sys.stderr)
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps([]))
        sys.exit(0)
    
    keyword = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    results = scrape_maps_cli(keyword, limit)
    print(json.dumps(results))