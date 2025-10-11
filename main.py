import streamlit as st
import asyncio
import time
import traceback
from typing import Dict, Any, Optional, Tuple
import pandas as pd

# Core imports
from api.hypixel_client import HypixelClient
from api.mojang_client import MojangClient
from processors.profile_processor import ProfileProcessor
from exporters.excel_exporter import ExcelExporter
from exporters.json_exporter import JSONExporter
from exporters.csv_exporter import CSVExporter
from exporters.pdf_exporter import PDFExporter

# New API integrations
from api.skyhelper_networth import SkyHelperNetworth
from api.elite_farming import EliteFarmingWeight
from api.neu_repository import NEURepository
from utils.cache import CacheManager
from utils.rate_limiter import RateLimiter

# Page configuration
st.set_page_config(
    page_title="Sky-Port | Hypixel SkyBlock Profile Exporter",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS with enhanced styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(45deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .status-success {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    
    .status-error {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    
    .status-processing {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
    
    .export-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .export-card:hover {
        border-color: #1f77b4;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables"""
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'player_data' not in st.session_state:
        st.session_state.player_data = None
    if 'selected_profile' not in st.session_state:
        st.session_state.selected_profile = None
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = None
    if 'export_ready' not in st.session_state:
        st.session_state.export_ready = False

# Enhanced caching with new integrations
@st.cache_data(ttl=300, show_spinner=False)
def fetch_and_process_profile(username: str, profile_id: str, api_key: str) -> Tuple[Dict, Dict, str]:
    """Fetch and process profile data with enhanced integrations"""
    try:
        # Initialize clients
        mojang_client = MojangClient()
        hypixel_client = HypixelClient(api_key)
        
        # Get player UUID
        uuid = mojang_client.get_uuid(username)
        if not uuid:
            return None, None, "Player not found"
        
        # Get profile data
        player_data = hypixel_client.get_player(uuid)
        skyblock_data = hypixel_client.get_skyblock_profiles(uuid)
        
        if not skyblock_data or 'profiles' not in skyblock_data:
            return None, None, "No SkyBlock profiles found"
        
        # Find selected profile
        selected_profile = None
        for profile in skyblock_data['profiles']:
            if profile['profile_id'] == profile_id:
                selected_profile = profile
                break
        
        if not selected_profile:
            return None, None, "Profile not found"
        
        return player_data, selected_profile, "success"
        
    except Exception as e:
        return None, None, f"Error fetching data: {str(e)}"

@st.cache_data(ttl=600, show_spinner=False)
def process_enhanced_data(player_data: Dict, profile_data: Dict) -> Dict[str, Any]:
    """Process profile data with enhanced calculations"""
    try:
        # Initialize processor
        processor = ProfileProcessor(player_data, profile_data)
        
        # Process standard data
        processed_data = processor.process_all_data()
        
        # Add enhanced calculations
        skyhelper = SkyHelperNetworth()
        elite_farming = EliteFarmingWeight()
        neu_repo = NEURepository()
        
        # Calculate detailed networth
        processed_data['detailed_networth'] = skyhelper.calculate_networth(profile_data)
        
        # Calculate farming weight
        processed_data['farming_weight'] = elite_farming.calculate_farming_weight(profile_data)
        
        # Enhance item data with NEU repository
        processed_data['enhanced_items'] = neu_repo.enhance_item_data(
            processed_data.get('inventory', {})
        )
        
        return processed_data
        
    except Exception as e:
        st.error(f"Error processing enhanced data: {str(e)}")
        return {}

def show_processing_progress():
    """Display enhanced processing progress with status updates"""
    progress_container = st.container()
    
    with progress_container:
        st.markdown('<div class="status-processing">🔄 Processing your SkyBlock profile with enhanced calculations...</div>', unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simulate processing steps with real status updates
        steps = [
            "Fetching player data...",
            "Processing skills and experience...",
            "Calculating networth with SkyHelper...",
            "Computing farming weight with Elite Bot...",
            "Analyzing inventory with NEU data...",
            "Processing dungeons and slayers...",
            "Finalizing collections and pets...",
            "Preparing export data..."
        ]
        
        for i, step in enumerate(steps):
            progress = (i + 1) / len(steps)
            progress_bar.progress(progress)
            status_text.text(step)
            time.sleep(0.5)  # Simulate processing time
        
        return progress_container

def display_enhanced_metrics(processed_data: Dict[str, Any]):
    """Display enhanced metrics with new calculations"""
    if not processed_data:
        return
    
    st.subheader("📊 Enhanced Profile Metrics")
    
    # Create metric columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        skill_avg = processed_data.get('skills', {}).get('skill_average', 0)
        st.markdown(f"""
        <div class="metric-card">
            <h3>⭐ Skill Average</h3>
            <h2>{skill_avg:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        networth = processed_data.get('detailed_networth', {}).get('total', 0)
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 Total Networth</h3>
            <h2>{networth:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        farming_weight = processed_data.get('farming_weight', {}).get('total_weight', 0)
        st.markdown(f"""
        <div class="metric-card">
            <h3>🌾 Farming Weight</h3>
            <h2>{farming_weight:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        catacombs_level = processed_data.get('dungeons', {}).get('catacombs_level', 0)
        st.markdown(f"""
        <div class="metric-card">
            <h3>⚔️ Catacombs</h3>
            <h2>Level {catacombs_level}</h2>
        </div>
        """, unsafe_allow_html=True)

def create_enhanced_export_interface(processed_data: Dict[str, Any]):
    """Create enhanced export interface with progress tracking"""
    st.subheader("📤 Export Your Data")
    
    # Export format selection
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Export Formats")
        export_formats = st.multiselect(
            "Select formats:",
            ["📊 Excel (.xlsx)", "🔧 JSON", "📈 CSV Bundle", "📄 PDF Report"],
            default=["📊 Excel (.xlsx)", "🔧 JSON"],
            help="Choose one or more export formats for your data"
        )
    
    with col2:
        st.markdown("### 🎯 Data Categories")
        data_categories = st.multiselect(
            "Select categories:",
            [
                "👤 Profile Info", "⭐ Skills", "🗡️ Slayers", "⚔️ Dungeons", 
                "🎒 Inventories", "📚 Collections", "🐕 Pets", "💰 Detailed Networth",
                "🌾 Farming Weight", "🎮 Enhanced Items"
            ],
            default=[
                "👤 Profile Info", "⭐ Skills", "💰 Detailed Networth", "🌾 Farming Weight"
            ],
            help="Choose which data categories to include in your export"
        )
    
    # Export buttons with enhanced functionality
    st.markdown("### 🚀 Generate Exports")
    
    export_col1, export_col2 = st.columns(2)
    
    with export_col1:
        if st.button("🎯 Export Selected Data", type="primary", use_container_width=True):
            generate_selective_exports(processed_data, export_formats, data_categories)
    
    with export_col2:
        if st.button("📦 Export Complete Profile", use_container_width=True):
            generate_complete_exports(processed_data, export_formats)

def generate_selective_exports(processed_data: Dict, formats: list, categories: list):
    """Generate exports for selected categories with progress tracking"""
    if not formats or not categories:
        st.warning("Please select at least one format and one category.")
        return
    
    # Show progress
    progress_container = st.container()
    with progress_container:
        st.info("🔄 Generating your selected exports...")
        export_progress = st.progress(0)
        
        # Filter data based on selected categories
        filtered_data = {}
        category_mapping = {
            "👤 Profile Info": "profile",
            "⭐ Skills": "skills", 
            "🗡️ Slayers": "slayers",
            "⚔️ Dungeons": "dungeons",
            "🎒 Inventories": "inventory",
            "📚 Collections": "collections",
            "🐕 Pets": "pets",
            "💰 Detailed Networth": "detailed_networth",
            "🌾 Farming Weight": "farming_weight",
            "🎮 Enhanced Items": "enhanced_items"
        }
        
        for category in categories:
            if category in category_mapping:
                key = category_mapping[category]
                if key in processed_data:
                    filtered_data[key] = processed_data[key]
        
        # Generate exports
        for i, format_type in enumerate(formats):
            export_progress.progress((i + 1) / len(formats))
            
            if "Excel" in format_type:
                create_excel_download(filtered_data, f"skyblock_data_selective")
            elif "JSON" in format_type:
                create_json_download(filtered_data, f"skyblock_data_selective")
            elif "CSV" in format_type:
                create_csv_download(filtered_data, f"skyblock_data_selective")
            elif "PDF" in format_type:
                create_pdf_download(filtered_data, f"skyblock_data_selective")
        
        st.success("✅ Exports generated successfully!")

def generate_complete_exports(processed_data: Dict, formats: list):
    """Generate complete profile exports"""
    if not formats:
        st.warning("Please select at least one format.")
        return
    
    progress_container = st.container()
    with progress_container:
        st.info("🔄 Generating complete profile exports...")
        export_progress = st.progress(0)
        
        for i, format_type in enumerate(formats):
            export_progress.progress((i + 1) / len(formats))
            
            if "Excel" in format_type:
                create_excel_download(processed_data, "skyblock_profile_complete")
            elif "JSON" in format_type:
                create_json_download(processed_data, "skyblock_profile_complete")
            elif "CSV" in format_type:
                create_csv_download(processed_data, "skyblock_profile_complete")
            elif "PDF" in format_type:
                create_pdf_download(processed_data, "skyblock_profile_complete")
        
        st.success("✅ Complete profile exports generated successfully!")

# Enhanced download functions
def create_excel_download(data: Dict, filename: str):
    """Create Excel download with enhanced formatting"""
    try:
        exporter = ExcelExporter()
        excel_data = exporter.create_workbook(data)
        
        st.download_button(
            label="📊 Download Excel File",
            data=excel_data,
            file_name=f"{filename}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error creating Excel file: {str(e)}")

def create_json_download(data: Dict, filename: str):
    """Create JSON download with formatting options"""
    try:
        exporter = JSONExporter()
        json_data = exporter.create_json(data)
        
        st.download_button(
            label="🔧 Download JSON File",
            data=json_data,
            file_name=f"{filename}.json",
            mime="application/json",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error creating JSON file: {str(e)}")

def create_csv_download(data: Dict, filename: str):
    """Create CSV bundle download"""
    try:
        exporter = CSVExporter()
        csv_data = exporter.create_csv_bundle(data)
        
        st.download_button(
            label="📈 Download CSV Bundle",
            data=csv_data,
            file_name=f"{filename}_bundle.zip",
            mime="application/zip",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error creating CSV bundle: {str(e)}")

def create_pdf_download(data: Dict, filename: str):
    """Create PDF report download"""
    try:
        exporter = PDFExporter()
        pdf_data = exporter.create_pdf(data)
        
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_data,
            file_name=f"{filename}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error creating PDF report: {str(e)}")

def main():
    """Enhanced main application function"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🚀 Sky-Port</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Comprehensive Hypixel SkyBlock Profile Exporter</p>', unsafe_allow_html=True)
    
    # API Key input with enhanced validation
    with st.expander("🔑 Configuration", expanded=True):
        api_key = st.text_input(
            "Hypixel API Key",
            type="password",
            help="Get your API key from /api new in Hypixel",
            value=st.secrets.get("hypixel_api_key", "") if "hypixel_api_key" in st.secrets else ""
        )
        
        if not api_key:
            st.warning("⚠️ Please enter your Hypixel API key to continue.")
            st.info("💡 Get your API key by typing `/api new` in Hypixel chat.")
            return
    
    # Player input
    col1, col2 = st.columns([3, 1])
    with col1:
        username = st.text_input("🎮 Player Username", placeholder="Enter Minecraft username...")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        fetch_button = st.button("🔍 Fetch Profile", type="primary", use_container_width=True)
    
    if fetch_button and username:
        with st.spinner("Fetching player profiles..."):
            # Get player profiles for selection
            try:
                mojang_client = MojangClient()
                hypixel_client = HypixelClient(api_key)
                
                uuid = mojang_client.get_uuid(username)
                if not uuid:
                    st.error("❌ Player not found!")
                    return
                
                player_data = hypixel_client.get_player(uuid)
                skyblock_data = hypixel_client.get_skyblock_profiles(uuid)
                
                if not skyblock_data or 'profiles' not in skyblock_data:
                    st.error("❌ No SkyBlock profiles found!")
                    return
                
                st.session_state.player_data = player_data
                st.session_state.skyblock_profiles = skyblock_data['profiles']
                
            except Exception as e:
                st.error(f"❌ Error fetching profiles: {str(e)}")
                return
    
    # Profile selection
    if st.session_state.get('skyblock_profiles'):
        st.subheader("📋 Select Profile")
        
        profile_options = []
        for i, profile in enumerate(st.session_state.skyblock_profiles):
            cute_name = profile.get('cute_name', f'Profile {i+1}')
            game_mode = profile.get('game_mode', 'Normal')
            last_save = pd.to_datetime(profile.get('last_save', 0), unit='ms')
            profile_options.append(f"{cute_name} ({game_mode}) - Last played: {last_save.strftime('%Y-%m-%d %H:%M')}")
        
        selected_index = st.selectbox("Choose a profile:", range(len(profile_options)), format_func=lambda x: profile_options[x])
        
        if st.button("🚀 Process Profile", type="primary", use_container_width=True):
            selected_profile = st.session_state.skyblock_profiles[selected_index]
            
            # Show processing progress
            progress_container = show_processing_progress()
            
            # Process data with enhanced calculations
            processed_data = process_enhanced_data(
                st.session_state.player_data, 
                selected_profile
            )
            
            if processed_data:
                st.session_state.processed_data = processed_data
                st.session_state.export_ready = True
                progress_container.empty()
                st.success("✅ Profile processed successfully with enhanced calculations!")
            else:
                st.error("❌ Failed to process profile data.")
    
    # Display results and export interface
    if st.session_state.get('export_ready') and st.session_state.get('processed_data'):
        # Enhanced metrics display
        display_enhanced_metrics(st.session_state.processed_data)
        
        # Data preview tabs (enhanced)
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "⭐ Skills", "💰 Networth", "🌾 Farming", "⚔️ Dungeons", "🎒 Inventory", "📚 Collections"
        ])
        
        with tab1:
            if 'skills' in st.session_state.processed_data:
                st.dataframe(st.session_state.processed_data['skills'], use_container_width=True)
        
        with tab2:
            if 'detailed_networth' in st.session_state.processed_data:
                networth_data = st.session_state.processed_data['detailed_networth']
                st.json(networth_data)
        
        with tab3:
            if 'farming_weight' in st.session_state.processed_data:
                farming_data = st.session_state.processed_data['farming_weight']
                st.json(farming_data)
        
        with tab4:
            if 'dungeons' in st.session_state.processed_data:
                st.dataframe(st.session_state.processed_data['dungeons'], use_container_width=True)
        
        with tab5:
            if 'inventory' in st.session_state.processed_data:
                st.json(st.session_state.processed_data['inventory'])
        
        with tab6:
            if 'collections' in st.session_state.processed_data:
                st.dataframe(st.session_state.processed_data['collections'], use_container_width=True)
        
        # Enhanced export interface
        st.divider()
        create_enhanced_export_interface(st.session_state.processed_data)

if __name__ == "__main__":
    main()
