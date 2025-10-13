import streamlit as st
import time
import traceback
from typing import Dict, Any, Tuple
import pandas as pd

# Core imports
# Import the custom exceptions along with the classes
from api.hypixel import HypixelAPI, HypixelAPIError, RateLimitError, InvalidAPIKeyError
from api.mojang import MojangAPI, MojangAPIError, PlayerNotFoundError
from processors.profile_processor import ProfileProcessor
from exporters.excel_exporter import ExcelExporter
from exporters.json_exporter import JSONExporter
from exporters.csv_exporter import CSVExporter
from exporters.pdf_exporter import PDFExporter

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
    
    .profile-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .profile-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .profile-name {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    
    .profile-stats {
        display: flex;
        justify-content: space-between;
        margin-top: 1rem;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-value {
        font-size: 1.2rem;
        font-weight: 700;
        color: #ff7f0e;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #666;
    }
    
    .processing-section {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-top: 2rem;
    }
    
    .export-section {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-top: 2rem;
    }
    
    .export-buttons {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        margin-top: 1rem;
    }
    
    .export-button {
        flex: 1;
        min-width: 120px;
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
    if 'skyblock_profiles' not in st.session_state:
        st.session_state.skyblock_profiles = None
    if 'selected_profile' not in st.session_state:
        st.session_state.selected_profile = None
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = None
    if 'export_ready' not in st.session_state:
        st.session_state.export_ready = False

def display_profiles(profiles):
    """Display the fetched profiles in a user-friendly format"""
    st.markdown("## 📋 SkyBlock Profiles")
    
    if not profiles:
        st.info("No profiles found for this player.")
        return
    
    cols = st.columns(2)
    
    for i, profile in enumerate(profiles):
        with cols[i % 2]:
            profile_name = profile.get('cute_name', 'Unknown')
            game_mode = profile.get('game_mode', 'normal')
            members = profile.get('members', {})
            members_count = len(members)
            
            # Get the first member's data for basic stats
            fairy_souls = 0
            first_member_data = {}
            
            if members:
                # Get the first member's UUID and data
                first_member_uuid = list(members.keys())[0]
                first_member_data = members.get(first_member_uuid, {})
                # Correct way to get fairy souls - it's in the player's profile data, not members
                fairy_souls = first_member_data.get('fairy_souls_collected', 0)
            
            with st.container():
                st.markdown(f"""
                <div class="profile-card">
                    <div class="profile-name">{profile_name}</div>
                    <div><strong>Mode:</strong> {game_mode.title()}</div>
                    <div><strong>Members:</strong> {members_count}</div>
                    <div class="profile-stats">
                        <div class="stat-item">
                            <div class="stat-value">{fairy_souls}</div>
                            <div class="stat-label">Fairy Souls</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Use a unique key for each button
                button_key = f"process_{profile.get('profile_id', f'profile_{i}')}"
                if st.button(f"Process {profile_name}", key=button_key):
                    st.session_state.selected_profile = profile
                    st.session_state.processing_status = "processing"
                    st.rerun()

def process_selected_profile():
    """Process the selected profile and display results"""
    if st.session_state.selected_profile and st.session_state.processing_status == "processing":
        st.markdown("## 🔄 Processing Profile")
        
        with st.spinner("Processing profile data..."):
            try:
                # Get the selected profile
                selected_profile = st.session_state.selected_profile
                
                # Extract the player data for the selected profile
                # The player data is in the 'members' section of the profile
                members = selected_profile.get('members', {})
                player_uuid = list(members.keys())[0] if members else None
                player_data = members.get(player_uuid, {}) if player_uuid else {}
                
                # Process the profile data
                processor = ProfileProcessor(player_data, selected_profile)
                processed_data = processor.process_all_data()
                st.session_state.processed_data = processed_data
                st.session_state.processing_status = "completed"
                
                st.success(f"✅ Profile '{selected_profile.get('cute_name', 'Unknown')}' processed successfully!")
                
            except Exception as e:
                st.error(f"❌ Error processing profile: {str(e)}")
                st.session_state.processing_status = None
                traceback.print_exc()

def display_processed_data():
    """Display processed profile data"""
    if st.session_state.processed_data and st.session_state.processing_status == "completed":
        st.markdown("## 📊 Processed Profile Data")
        
        processed_data = st.session_state.processed_data
        
        # Display profile info
        profile_info = processed_data.get('profile_info', {})
        if profile_info and profile_info.get('data'):
            info = profile_info['data'][0]
            st.markdown(f"### {info.get('profile_name', 'Unknown Profile')}")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Game Mode", info.get('game_mode', 'Unknown'))
            with col2:
                st.metric("Fairy Souls", info.get('fairy_souls', 0))
            with col3:
                st.metric("Last Save", info.get('last_save', 'Unknown'))

def display_export_options():
    """Display export options for processed data"""
    if st.session_state.processed_data and st.session_state.processing_status == "completed":
        st.markdown("## 📤 Export Options")
        
        with st.container():
            st.markdown('<div class="export-section">', unsafe_allow_html=True)
            st.markdown("### Choose Export Format")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("📊 Excel", key="export_excel", use_container_width=True):
                    try:
                        exporter = ExcelExporter(st.session_state.processed_data)
                        excel_data = exporter.create_workbook()
                        
                        st.download_button(
                            label="Download Excel File",
                            data=excel_data,
                            file_name=f"skyblock_profile_{st.session_state.selected_profile.get('cute_name', 'profile')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    except Exception as e:
                        st.error(f"Error exporting to Excel: {str(e)}")
                        traceback.print_exc()
            
            with col2:
                if st.button("🔧 JSON", key="export_json", use_container_width=True):
                    try:
                        exporter = JSONExporter(st.session_state.processed_data)
                        json_data = exporter.create_export()
                        
                        st.download_button(
                            label="Download JSON File",
                            data=json_data,
                            file_name=f"skyblock_profile_{st.session_state.selected_profile.get('cute_name', 'profile')}.json",
                            mime="application/json"
                        )
                    except Exception as e:
                        st.error(f"Error exporting to JSON: {str(e)}")
                        traceback.print_exc()
            
            with col3:
                if st.button("📈 CSV", key="export_csv", use_container_width=True):
                    try:
                        exporter = CSVExporter(st.session_state.processed_data)
                        csv_data = exporter.create_combined_csv()
                        
                        st.download_button(
                            label="Download CSV File",
                            data=csv_data,
                            file_name=f"skyblock_profile_{st.session_state.selected_profile.get('cute_name', 'profile')}.csv",
                            mime="text/csv"
                        )
                    except Exception as e:
                        st.error(f"Error exporting to CSV: {str(e)}")
                        traceback.print_exc()
            
            with col4:
                if st.button("📄 PDF", key="export_pdf", use_container_width=True):
                    try:
                        exporter = PDFExporter(st.session_state.processed_data)
                        pdf_data = exporter.create_report()
                        
                        st.download_button(
                            label="Download PDF Report",
                            data=pdf_data,
                            file_name=f"skyblock_profile_{st.session_state.selected_profile.get('cute_name', 'profile')}.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"Error exporting to PDF: {str(e)}")
                        traceback.print_exc()
            
            st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Enhanced main application function"""
    initialize_session_state()
    
    st.markdown('<h1 class="main-header">🚀 Sky-Port</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Comprehensive Hypixel SkyBlock Profile Exporter</p>', unsafe_allow_html=True)
    
    with st.expander("🔑 Configuration", expanded=True):
        api_key = st.text_input(
            "Hypixel API Key",
            type="password",
            help="Get your API key by typing /api new in Hypixel",
        )
        if not api_key:
            st.warning("⚠️ Please enter your Hypixel API key to continue.")
            st.info("💡 Get your API key by typing `/api new` in Hypixel chat.")
            return
    
    col1, col2 = st.columns([3, 1])
    with col1:
        username = st.text_input("🎮 Player Username", placeholder="Enter Minecraft username...")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        fetch_button = st.button("🔍 Fetch Profile", type="primary", use_container_width=True)
    
    if fetch_button and username:
        with st.spinner("Fetching player profiles..."):
            # ADD THIS TRY...EXCEPT BLOCK
            try:
                mojang_client = MojangAPI()
                hypixel_client = HypixelAPI(api_key)
                
                uuid_data = mojang_client.get_uuid(username)
                if not uuid_data:
                    st.error("❌ Player not found!")
                    return
                    
                uuid = uuid_data['id']
                
                player_data = hypixel_client.get_player(uuid)
                skyblock_data = hypixel_client.get_skyblock_profiles(uuid)
                
                if not skyblock_data or 'profiles' not in skyblock_data or not skyblock_data['profiles']:
                    st.error("❌ No SkyBlock profiles found for this player.")
                    return
                
                st.session_state.player_data = player_data
                st.session_state.skyblock_profiles = skyblock_data['profiles']
                st.success("✅ Profiles fetched successfully!")

            # CATCH THE SPECIFIC ERRORS
            except (PlayerNotFoundError, InvalidAPIKeyError, RateLimitError, MojangAPIError, HypixelAPIError) as e:
                st.error(f"❌ {str(e)}")
                return
            except Exception as e:
                st.error(f"❌ An unexpected error occurred: {str(e)}")
                traceback.print_exc() # For debugging
                return
    
    # Display profiles if they've been fetched
    if st.session_state.skyblock_profiles:
        display_profiles(st.session_state.skyblock_profiles)
    
    # Process selected profile if needed
    process_selected_profile()
    
    # Display processed data if available
    display_processed_data()
    
    # Display export options if data is processed
    display_export_options()

if __name__ == "__main__":
    main()