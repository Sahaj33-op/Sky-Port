import streamlit as st
import time
import traceback
from typing import Dict, Any, Optional, Tuple
import pandas as pd

# Core imports - FIXED PATHS TO MATCH ACTUAL FILE STRUCTURE
from api.hypixel import HypixelAPI, HypixelAPIError, RateLimitError, InvalidAPIKeyError
from api.mojang import MojangAPI, MojangAPIError, PlayerNotFoundError
from processors.profile_processor import ProfileProcessor
from exporters.excel_exporter import ExcelExporter
from exporters.json_exporter import JSONExporter
from exporters.csv_exporter import CSVExporter
from exporters.pdf_exporter import PDFExporter

# Enhanced API integrations - OPTIONAL IMPORTS WITH ERROR HANDLING
try:
    from api.skyhelper_networth import SkyHelperNetworth
    SKYHELPER_AVAILABLE = True
except ImportError:
    SKYHELPER_AVAILABLE = False
    
try:
    from api.elite_farming import EliteFarmingWeight  
    ELITE_FARMING_AVAILABLE = True
except ImportError:
    ELITE_FARMING_AVAILABLE = False

try:
    from api.neu_repository import NEURepository
    NEU_AVAILABLE = True
except ImportError:
    NEU_AVAILABLE = False

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
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .profile-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    
    .profile-name {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    
    .export-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid #dee2e6;
    }
    
    .metric-highlight {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    
    .status-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .status-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'processed_data': None,
        'player_data': None,
        'skyblock_profiles': None,
        'selected_profile': None,
        'processing_status': None,
        'export_ready': False,
        'player_uuid': None,
        'selected_profile_index': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def display_feature_status():
    """Display which enhanced features are available"""
    with st.expander("🔧 Enhanced Features Status", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status = "✅ Available" if SKYHELPER_AVAILABLE else "❌ Not Available"
            st.write(f"**SkyHelper Networth:** {status}")
        
        with col2:
            status = "✅ Available" if ELITE_FARMING_AVAILABLE else "❌ Not Available"
            st.write(f"**Elite Farming Weight:** {status}")
        
        with col3:
            status = "✅ Available" if NEU_AVAILABLE else "❌ Not Available"
            st.write(f"**NEU Repository:** {status}")
        
        if not (SKYHELPER_AVAILABLE or ELITE_FARMING_AVAILABLE or NEU_AVAILABLE):
            st.info("💡 Enhanced features will be available once the API integrations are configured.")

def display_profiles(profiles):
    """Display profiles in an enhanced format"""
    st.markdown("## 📋 Select SkyBlock Profile")
    
    if not profiles:
        st.info("No profiles found for this player.")
        return
    
    # Create profile cards
    for i, profile in enumerate(profiles):
        profile_name = profile.get('cute_name', f'Profile {i+1}')
        game_mode = profile.get('game_mode', 'normal')
        members = profile.get('members', {})
        member_count = len(members)
        
        # Get basic stats from first member
        fairy_souls = 0
        if members:
            first_member_uuid = list(members.keys())[0]
            first_member_data = members.get(first_member_uuid, {})
            fairy_souls = first_member_data.get('fairy_souls_collected', 0)
        
        # Create profile card
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            <div class="profile-card">
                <div class="profile-name">{profile_name}</div>
                <div><strong>Mode:</strong> {game_mode.title()}</div>
                <div><strong>Members:</strong> {member_count}</div>
                <div><strong>Fairy Souls:</strong> {fairy_souls}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if st.button(f"Process {profile_name}", key=f"process_{i}", use_container_width=True):
                st.session_state.selected_profile = profile
                st.session_state.selected_profile_index = i
                st.session_state.processing_status = "processing"
                st.rerun()

def process_selected_profile():
    """Process the selected profile with enhanced calculations"""
    if (st.session_state.selected_profile and 
        st.session_state.processing_status == "processing"):
        
        st.markdown("## 🔄 Processing Profile Data")
        
        # Create progress indicator
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            selected_profile = st.session_state.selected_profile
            
            # Step 1: Extract player data
            status_text.text("Extracting player data...")
            progress_bar.progress(20)
            
            members = selected_profile.get('members', {})
            if not members:
                st.error("❌ No member data found in profile")
                st.session_state.processing_status = None
                return
                
            player_uuid = list(members.keys())[0]
            player_data = members.get(player_uuid, {})
            st.session_state.player_uuid = player_uuid
            
            # Step 2: Initialize processor
            status_text.text("Initializing data processor...")
            progress_bar.progress(40)
            
            processor = ProfileProcessor(player_data, selected_profile)
            
            # Step 3: Process basic data
            status_text.text("Processing skills, slayers, dungeons...")
            progress_bar.progress(60)
            
            processed_data = processor.process_all_data()
            
            # Step 4: Add enhanced calculations if available
            if SKYHELPER_AVAILABLE:
                status_text.text("Calculating detailed networth...")
                progress_bar.progress(75)
                try:
                    skyhelper = SkyHelperNetworth()
                    processed_data['detailed_networth'] = skyhelper.calculate_networth(player_data)
                except Exception as e:
                    st.warning(f"SkyHelper networth calculation failed: {e}")
            
            if ELITE_FARMING_AVAILABLE:
                status_text.text("Computing farming weight...")
                progress_bar.progress(85)
                try:
                    elite_farming = EliteFarmingWeight()
                    processed_data['farming_weight'] = elite_farming.calculate_farming_weight(player_data)
                except Exception as e:
                    st.warning(f"Elite farming weight calculation failed: {e}")
            
            if NEU_AVAILABLE:
                status_text.text("Enhancing item data...")
                progress_bar.progress(95)
                try:
                    neu_repo = NEURepository()
                    processed_data['enhanced_items'] = neu_repo.enhance_item_data(
                        player_data.get('inv_contents', {})
                    )
                except Exception as e:
                    st.warning(f"NEU item enhancement failed: {e}")
            
            # Step 5: Finalize
            status_text.text("Finalizing data...")
            progress_bar.progress(100)
            
            st.session_state.processed_data = processed_data
            st.session_state.processing_status = "completed"
            st.session_state.export_ready = True
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            st.markdown('<div class="status-success">✅ Profile processed successfully!</div>', 
                       unsafe_allow_html=True)
            
        except Exception as e:
            st.markdown(f'<div class="status-error">❌ Error processing profile: {str(e)}</div>', 
                       unsafe_allow_html=True)
            st.session_state.processing_status = None
            traceback.print_exc()

def display_processed_data():
    """Display processed profile data with enhanced metrics"""
    if (st.session_state.processed_data and 
        st.session_state.processing_status == "completed"):
        
        st.markdown("## 📊 Profile Analytics")
        
        processed_data = st.session_state.processed_data
        
        # Enhanced metrics display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Skills average
            skills_data = processed_data.get('skills', {})
            skill_avg = skills_data.get('average', 0) if skills_data else 0
            st.markdown(f"""
            <div class="metric-highlight">
                <h3 style="margin: 0; color: #1f77b4;">⭐ Skills</h3>
                <h2 style="margin: 0;">{skill_avg:.2f}</h2>
                <p style="margin: 0; color: #666;">Average Level</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Networth
            networth_data = processed_data.get('networth', {})
            if 'detailed_networth' in processed_data:
                networth = processed_data['detailed_networth'].get('total', 0)
            else:
                networth = networth_data.get('total', 0) if networth_data else 0
            
            st.markdown(f"""
            <div class="metric-highlight">
                <h3 style="margin: 0; color: #ff7f0e;">💰 Networth</h3>
                <h2 style="margin: 0;">{networth:,.0f}</h2>
                <p style="margin: 0; color: #666;">Total Coins</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Farming weight
            if 'farming_weight' in processed_data:
                farming_weight = processed_data['farming_weight'].get('total_weight', 0)
            else:
                farming_weight = 0
            
            st.markdown(f"""
            <div class="metric-highlight">
                <h3 style="margin: 0; color: #2ca02c;">🌾 Farming</h3>
                <h2 style="margin: 0;">{farming_weight:,.0f}</h2>
                <p style="margin: 0; color: #666;">Weight</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            # Slayer progress
            slayers_data = processed_data.get('slayers', {})
            slayer_xp = slayers_data.get('summary', {}).get('total_slayer_xp', 0) if slayers_data else 0
            
            st.markdown(f"""
            <div class="metric-highlight">
                <h3 style="margin: 0; color: #d62728;">🗡️ Slayers</h3>
                <h2 style="margin: 0;">{slayer_xp:,.0f}</h2>
                <p style="margin: 0; color: #666;">Total XP</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Data preview tabs
        st.markdown("## 🔍 Data Preview")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "⭐ Skills", "🗡️ Slayers", "⚔️ Dungeons", "🎒 Inventory", "📚 Collections"
        ])
        
        with tab1:
            skills_data = processed_data.get('skills', {})
            if skills_data and 'data' in skills_data and skills_data['data']:
                df = pd.DataFrame(skills_data['data'])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No skills data available")
        
        with tab2:
            slayers_data = processed_data.get('slayers', {})
            if slayers_data and 'data' in slayers_data and slayers_data['data']:
                df = pd.DataFrame(slayers_data['data'])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No slayers data available")
        
        with tab3:
            dungeons_data = processed_data.get('dungeons', {})
            if dungeons_data and 'data' in dungeons_data and dungeons_data['data']:
                df = pd.DataFrame(dungeons_data['data'])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No dungeons data available")
        
        with tab4:
            inventory_data = processed_data.get('inventory', {})
            if inventory_data and 'data' in inventory_data and inventory_data['data']:
                df = pd.DataFrame(inventory_data['data'])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No inventory data available")
        
        with tab5:
            collections_data = processed_data.get('collections', {})
            if collections_data and 'data' in collections_data and collections_data['data']:
                df = pd.DataFrame(collections_data['data'])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No collections data available")

def display_export_options():
    """Display enhanced export options"""
    if (st.session_state.processed_data and 
        st.session_state.processing_status == "completed"):
        
        st.markdown('<div class="export-section">', unsafe_allow_html=True)
        st.markdown("## 📤 Export Your Data")
        
        # Profile name for filenames
        profile_name = "skyblock_profile"
        if st.session_state.selected_profile:
            profile_name = st.session_state.selected_profile.get('cute_name', 'profile').replace(' ', '_').replace('/', '_')
        
        # Export format selection
        st.markdown("### Choose Export Format")
        
        # Export buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Excel Export", key="export_excel", use_container_width=True):
                try:
                    with st.spinner("Generating Excel file..."):
                        exporter = ExcelExporter(st.session_state.processed_data)
                        excel_data = exporter.create_workbook()
                        
                        st.download_button(
                            label="⬇️ Download Excel File",
                            data=excel_data,
                            file_name=f"{profile_name}_export.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                        st.success("Excel file generated!")
                except Exception as e:
                    st.error(f"Excel export error: {str(e)}")
                    with st.expander("Error Details"):
                        st.code(traceback.format_exc())
        
        with col2:
            if st.button("🔧 JSON Export", key="export_json", use_container_width=True):
                try:
                    with st.spinner("Generating JSON file..."):
                        exporter = JSONExporter(st.session_state.processed_data)
                        json_data = exporter.create_export()
                        
                        st.download_button(
                            label="⬇️ Download JSON File",
                            data=json_data,
                            file_name=f"{profile_name}_data.json",
                            mime="application/json",
                            use_container_width=True
                        )
                        st.success("JSON file generated!")
                except Exception as e:
                    st.error(f"JSON export error: {str(e)}")
                    with st.expander("Error Details"):
                        st.code(traceback.format_exc())
        
        with col3:
            if st.button("📈 CSV Export", key="export_csv", use_container_width=True):
                try:
                    with st.spinner("Generating CSV file..."):
                        exporter = CSVExporter(st.session_state.processed_data)
                        csv_data = exporter.create_combined_csv()
                        
                        st.download_button(
                            label="⬇️ Download CSV File",
                            data=csv_data,
                            file_name=f"{profile_name}_data.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                        st.success("CSV file generated!")
                except Exception as e:
                    st.error(f"CSV export error: {str(e)}")
                    with st.expander("Error Details"):
                        st.code(traceback.format_exc())
        
        with col4:
            if st.button("📄 PDF Report", key="export_pdf", use_container_width=True):
                try:
                    with st.spinner("Generating PDF report..."):
                        exporter = PDFExporter(st.session_state.processed_data)
                        pdf_data = exporter.create_report()
                        
                        st.download_button(
                            label="⬇️ Download PDF Report",
                            data=pdf_data,
                            file_name=f"{profile_name}_report.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        st.success("PDF report generated!")
                except Exception as e:
                    st.error(f"PDF export error: {str(e)}")
                    with st.expander("Error Details"):
                        st.code(traceback.format_exc())
        
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application function - FULLY FUNCTIONAL"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🚀 Sky-Port</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;">Comprehensive Hypixel SkyBlock Profile Exporter</p>', unsafe_allow_html=True)
    
    # Show feature status
    display_feature_status()
    
    # API Configuration
    with st.expander("🔑 API Configuration", expanded=not st.session_state.get('skyblock_profiles')):
        api_key = st.text_input(
            "Hypixel API Key",
            type="password",
            help="Get your API key by typing /api new in Hypixel",
            value=st.secrets.get("hypixel_api_key", "") if hasattr(st, 'secrets') and "hypixel_api_key" in st.secrets else ""
        )
        
        if not api_key:
            st.warning("⚠️ Please enter your Hypixel API key to continue.")
            st.info("💡 Get your API key by typing `/api new` in Hypixel chat.")
            st.markdown("""<div style="background: #e3f2fd; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
            <h4>How to get your API key:</h4>
            <ol>
                <li>Join Hypixel server</li>
                <li>Type <code>/api new</code> in chat</li>
                <li>Copy the generated key</li>
                <li>Paste it above</li>
            </ol>
            </div>""", unsafe_allow_html=True)
            return
    
    # Player lookup
    st.markdown("## 🎮 Player Lookup")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        username = st.text_input(
            "Minecraft Username",
            placeholder="Enter username (e.g., Technoblade, Dream, etc.)",
            help="Enter any Minecraft username to fetch their SkyBlock profiles"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        fetch_button = st.button("🔍 Fetch Profiles", type="primary", use_container_width=True)
    
    # Fetch player profiles
    if fetch_button and username:
        with st.spinner("🔍 Fetching player profiles..."):
            try:
                # Initialize API clients
                mojang_client = MojangAPI()
                hypixel_client = HypixelAPI(api_key)
                
                # Get UUID
                uuid_data = mojang_client.get_uuid(username)
                if not uuid_data:
                    st.error("❌ Player not found! Please check the username.")
                    return
                
                uuid = uuid_data['id']
                st.session_state.player_uuid = uuid
                
                # Get player and profile data
                player_data = hypixel_client.get_player(uuid)
                skyblock_data = hypixel_client.get_skyblock_profiles(uuid)
                
                if not skyblock_data or 'profiles' not in skyblock_data or not skyblock_data['profiles']:
                    st.error("❌ No SkyBlock profiles found for this player.")
                    st.info("This player may not have played SkyBlock or their profiles are private.")
                    return
                
                st.session_state.player_data = player_data
                st.session_state.skyblock_profiles = skyblock_data['profiles']
                
                st.success(f"✅ Found {len(skyblock_data['profiles'])} profile(s) for {username}!")
                
            except (PlayerNotFoundError, InvalidAPIKeyError, RateLimitError, MojangAPIError, HypixelAPIError) as e:
                st.error(f"❌ {str(e)}")
                return
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                with st.expander("Error Details (for debugging)"):
                    st.code(traceback.format_exc())
                return
    
    # Display profiles if available
    if st.session_state.get('skyblock_profiles'):
        display_profiles(st.session_state.skyblock_profiles)
    
    # Process selected profile
    process_selected_profile()
    
    # Display results and export options
    display_processed_data()
    display_export_options()
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<p style='text-align: center; color: #666;'>Built with ❤️ for the Hypixel SkyBlock community | Sky-Port v2.0.0</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()