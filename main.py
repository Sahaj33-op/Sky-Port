import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
from io import BytesIO
import base64
from typing import Optional, Dict, Any

# Import our custom modules
from api.hypixel import HypixelAPI
from api.mojang import MojangAPI
from processors.profile_processor import ProfileProcessor
from exporters.excel_exporter import ExcelExporter
from exporters.pdf_exporter import PDFExporter
from exporters.csv_exporter import CSVExporter
from exporters.json_exporter import JSONExporter
from utils.cache import CacheManager
from utils.rate_limiter import RateLimiter

# Page configuration
st.set_page_config(
    page_title="Sky-Port | Hypixel SkyBlock Profile Exporter",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for minimalist UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f1f1f;
        margin-bottom: 2rem;
    }
    .stButton > button {
        width: 100%;
        margin: 0.25rem 0;
    }
    .export-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .data-preview {
        max-height: 400px;
        overflow-y: auto;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    if 'profile_data' not in st.session_state:
        st.session_state.profile_data = None
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'player_uuid' not in st.session_state:
        st.session_state.player_uuid = None
    if 'selected_profile' not in st.session_state:
        st.session_state.selected_profile = None

def main():
    init_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">⚡ Sky-Port</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Comprehensive Hypixel SkyBlock Profile Data Exporter</p>', unsafe_allow_html=True)
    
    # Sidebar for inputs and configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Hypixel API Key",
            type="password",
            help="Get your API key from /api new in-game"
        )
        
        if not api_key:
            st.warning("Please enter your Hypixel API key to continue")
            return
        
        st.divider()
        
        # Player input
        st.subheader("👤 Player Lookup")
        player_input = st.text_input(
            "Username or UUID",
            placeholder="Enter Minecraft username"
        )
        
        fetch_button = st.button("🔍 Fetch Player Data", type="primary")
        
        # Initialize APIs
        hypixel_api = HypixelAPI(api_key)
        mojang_api = MojangAPI()
        
        if fetch_button and player_input:
            with st.spinner("Fetching player data..."):
                try:
                    # Get UUID if username provided
                    if len(player_input) != 32:  # Not a UUID
                        uuid_data = mojang_api.get_uuid(player_input)
                        if not uuid_data:
                            st.error("Player not found!")
                            return
                        player_uuid = uuid_data['id']
                        st.session_state.player_uuid = player_uuid
                    else:
                        st.session_state.player_uuid = player_input
                    
                    # Fetch SkyBlock profiles
                    profiles = hypixel_api.get_skyblock_profiles(st.session_state.player_uuid)
                    
                    if not profiles or 'profiles' not in profiles:
                        st.error("No SkyBlock profiles found for this player!")
                        return
                    
                    st.session_state.profile_data = profiles
                    st.success(f"Found {len(profiles['profiles'])} profile(s)!")
                    
                except Exception as e:
                    st.error(f"Error fetching data: {str(e)}")
        
        # Profile selection
        if st.session_state.profile_data:
            st.divider()
            st.subheader("📋 Select Profile")
            
            profiles = st.session_state.profile_data['profiles']
            profile_options = {}
            
            for profile in profiles:
                name = profile.get('cute_name', 'Unnamed Profile')
                game_mode = profile.get('game_mode', 'Normal')
                last_save = datetime.fromtimestamp(profile.get('last_save', 0) / 1000)
                profile_options[f"{name} ({game_mode}) - {last_save.strftime('%Y-%m-%d')}"] = profile
            
            selected_profile_key = st.selectbox(
                "Choose a profile:",
                options=list(profile_options.keys())
            )
            
            if selected_profile_key:
                st.session_state.selected_profile = profile_options[selected_profile_key]
                st.success("Profile selected!")
    
    # Main content area
    if st.session_state.selected_profile:
        profile = st.session_state.selected_profile
        player_data = profile['members'].get(st.session_state.player_uuid, {})
        
        # Process the data
        if st.session_state.processed_data is None:
            with st.spinner("Processing profile data..."):
                processor = ProfileProcessor(player_data, profile)
                st.session_state.processed_data = processor.process_all_data()
        
        processed_data = st.session_state.processed_data
        
        # Display overview metrics
        st.header("📊 Profile Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Profile Name", profile.get('cute_name', 'Unnamed'))
        with col2:
            st.metric("Game Mode", profile.get('game_mode', 'Normal'))
        with col3:
            skill_avg = processed_data.get('skills', {}).get('average', 0)
            st.metric("Skill Average", f"{skill_avg:.1f}")
        with col4:
            networth = processed_data.get('networth', {}).get('total', 0)
            st.metric("Networth", f"{networth:,}")
        
        # Data preview tabs
        st.header("🔍 Data Preview")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Skills", "Slayers", "Dungeons", "Inventory", "Collections"])
        
        with tab1:
            if 'skills' in processed_data:
                skills_df = pd.DataFrame(processed_data['skills']['data'])
                st.dataframe(skills_df, use_container_width=True)
        
        with tab2:
            if 'slayers' in processed_data:
                slayers_df = pd.DataFrame(processed_data['slayers']['data'])
                st.dataframe(slayers_df, use_container_width=True)
        
        with tab3:
            if 'dungeons' in processed_data:
                dungeons_df = pd.DataFrame(processed_data['dungeons']['data'])
                st.dataframe(dungeons_df, use_container_width=True)
        
        with tab4:
            if 'inventory' in processed_data:
                inventory_df = pd.DataFrame(processed_data['inventory']['data'])
                st.dataframe(inventory_df, use_container_width=True)
        
        with tab5:
            if 'collections' in processed_data:
                collections_df = pd.DataFrame(processed_data['collections']['data'])
                st.dataframe(collections_df, use_container_width=True)
        
        # Export section
        st.header("📤 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Full Profile Export")
            
            # Excel export
            if st.button("📊 Export to Excel (.xlsx)", key="excel_full"):
                with st.spinner("Generating Excel file..."):
                    exporter = ExcelExporter(processed_data)
                    excel_data = exporter.create_workbook()
                    
                    st.download_button(
                        label="⬇️ Download Excel File",
                        data=excel_data,
                        file_name=f"{profile.get('cute_name', 'profile')}_full_export.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            # PDF export
            if st.button("📄 Export to PDF", key="pdf_full"):
                with st.spinner("Generating PDF report..."):
                    exporter = PDFExporter(processed_data)
                    pdf_data = exporter.create_report()
                    
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_data,
                        file_name=f"{profile.get('cute_name', 'profile')}_report.pdf",
                        mime="application/pdf"
                    )
            
            # JSON export
            if st.button("📋 Export to JSON", key="json_full"):
                exporter = JSONExporter(processed_data)
                json_data = exporter.create_export()
                
                st.download_button(
                    label="⬇️ Download JSON File",
                    data=json_data,
                    file_name=f"{profile.get('cute_name', 'profile')}_data.json",
                    mime="application/json"
                )
        
        with col2:
            st.subheader("Section-Specific Export")
            
            section = st.selectbox(
                "Choose section to export:",
                ["skills", "slayers", "dungeons", "inventory", "collections", "pets", "networth"]
            )
            
            if section in processed_data:
                # CSV export for selected section
                if st.button(f"📊 Export {section.title()} to CSV", key=f"csv_{section}"):
                    exporter = CSVExporter(processed_data)
                    csv_data = exporter.create_section_csv(section)
                    
                    st.download_button(
                        label=f"⬇️ Download {section.title()} CSV",
                        data=csv_data,
                        file_name=f"{profile.get('cute_name', 'profile')}_{section}.csv",
                        mime="text/csv"
                    )
                
                # JSON export for selected section
                if st.button(f"📋 Export {section.title()} to JSON", key=f"json_{section}"):
                    section_data = {section: processed_data[section]}
                    exporter = JSONExporter(section_data)
                    json_data = exporter.create_export()
                    
                    st.download_button(
                        label=f"⬇️ Download {section.title()} JSON",
                        data=json_data,
                        file_name=f"{profile.get('cute_name', 'profile')}_{section}.json",
                        mime="application/json"
                    )
    
    else:
        # Welcome screen
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <h2>Welcome to Sky-Port! ⚡</h2>
            <p style="font-size: 1.2rem; color: #666;">Your comprehensive Hypixel SkyBlock profile data exporter</p>
            <br>
            <h3>🚀 Getting Started</h3>
            <ol style="text-align: left; max-width: 600px; margin: 0 auto;">
                <li>Enter your Hypixel API key (get it with <code>/api new</code> in-game)</li>
                <li>Input your Minecraft username or UUID</li>
                <li>Select a SkyBlock profile</li>
                <li>Export your data in multiple formats!</li>
            </ol>
            <br>
            <h3>📊 Supported Export Formats</h3>
            <div style="display: flex; justify-content: center; gap: 2rem; margin: 2rem 0;">
                <div>📊 Excel (.xlsx)</div>
                <div>📄 PDF Reports</div>
                <div>📋 JSON Data</div>
                <div>📈 CSV Files</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()