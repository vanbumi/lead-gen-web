import streamlit as st
import pandas as pd
import time
import os
from scraper import scrape_maps
from message_generator import generate_message
from utils import save_to_excel, generate_filename
from database import init_db, save_to_history, get_history, delete_history_item, get_total_stats

# Page config
st.set_page_config(
    page_title="LeadGen Pro - Google Maps Scraper",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile friendly
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
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-radius: 10px;
        border-left: 5px solid #28a745;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-radius: 10px;
        border-left: 5px solid #17a2b8;
    }
    @media (max-width: 768px) {
        .stMarkdown h1 {
            font-size: 24px !important;
        }
        .stMarkdown h2 {
            font-size: 20px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database
init_db()

# Header
col_title, col_logo = st.columns([4, 1])
with col_title:
    st.markdown("# 🔍 LeadGen Pro")
    st.markdown("### Extract leads from Google Maps + AI Outreach Messages")
with col_logo:
    st.markdown("")
    st.markdown("")
    st.caption("v1.0.0")

# Sidebar for settings
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    generate_msgs = st.checkbox("💬 Generate AI Messages", value=True)
    
    if generate_msgs:
        st.caption("Using Groq AI (Llama 3.3)")
    
    st.markdown("---")
    st.markdown("### 📊 Statistics")
    
    stats = get_total_stats()
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Leads", stats['total_leads'])
    with col2:
        st.metric("Total Scrapes", stats['total_scrapes'])
    
    st.markdown("---")
    st.caption("Made with ❤️ by LeadGen Pro")

# Main content
tab1, tab2 = st.tabs(["🎯 New Scrape", "📜 History"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 🎯 Target Your Leads")
        
        input_method = st.radio(
            "Choose input method:",
            ["Single Keyword", "Batch Upload (CSV/TXT)"],
            horizontal=True
        )
        
        keywords_list = []
        
        if input_method == "Single Keyword":
            keyword = st.text_input(
                "Enter keyword:", 
                placeholder="e.g., cafe in bandung, hospital in jakarta, hotel in bali"
            )
            if keyword:
                keywords_list = [keyword]
        else:
            uploaded_file = st.file_uploader(
                "Upload keywords file", 
                type=['txt', 'csv'],
                help="One keyword per line"
            )
            if uploaded_file:
                content = uploaded_file.read().decode('utf-8')
                keywords_list = [line.strip() for line in content.split('\n') if line.strip()]
                st.success(f"✅ {len(keywords_list)} keywords loaded")
                for kw in keywords_list[:5]:
                    st.caption(f"• {kw}")
                if len(keywords_list) > 5:
                    st.caption(f"... and {len(keywords_list)-5} more")
        
        # Limit selection
        limit = st.select_slider(
            "Number of leads per keyword:",
            options=[5, 10, 20, 30, 50],
            value=10
        )
    
    with col2:
        st.markdown("## 💡 Pro Tips")
        st.info("""
        **Best Practices:**
        • Use specific keywords
        • Add location: "cafe di bandung"
        • Try different variations
        • Batch upload for multiple cities
        """)
        
        st.markdown("**Example Keywords:**")
        st.code("""
cafe di bandung utara
hospital in jakarta
restaurant in bali
hotel di surabaya
        """)
    
    # Scraping section
    if keywords_list:
        st.markdown("---")
        st.markdown("## 🚀 Start Scraping")
        
        if st.button("▶️ START SCRAPING", use_container_width=True, type="primary"):
            
            all_results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for kw_idx, keyword in enumerate(keywords_list):
                st.markdown(f"### 📍 {keyword}")
                
                # Progress callback
                def update_progress(percent, message):
                    overall_progress = (kw_idx + (percent/100)) / len(keywords_list)
                    progress_bar.progress(overall_progress)
                    status_text.text(f"[{kw_idx+1}/{len(keywords_list)}] {message}")
                
                # Scrape
                try:
                    with st.spinner(f"Scraping '{keyword}'..."):
                        leads = scrape_maps(keyword, limit=limit, progress_callback=update_progress)
                        
                    # Tambahkan debug info
                    st.info(f"Debug: Raw result type = {type(leads)}, length = {len(leads) if leads else 0}")
                except Exception as e:
                    st.error(f"Scraping error: {e}")
                    leads = []
                
                if leads:
                    # Generate messages if needed
                    if generate_msgs:
                        msg_progress = st.progress(0)
                        msg_text = st.empty()
                        for idx, lead in enumerate(leads):
                            msg_text.text(f"Generating message for {lead['Name'][:30]}...")
                            lead['Message'] = generate_message(lead['Name'])
                            msg_progress.progress((idx+1)/len(leads))
                        msg_progress.empty()
                        msg_text.empty()
                    else:
                        for lead in leads:
                            lead['Message'] = "-"
                    
                    # Save to Excel
                    filepath = save_to_excel(leads, keyword)
                    
                    if filepath:
                        filename = os.path.basename(filepath)
                        save_to_history(keyword, len(leads), filename)
                        
                        # Show success message
                        st.success(f"✅ Found {len(leads)} leads!")
                        
                        # Download button
                        with open(filepath, "rb") as f:
                            st.download_button(
                                label=f"📥 Download {filename}",
                                data=f,
                                file_name=filename,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"download_result_{kw_idx}_{int(time.time())}"
                            )
                        
                        # Preview table
                        with st.expander(f"🔍 Preview first 5 leads"):
                            preview_df = pd.DataFrame(leads[:5])
                            st.dataframe(preview_df, use_container_width=True)
                    else:
                        st.error(f"❌ Failed to save file for '{keyword}'")
                else:
                    st.warning(f"⚠️ No leads found for '{keyword}'")
                
                st.markdown("---")
            
            progress_bar.empty()
            status_text.empty()
            st.balloons()
            st.success("🎉 ALL SCRAPING COMPLETE! Check downloads above.")
            st.audio("https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3", format="audio/mp3", autoplay=True)

with tab2:
    st.markdown("## 📜 Scraping History")
    
    history = get_history(50)
    
    if history:
        for item in history:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**🔑 {item['keyword']}**")
                    st.caption(f"📅 {item['created_at']} • {item['leads_count']} leads")
                
                with col2:
                    filename = item['filename']
                    filepath = f"output/{filename}"
                    
                    if os.path.exists(filepath):
                        with open(filepath, "rb") as f:
                            st.download_button(
                                label="📥 Download",
                                data=f,
                                file_name=filename,
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"history_download_{item['id']}"
                            )
                    else:
                        st.caption("File missing")
                
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{item['id']}"):
                        delete_history_item(item['id'])
                        if os.path.exists(filepath):
                            os.remove(filepath)
                        st.rerun()
                
                st.markdown("---")
    else:
        st.info("No scraping history yet. Start your first scrape in the 'New Scrape' tab!")

# Footer
st.markdown("---")
st.caption("💡 Tip: Use specific keywords like 'cafe di bandung utara' for better results")