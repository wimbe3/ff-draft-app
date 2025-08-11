"""
Fantasy Football Mock Draft Simulator
Main application entry point
"""

import streamlit as st
import pandas as pd
import logging
from datetime import datetime
import os
from typing import Optional, Dict, Any

# Import custom modules
from session_manager import SessionManager
from data_processor import DataProcessor
from draft_logic import DraftEngine
from ui_components import UIComponents
from export_manager import ExportManager
from styles import apply_custom_styles
from config import (
    DraftConfig, RosterConfig, ERROR_MESSAGES,
    setup_logging
)

# Setup logging
logger = setup_logging()

# Page configuration
st.set_page_config(
    page_title="Fantasy Football Mock Draft Simulator",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS
apply_custom_styles()

def render_upload_page():
    """Render the file upload page"""
    st.title("🏈 Fantasy Football Mock Draft Simulator")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### Step 1: Upload Rankings
        
        **📥 Download Rankings:**
        
        **[Get Rankings from FantasyPros →](https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php)**
        
        **Important:** Select your scoring type first!
        - PPR (Point Per Reception)
        - Half-PPR (0.5 points per reception)  
        - Standard (no reception points)
        
        Then click "Export" to download CSV
        """)
        
        uploaded_file = st.file_uploader(
            "Choose your rankings CSV file",
            type=['csv'],
            help="Upload your player rankings CSV file from FantasyPros"
        )
        
        if uploaded_file is not None:
            # Process the file
            data_processor = DataProcessor()
            players_df = data_processor.load_uploaded_file(uploaded_file)
            
            if players_df is not None:
                st.session_state.players_df = players_df
                st.session_state.uploaded_file = uploaded_file
                st.session_state.app_stage = 'league_config'
                st.success("✅ Rankings loaded successfully!")
                st.rerun()
            else:
                st.error("Failed to load rankings. Please check your CSV format.")
    
    with col2:
        st.markdown("""
        ### How it Works
        
        **1️⃣ Upload Rankings**
        Get your rankings from FantasyPros with your league's scoring type
        
        **2️⃣ Configure League**
        Set number of teams, your draft position, and roster requirements
        
        **3️⃣ Set Keepers**
        Assign keeper players to teams and rounds
        
        **4️⃣ Run Mock Draft**
        Practice your draft with smart autopick AI
        
        ---
        
        **Features:**
        - 🤖 Smart autopick algorithm
        - 🎯 Full keeper support
        - 📊 Live draft analysis
        - 💾 Export results
        - 🎨 Beautiful draft board
        """)

def render_league_config():
    """Render the league configuration page"""
    st.title("⚙️ League Configuration")
    
    st.markdown("### Step 2: Configure Your League Settings")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.subheader("League Size")
        num_teams = st.number_input(
            "Number of Teams",
            min_value=8,
            max_value=14,
            value=st.session_state.get('num_teams', 12),
            step=1,
            key='num_teams_config'
        )
        
        draft_position = st.number_input(
            "Your Draft Position",
            min_value=1,
            max_value=num_teams,
            value=st.session_state.get('draft_position', 1),
            step=1,
            key='draft_position_config'
        )
    
    with col2:
        st.subheader("Starting Lineup")
        roster_config = {
            'QB': st.number_input("QB", min_value=0, max_value=3, value=1, key='qb_slots'),
            'RB': st.number_input("RB", min_value=0, max_value=5, value=2, key='rb_slots'),
            'WR': st.number_input("WR", min_value=0, max_value=5, value=2, key='wr_slots'),
            'TE': st.number_input("TE", min_value=0, max_value=3, value=1, key='te_slots'),
            'FLEX': st.number_input("FLEX (RB/WR/TE)", min_value=0, max_value=3, value=1, key='flex_slots'),
            'K': st.number_input("K", min_value=0, max_value=2, value=1, key='k_slots'),
            'DST': st.number_input("DST", min_value=0, max_value=2, value=1, key='dst_slots'),
        }
    
    with col3:
        st.subheader("Bench & Totals")
        bench_slots = st.number_input("Bench Spots", min_value=0, max_value=10, value=6, key='bench_slots')
        roster_config['BENCH'] = bench_slots
        
        total_starters = sum([v for k, v in roster_config.items() if k != 'BENCH'])
        total_roster = sum(roster_config.values())
        
        st.metric("Starting Lineup", total_starters)
        st.metric("Total Roster Size", total_roster)
        st.metric("Total Rounds", total_roster)
    
    st.divider()
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back to Upload", use_container_width=True):
            st.session_state.app_stage = 'upload'
            st.rerun()
    
    with col2:
        pass
    
    with col3:
        if st.button("Continue to Keepers →", type="primary", use_container_width=True):
            # Save configuration
            st.session_state.num_teams = num_teams
            st.session_state.draft_position = draft_position
            st.session_state.roster_config = roster_config
            st.session_state.total_rounds = sum(roster_config.values())
            st.session_state.app_stage = 'keepers'
            st.rerun()

def render_keeper_config():
    """Render the keeper configuration page"""
    st.title("🎯 Keeper Configuration")
    
    st.markdown("### Step 3: Assign Keeper Players")
    
    # Initialize or use existing draft engine
    if 'players_df' in st.session_state:
        # Check if draft engine already exists in session state
        if 'draft_engine' not in st.session_state:
            draft_engine = DraftEngine(
                players_df=st.session_state.players_df,
                num_teams=st.session_state.num_teams,
                draft_position=st.session_state.draft_position,
                roster_config=st.session_state.roster_config
            )
            st.session_state.draft_engine = draft_engine
        else:
            # Use existing draft engine to preserve keeper data
            draft_engine = st.session_state.draft_engine
        
        # Use UI component to render keeper interface
        ui = UIComponents()
        ui.render_keeper_configuration(draft_engine)
        
        st.divider()
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("← Back to League Config", use_container_width=True):
                st.session_state.app_stage = 'league_config'
                st.rerun()
        
        with col2:
            # Count total keepers
            total_keepers = sum(len(team.keepers) for team in draft_engine.teams.values())
            st.metric("Total Keepers Set", total_keepers)
        
        with col3:
            if st.button("Continue to Draft →", type="primary", use_container_width=True):
                # Make sure draft engine is saved to session state
                st.session_state.draft_engine = draft_engine
                st.session_state.app_stage = 'draft'
                st.session_state.draft_started = True
                st.rerun()
    else:
        st.error("No player data loaded. Please go back and upload a rankings file.")
        if st.button("← Back to Upload"):
            st.session_state.app_stage = 'upload'
            st.rerun()

def render_draft_page():
    """Render the main draft page"""
    
    # Initialize draft engine
    if 'players_df' not in st.session_state:
        st.error("No player data loaded. Please start from the beginning.")
        if st.button("Start Over"):
            st.session_state.app_stage = 'upload'
            st.rerun()
        return
    
    # Use existing draft engine or create new one
    if 'draft_engine' in st.session_state:
        draft_engine = st.session_state.draft_engine
    else:
        draft_engine = DraftEngine(
            players_df=st.session_state.players_df,
            num_teams=st.session_state.num_teams,
            draft_position=st.session_state.draft_position,
            roster_config=st.session_state.roster_config
        )
        st.session_state.draft_engine = draft_engine
    
    # Create UI components
    ui = UIComponents()
    
    # Header with draft controls
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
    
    with col1:
        st.title("🏈 Mock Draft in Progress")
    
    with col2:
        current_pick = draft_engine.current_pick
        st.metric("Current Pick", f"#{current_pick}")
    
    with col3:
        current_round = ((current_pick - 1) // st.session_state.num_teams) + 1
        st.metric("Round", f"{current_round}/{st.session_state.total_rounds}")
    
    with col4:
        on_clock_team = draft_engine.get_team_on_clock(current_pick)
        on_clock_owner = draft_engine.teams[on_clock_team].owner_name
        st.metric("On Clock", on_clock_owner)
    
    with col5:
        if st.button("🔄 Reset Draft", use_container_width=True,
                    help="Start over from the beginning - requires confirmation"):
            if st.button("Confirm Reset?", key="confirm_reset"):
                st.session_state.app_stage = 'upload'
                for key in ['players_df', 'draft_engine', 'draft_started']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    # Auto-draft for CPU teams if it's not the user's turn
    if not draft_engine.draft_complete:
        current_team = draft_engine.get_team_on_clock(draft_engine.current_pick)
        current_round = ((draft_engine.current_pick - 1) // draft_engine.num_teams) + 1
        
        # Check if this pick is a keeper slot
        is_keeper_slot = False
        if current_team in draft_engine.keepers:
            for keeper_player_id, keeper_round in draft_engine.keepers[current_team]:
                if keeper_round == current_round:
                    is_keeper_slot = True
                    break
        
        if is_keeper_slot:
            # Skip this pick as it's already filled by a keeper
            draft_engine.current_pick += 1
            st.rerun()
        elif current_team != draft_engine.user_position:
            # Show status message
            st.info(f"🤖 Auto-drafting for {draft_engine.teams[current_team].owner_name}...")
            # Autopick for CPU team
            player_id = draft_engine.autopick(current_team)
            if player_id and draft_engine.make_pick(player_id):
                st.rerun()
    
    # Main draft interface - all on one page
    # Add instructions expander with custom styling
    st.markdown("""
    <style>
    /* Style the expander */
    div[data-testid="stExpander"] > details {
        border: 2px solid black !important;
        border-radius: 8px;
        padding: 5px;
        background-color: #f8f9fa;
    }
    
    /* Style the expander content */
    div[data-testid="stExpander"] > details > div {
        font-size: 16px !important;
    }
    
    /* Style the expander header */
    div[data-testid="stExpander"] > details > summary {
        font-size: 18px !important;
        font-weight: bold !important;
        color: #2c3e50 !important;
    }
    
    /* Style the expander arrow */
    div[data-testid="stExpander"] > details > summary > svg {
        width: 24px !important;
        height: 24px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.expander("📖 How to Use This Draft Tool", expanded=False):
        st.markdown("""
        ### Draft Instructions
        
        **Making Your Pick:**
        1. When it's your turn, you'll see "On Clock" highlighted in yellow
        2. Browse available players in the table below the draft board
        3. Click the **checkbox in the leftmost column** of a player row to select them
        4. Click "🎯 Make Pick" to draft that player
        
        **Draft Controls:**
        - **🤖 Autopick** - Let the AI make one pick for the current team
        - **🔄 Reset Draft** - Start over from the beginning
        
        **Understanding the Board:**
        - Each column represents a team's picks
        - Green header (#2) indicates your team
        - Bold players with thick borders are keepers
        - Colors indicate positions: RB (teal), WR (blue), QB (red), TE (green)
        
        **Draft Format:**
        - Snake draft: Order reverses each round
        - Round 1: Teams 1→10, Round 2: Teams 10→1, etc.
        - CPU teams auto-draft when it's their turn
        """)
    
    ui.render_draft_board(draft_engine, st.session_state.total_rounds)
    
    # Export section
    if draft_engine.draft_complete:
        st.divider()
        st.subheader("📥 Export Draft Results")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            export_manager = ExportManager()
            csv_data = export_manager.export_to_csv(draft_engine)
            st.download_button(
                label="📊 Download CSV",
                data=csv_data,
                file_name=f"mock_draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            html_data = export_manager.export_to_html(draft_engine)
            st.download_button(
                label="🌐 Download HTML Report",
                data=html_data,
                file_name=f"mock_draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html",
                use_container_width=True
            )
        
        with col3:
            json_data = export_manager.export_to_json(draft_engine)
            st.download_button(
                label="📄 Download JSON",
                data=json_data,
                file_name=f"mock_draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

def main():
    """Main application function"""
    
    # Initialize session manager
    session = SessionManager()
    session.initialize_session()
    
    # Initialize app stage if not set
    if 'app_stage' not in st.session_state:
        st.session_state.app_stage = 'upload'
    
    # Route to appropriate page based on stage
    if st.session_state.app_stage == 'upload':
        render_upload_page()
    elif st.session_state.app_stage == 'league_config':
        render_league_config()
    elif st.session_state.app_stage == 'keepers':
        render_keeper_config()
    elif st.session_state.app_stage == 'draft':
        render_draft_page()
    else:
        # Default to upload page
        st.session_state.app_stage = 'upload'
        st.rerun()

if __name__ == "__main__":
    main()