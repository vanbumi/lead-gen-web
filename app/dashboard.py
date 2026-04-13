import streamlit as st
import pandas as pd
import time
import os
from datetime import datetime
from message_generator import generate_message
from utils import save_to_excel
from database import init_db, save_to_history, get_history, delete_history_item, get_total_stats
from playwright.sync_api import sync_playwright

# Page config
st.set_page_config(
    page_title="LeadGen Pro - Google Maps Scraper",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #ff6b6b;
    }
    @media (max-width: 768px) {
        .stMarkdown h1 {
            font-size: 24px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database
init_db()

# Header
st.markdown("# 🔍 LeadGen Pro")
st.markdown("### Extract leads from Google Maps + AI Outreach Messages")

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    generate_msgs = st.checkbox("💬 Generate AI Messages", value=True)
    st.markdown("---")
    stats = get_total_stats()
    st.metric("Total Leads", stats['total_leads'])
    st.metric("Total Scrapes", stats['total_scrapes'])
    st.markdown("---")
    st.caption("Made with ❤️ by LeadGen Pro")

def scrape_maps_playwright(keyword, limit=10, progress_callback=None):
    """Scrape Google Maps menggunakan Playwright"""
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        if progress_callback:
            progress_callback(10, "Opening Google Maps...")
        
        page.goto("https://www.google.com/maps")
        time.sleep(3)
        
        # Search
        if progress_callback:
            progress_callback(20, f"Searching for '{keyword}'...")
        
        page.keyboard.press("/")
        time.sleep(1)
        page.keyboard.type(keyword)
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(5)
        
        # Scroll untuk load lebih banyak
        for i in range(4):
            page.mouse.wheel(0, 3000)
            time.sleep(1.5)
            if progress_callback:
                progress_callback(20 + (i * 10), f"Scrolling... ({i+1}/4)")
        
        # Ambil listing bisnis
        listing_selectors = [
            'div[role="article"]',
            'div.Nv2PK',
            'a.hfpxzc'
        ]
        
        listings = []
        for selector in listing_selectors:
            try:
                temp = page.query_selector_all(selector)
                if temp and len(temp) > 0:
                    listings = temp
                    break
            except:
                continue
        
        if not listings:
            browser.close()
            return []
        
        # Ekstrak data
        for idx, item in enumerate(listings[:limit]):
            if progress_callback:
                progress_callback(50 + (idx * (50/limit)), f"Processing business {idx+1}/{limit}...")
            
            try:
                # Ambil nama
                name = "-"
                name_selectors = ['h3', 'div[role="heading"]', '.fontHeadlineSmall']
                for ns in name_selectors:
                    try:
                        elem = item.query_selector(ns)
                        if elem:
                            name = elem.inner_text().strip()
                            if name:
                                break
                    except:
                        continue
                
                # Klik untuk detail (opsional)
                try:
                    item.click()
                    time.sleep(1)
                except:
                    pass
                
                # Ambil alamat
                address = "-"
                address_selectors = [
                    'button[aria-label*="Address"] div',
                    'div[aria-label*="Address"]',
                    '[data-item-id*="address"]'
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
                
                # Ambil telepon
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
                
                # Ambil website
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
                    "Name": name if name != "-" else f"Business {idx+1}",
                    "Address": address,
                    "Contact": contact,
                    "Website": website,
                    "Message": ""
                })
                
                time.sleep(0.5)
                
            except Exception as e:
                continue
        
        browser.close()
    
    if progress_callback:
        progress_callback(100, f"Found {len(results)} leads!")
    
    return results

# Main tabs
tab1, tab2 = st.tabs(["🎯 New Scrape", "📜 History"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        keyword = st.text_input("Enter keyword:", placeholder="e.g., cafe in bandung, barbershop in sydney")
        limit = st.select_slider("Number of leads:", options=[5, 10, 20, 30, 50], value=10)
    
    with col2:
        st.info("💡 **Pro Tips**\n• Use specific keywords\n• Add location\n• Try different variations")
    
    if keyword and st.button("▶️ START SCRAPING", use_container_width=True, type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(percent, message):
            progress_bar.progress(int(percent))
            status_text.text(message)
        
        try:
            leads = scrape_maps_playwright(keyword, limit=limit, progress_callback=update_progress)
            
            if leads:
                if generate_msgs:
                    msg_bar = st.progress(0)
                    for idx, lead in enumerate(leads):
                        lead['Message'] = generate_message(lead['Name'])
                        msg_bar.progress((idx+1)/len(leads))
                    msg_bar.empty()
                else:
                    for lead in leads:
                        lead['Message'] = "-"
                
                filepath = save_to_excel(leads, keyword)
                if filepath:
                    filename = os.path.basename(filepath)
                    save_to_history(keyword, len(leads), filename)
                    
                    st.success(f"✅ Found {len(leads)} leads!")
                    
                    with open(filepath, "rb") as f:
                        st.download_button(
                            label=f"📥 Download {filename}",
                            data=f,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                    with st.expander("🔍 Preview first 5 leads"):
                        st.dataframe(pd.DataFrame(leads[:5]), use_container_width=True)
            else:
                st.warning(f"⚠️ No leads found for '{keyword}'")
                
        except Exception as e:
            st.error(f"Scraping error: {e}")
            st.code(str(e))
        
        progress_bar.empty()
        status_text.empty()
        st.balloons()

with tab2:
    st.markdown("## 📜 Scraping History")
    history = get_history(50)
    
    if history:
        for item in history:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**🔑 {item['keyword']}**")
                st.caption(f"📅 {item['created_at']} • {item['leads_count']} leads")
            with col2:
                filepath = f"output/{item['filename']}"
                if os.path.exists(filepath):
                    with open(filepath, "rb") as f:
                        st.download_button(
                            "📥 Download", 
                            data=f, 
                            file_name=item['filename'], 
                            key=f"history_{item['id']}"
                        )
            with col3:
                if st.button("🗑️ Delete", key=f"del_{item['id']}"):
                    delete_history_item(item['id'])
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    st.rerun()
            st.markdown("---")
    else:
        st.info("No scraping history yet.")
