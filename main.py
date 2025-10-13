import streamlit as st
import asyncio
import time
import traceback
from typing import Dict, Any, Optional, Tuple
import pandas as pd
from datetime import datetime

# Core imports - Fixed paths to match actual file structure
from api.hypixel import HypixelAPI, HypixelAPIError, RateLimitError, InvalidAPIKeyError
from api.mojang import MojangAPI, MojangAPIError, PlayerNotFoundError
from processors.profile_processor import ProfileProcessor
from exporters.excel_exporter import ExcelExporter
from exporters.json_exporter import JSONExporter
from exporters.csv_exporter import CSVExporter
from exporters.pdf_exporter import PDFExporter

# Fixed API integrations - Now properly imported with correct module names
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

# Enhanced CSS
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
    
    .profile-card {
        border: 2px solid #e0e0e0;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    .profile-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        border-color: #1f77b4;
    }
    
    .profile-name {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .profile-stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 1rem;
        margin-top: 1.5rem;
    }
    
    .stat-item {
        text-align: center;
        padding: 0.5rem;
        background: rgba(31, 119, 180, 0.1);
        border-radius: 8px;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ff7f0e;
        display: block;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.25rem;
    }
    
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'processed_data': None,
        'player_data': None,
        'skyblock_profiles': None,
        'selected_profile': None,
        'processing_status': None,
        'export_ready': False,
        'current_player': None
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def display_profiles(profiles):
    """Display the fetched profiles in a user-friendly format"""
    st.markdown("## 📋 Available SkyBlock Profiles")
    
    if not profiles:
        st.info("🔍 No SkyBlock profiles found for this player.")
        return
    
    # Create responsive columns
    cols = st.columns(min(len(profiles), 3))
    
    for i, profile in enumerate(profiles):
        with cols[i % len(cols)]:
            profile_name = profile.get('cute_name', f'Profile {i+1}')
            game_mode = profile.get('game_mode', 'normal')
            profile_id = profile.get('profile_id', f'unknown_{i}')
            
            # Get basic stats from profile members
            members = profile.get('members', {})
            member_count = len(members)
            
            # Extract player-specific data
            player_uuid = st.session_state.get('current_player_uuid')
            player_data = members.get(player_uuid, {}) if player_uuid and members else {}
            
            fairy_souls = player_data.get('fairy_souls_collected', 0)
            last_save = profile.get('last_save', 0)
            last_save_str = datetime.fromtimestamp(last_save / 1000).strftime('%Y-%m-%d %H:%M') if last_save else 'Unknown'
            
            # Display profile card
            st.markdown(f"""
            <div class="profile-card">
                <div class="profile-name">🎮 {profile_name}</div>
                <div><strong>Game Mode:</strong> {game_mode.title()}</div>
                <div><strong>Members:</strong> {member_count}</div>
                <div><strong>Last Active:</strong> {last_save_str}</div>
                <div class="profile-stats">
                    <div class="stat-item">
                        <span class="stat-value">{fairy_souls}</span>
                        <div class="stat-label">Fairy Souls</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Process button
            button_key = f"process_{profile_id}_{i}"
            if st.button(f"🚀 Process {profile_name}", key=button_key, use_container_width=True):
                st.session_state.selected_profile = profile
                st.session_state.processing_status = "processing"
                st.rerun()

def process_selected_profile():
    """Process the selected profile and display results"""
    if not (st.session_state.selected_profile and st.session_state.processing_status == "processing"):
        return
        
    st.markdown("## 🔄 Processing Profile Data")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        selected_profile = st.session_state.selected_profile
        profile_name = selected_profile.get('cute_name', 'Unknown')
        
        # Update progress
        status_text.text("📋 Extracting profile data...")
        progress_bar.progress(20)
        
        # Get player data from profile members
        members = selected_profile.get('members', {})
        player_uuid = st.session_state.get('current_player_uuid')
        
        if not player_uuid or player_uuid not in members:
            # Try to find the player UUID
            if members:
                player_uuid = list(members.keys())[0]
            else:
                raise ValueError("No member data found in profile")
        
        player_profile_data = members[player_uuid]
        
        # Update progress
        status_text.text("⚙️ Initializing processors...")
        progress_bar.progress(40)
        
        # Process the profile data
        processor = ProfileProcessor(player_profile_data, selected_profile)
        
        status_text.text("📊 Processing all data categories...")
        progress_bar.progress(60)
        
        processed_data = processor.process_all_data()
        
        status_text.text("✅ Finalizing data...")
        progress_bar.progress(80)
        
        # Store processed data
        st.session_state.processed_data = processed_data
        st.session_state.processing_status = "completed"
        
        progress_bar.progress(100)
        status_text.text("🎉 Processing completed successfully!")
        
        # Success message
        st.markdown(f"""
        <div class="success-message">
            <strong>✅ Success!</strong> Profile '{profile_name}' has been processed successfully!
        </div>
        """, unsafe_allow_html=True)
        
        # Clear progress indicators after a moment
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
    except Exception as e:
        st.markdown(f"""
        <div class="error-message">
            <strong>❌ Processing Error:</strong> {str(e)}
        </div>
        """, unsafe_allow_html=True)
        
        st.session_state.processing_status = None
        st.error("Please try again or check if the profile data is accessible.")
        
        # Log error for debugging
        st.expander("🔍 Error Details (for debugging)", expanded=False).code(traceback.format_exc())

def display_processed_data():
    """Display processed profile data with enhanced metrics"""
    if not (st.session_state.processed_data and st.session_state.processing_status == "completed"):
        return
        
    st.markdown("## 📊 Profile Analysis")
    
    processed_data = st.session_state.processed_data
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        profile_info = processed_data.get('profile', {}).get('data', {})
        st.metric("🎮 Profile", profile_info.get('profile_name', 'Unknown'))
    
    with col2:
        skills_data = processed_data.get('skills', {}).get('data', [])
        skill_avg = sum(skill.get('level', 0) for skill in skills_data) / len(skills_data) if skills_data else 0
        st.metric("⭐ Skill Average", f"{skill_avg:.1f}")
    
    with col3:
        networth = processed_data.get('networth', {}).get('data', {}).get('total_coins', 0)
        st.metric("💰 Networth", f"{networth:,.0f}")
    
    with col4:
        slayer_data = processed_data.get('slayers', {}).get('data', [])
        total_slayer_xp = sum(slayer.get('xp', 0) for slayer in slayer_data)
        st.metric("🗡️ Slayer XP", f"{total_slayer_xp:,.0f}")
    
    # Data preview tabs
    tabs = st.tabs(["📈 Skills", "🗡️ Slayers", "⚔️ Dungeons", "💰 Economy", "🎒 Inventory"])
    
    with tabs[0]:  # Skills
        if 'skills' in processed_data and processed_data['skills'].get('data'):
            skills_df = pd.DataFrame(processed_data['skills']['data'])
            st.dataframe(skills_df, use_container_width=True, hide_index=True)
        else:
            st.info("No skills data available")
    
    with tabs[1]:  # Slayers
        if 'slayers' in processed_data and processed_data['slayers'].get('data'):
            slayers_df = pd.DataFrame(processed_data['slayers']['data'])
            st.dataframe(slayers_df, use_container_width=True, hide_index=True)
        else:
            st.info("No slayers data available")
    
    with tabs[2]:  # Dungeons
        if 'dungeons' in processed_data and processed_data['dungeons'].get('data'):
            dungeons_data = processed_data['dungeons']['data']
            if isinstance(dungeons_data, list):
                dungeons_df = pd.DataFrame(dungeons_data)
                st.dataframe(dungeons_df, use_container_width=True, hide_index=True)
            else:
                st.json(dungeons_data)
        else:
            st.info("No dungeons data available")
    
    with tabs[3]:  # Economy
        if 'networth' in processed_data and processed_data['networth'].get('data'):
            networth_data = processed_data['networth']['data']
            st.json(networth_data)
        else:
            st.info("No economy data available")
    
    with tabs[4]:  # Inventory
        if 'inventory' in processed_data and processed_data['inventory'].get('data'):
            inventory_data = processed_data['inventory']['data']
            if isinstance(inventory_data, list):
                inventory_df = pd.DataFrame(inventory_data)
                st.dataframe(inventory_df, use_container_width=True, hide_index=True)
            else:
                st.json(inventory_data)
        else:
            st.info("No inventory data available")

def display_export_options():
    """Display comprehensive export options"""
    if not (st.session_state.processed_data and st.session_state.processing_status == "completed"):
        return
        
    st.markdown("## 📤 Export Your Data")
    
    # Export format selection
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📋 Choose Export Formats")
        export_formats = st.multiselect(
            "Select formats to export:",
            ["📊 Excel (.xlsx)", "🔧 JSON (.json)", "📈 CSV (.csv)", "📄 PDF Report"],
            default=["📊 Excel (.xlsx)", "🔧 JSON (.json)"],
            help="Select one or more formats for your data export"
        )
    
    with col2:
        st.markdown("### 🎯 Export Options")
        include_raw_data = st.checkbox("Include raw API data", value=False)
        compress_export = st.checkbox("Compress large exports", value=True)
    
    # Export buttons
    st.markdown("### 🚀 Generate Exports")
    
    if st.button("📦 Export Selected Formats", type="primary", use_container_width=True):
        if not export_formats:
            st.warning("⚠️ Please select at least one export format.")
            return
            
        profile_name = st.session_state.selected_profile.get('cute_name', 'profile')
        
        export_progress = st.progress(0)
        export_status = st.empty()
        
        for i, format_option in enumerate(export_formats):
            try:
                export_status.text(f"Generating {format_option}...")
                export_progress.progress((i + 1) / len(export_formats))
                
                if "Excel" in format_option:
                    exporter = ExcelExporter(st.session_state.processed_data)
                    excel_data = exporter.create_workbook()
                    
                    st.download_button(
                        label="📊 Download Excel File",
                        data=excel_data,
                        file_name=f"skyblock_{profile_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
                elif "JSON" in format_option:
                    exporter = JSONExporter(st.session_state.processed_data)
                    json_data = exporter.create_export()
                    
                    st.download_button(
                        label="🔧 Download JSON File",
                        data=json_data,
                        file_name=f"skyblock_{profile_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                elif "CSV" in format_option:
                    exporter = CSVExporter(st.session_state.processed_data)
                    csv_data = exporter.create_combined_csv()
                    
                    st.download_button(
                        label="📈 Download CSV File", 
                        data=csv_data,
                        file_name=f"skyblock_{profile_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                elif "PDF" in format_option:
                    exporter = PDFExporter(st.session_state.processed_data)
                    pdf_data = exporter.create_report()
                    
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_data,
                        file_name=f"skyblock_{profile_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                        
            except Exception as e:
                st.error(f"❌ Error generating {format_option}: {str(e)}")
        
        export_status.text("✅ All exports generated successfully!")
        time.sleep(1)
        export_progress.empty()
        export_status.empty()

def main():
    """Main application function"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🚀 Sky-Port</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;">'
        'Comprehensive Hypixel SkyBlock Profile Exporter</p>', 
        unsafe_allow_html=True
    )
    
    # Configuration
    with st.expander("🔑 API Configuration", expanded=not st.session_state.get('api_configured', False)):
        api_key = st.text_input(
            "Hypixel API Key",
            type="password",
            help="Get your API key by typing '/api new' in Hypixel chat",
            placeholder="Enter your Hypixel API key..."
        )
        
        if api_key:
            st.session_state.api_configured = True
            st.success("✅ API key configured!")
        else:
            st.warning("⚠️ Please enter your Hypixel API key to continue.")
            st.info("💡 Get your API key by typing `/api new` in Hypixel chat.")
            st.stop()
    
    # Player input
    st.markdown("### 🎮 Player Lookup")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        username = st.text_input(
            "Minecraft Username",
            placeholder="Enter any Minecraft username...",
            help="Enter the Minecraft username to fetch SkyBlock profiles"
        )
    
    with col2:
        st.markdown("<div style='margin-top: 1.7rem;'></div>", unsafe_allow_html=True)
        fetch_button = st.button("🔍 Fetch Profiles", type="primary", use_container_width=True)
    
    # Fetch profiles
    if fetch_button and username:
        if not api_key:
            st.error("❌ Please configure your API key first!")
            return
            
        with st.spinner("🔍 Fetching player profiles..."):
            try:
                # Initialize API clients
                mojang_client = MojangAPI()
                hypixel_client = HypixelAPI(api_key)
                
                # Get player UUID
                uuid_data = mojang_client.get_uuid(username)
                if not uuid_data:
                    st.error("❌ Player not found! Please check the username.")
                    return
                
                uuid = uuid_data.get('id')
                if not uuid:
                    st.error("❌ Could not retrieve player UUID.")
                    return
                    
                st.session_state.current_player_uuid = uuid
                
                # Get player and SkyBlock data
                player_data = hypixel_client.get_player(uuid)
                skyblock_data = hypixel_client.get_skyblock_profiles(uuid)
                
                if not skyblock_data or not skyblock_data.get('profiles'):
                    st.error("❌ No SkyBlock profiles found for this player.")
                    return
                
                # Store data
                st.session_state.player_data = player_data
                st.session_state.skyblock_profiles = skyblock_data['profiles']
                
                st.success(f"✅ Found {len(skyblock_data['profiles'])} SkyBlock profile(s) for {username}!")
                
            except Exception as e:
                error_msg = str(e)
                if "403" in error_msg or "Forbidden" in error_msg:
                    st.error("❌ Invalid API key! Please check your Hypixel API key.")
                elif "429" in error_msg or "rate limit" in error_msg.lower():
                    st.error("❌ Rate limited! Please wait a moment before trying again.")
                elif "timeout" in error_msg.lower():
                    st.error("❌ Request timed out! Please check your internet connection.")
                else:
                    st.error(f"❌ An error occurred: {error_msg}")
                
                # Show debug info in expander
                with st.expander("🔍 Debug Information"):
                    st.code(traceback.format_exc())
                return
    
    # Display profiles
    if st.session_state.skyblock_profiles:
        display_profiles(st.session_state.skyblock_profiles)
    
    # Process selected profile
    process_selected_profile()
    
    # Display results
    display_processed_data()
    
    # Export options
    display_export_options()
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666; font-size: 0.9rem;">'
        'Sky-Port - Built with ❤️ for the Hypixel SkyBlock community | '
        '<a href="https://github.com/Sahaj33-op/Sky-Port" target="_blank">GitHub</a></p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
