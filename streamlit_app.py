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
    page_title="Fantasy Football Mock Draft Simulator v1.2",
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
            step=1
        )
        
        draft_position = st.number_input(
            "Your Draft Position",
            min_value=1,
            max_value=num_teams,
            value=st.session_state.get('draft_position', 1),
            step=1
        )
    
    with col2:
        st.subheader("Starting Lineup")
        qb_slots = st.number_input("QB", min_value=0, max_value=3, value=st.session_state.get('roster_config', {}).get('QB', 1))
        rb_slots = st.number_input("RB", min_value=0, max_value=5, value=st.session_state.get('roster_config', {}).get('RB', 2))
        wr_slots = st.number_input("WR", min_value=0, max_value=5, value=st.session_state.get('roster_config', {}).get('WR', 2))
        te_slots = st.number_input("TE", min_value=0, max_value=3, value=st.session_state.get('roster_config', {}).get('TE', 1))
        flex_slots = st.number_input("FLEX (RB/WR/TE)", min_value=0, max_value=3, value=st.session_state.get('roster_config', {}).get('FLEX', 1))
        k_slots = st.number_input("K", min_value=0, max_value=2, value=st.session_state.get('roster_config', {}).get('K', 1))
        dst_slots = st.number_input("DST", min_value=0, max_value=2, value=st.session_state.get('roster_config', {}).get('DST', 1))
        
        roster_config = {
            'QB': qb_slots,
            'RB': rb_slots,
            'WR': wr_slots,
            'TE': te_slots,
            'FLEX': flex_slots,
            'K': k_slots,
            'DST': dst_slots
        }
    
    with col3:
        st.subheader("Bench & Totals")
        bench_slots = st.number_input("Bench Spots", min_value=0, max_value=10, 
                                     value=st.session_state.get('roster_config', {}).get('BENCH', 6))
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
            # Save configuration - use the direct widget values
            st.session_state.num_teams = num_teams
            st.session_state.draft_position = draft_position
            st.session_state.roster_config = roster_config
            st.session_state.total_rounds = sum(roster_config.values())
            st.session_state.app_stage = 'keepers'
            st.rerun()

def render_keeper_config():
    """Render the keeper configuration page"""
    st.title("🎯 Keeper Configuration")
    
    st.markdown("**Step 3: Assign Keeper Players**")
    
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
            # Update draft position if it changed
            if draft_engine.user_position != st.session_state.draft_position:
                logger.info(f"Updating draft position from {draft_engine.user_position} to {st.session_state.draft_position}")
                draft_engine.user_position = st.session_state.draft_position
                # Re-initialize teams to update the "You" label
                draft_engine.teams = draft_engine._initialize_teams()
        
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
        # Ensure the draft position is correct
        if draft_engine.user_position != st.session_state.draft_position:
            logger.info(f"Updating draft position from {draft_engine.user_position} to {st.session_state.draft_position}")
            draft_engine.user_position = st.session_state.draft_position
            # Re-initialize teams to update the "You" label
            draft_engine.teams = draft_engine._initialize_teams()
    else:
        draft_engine = DraftEngine(
            players_df=st.session_state.players_df,
            num_teams=st.session_state.num_teams,
            draft_position=st.session_state.draft_position,
            roster_config=st.session_state.roster_config
        )
        st.session_state.draft_engine = draft_engine
    
    # Debug output
    logger.info(f"Draft page: user_position={draft_engine.user_position}, draft_position in session={st.session_state.draft_position}")
    
    # Initialize draft_in_progress flag
    if 'draft_in_progress' not in st.session_state:
        st.session_state.draft_in_progress = False
    
    # Create UI components
    ui = UIComponents()
    
    # Check if draft has started
    if not st.session_state.draft_in_progress:
        # Show title and instructions first
        st.title("🏈 Fantasy Football Mock Draft")
        
        # Show draft setup info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("League Size", f"{st.session_state.num_teams} Teams")
        with col2:
            st.metric("Your Draft Position", f"#{st.session_state.draft_position}")
        with col3:
            st.metric("Total Rounds", st.session_state.total_rounds)
        
        st.divider()
        
        # Add instructions expander with custom styling (pre-expanded when not started)
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
        
        with st.expander("📖 How to Use This Draft Tool", expanded=True):
            st.markdown(f"""
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
            - Green header indicates your team
            - Bold players with thick borders are keepers
            - Colors indicate positions: RB (teal), WR (blue), QB (red), TE (green)
            
            **Draft Format:**
            - Snake draft: Order reverses each round
            - Round 1: Pick 1→{st.session_state.num_teams}, Round 2: Pick {st.session_state.num_teams}→1, etc.
            - CPU teams auto-draft when it's their turn
            """)
        
        st.divider()
        
        # Start Draft button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 **START DRAFT**", type="primary", use_container_width=True,
                        help="Begin the mock draft"):
                st.session_state.draft_in_progress = True
                # Initialize draft board if not exists
                if 'draft_board' not in st.session_state:
                    st.session_state.draft_board = {}
                
                # Ensure the draft engine is properly initialized
                # Reset the current pick to 1 to start fresh
                draft_engine.current_pick = 1
                draft_engine.draft_complete = False
                
                # Log the state of the draft for debugging
                logger.info(f"Starting draft - Total players: {len(draft_engine.players_df)}")
                logger.info(f"Players marked as drafted: {draft_engine.players_df['drafted'].sum() if 'drafted' in draft_engine.players_df.columns else 'N/A'}")
                logger.info(f"Current pick: {draft_engine.current_pick}, User position: {draft_engine.user_position}")
                
                # Check if CPU has first pick and start autopicking
                if draft_engine.get_team_on_clock(1) != draft_engine.user_position:
                    st.session_state.cpu_needs_to_draft = True
                st.rerun()
        
        # Don't show draft board until started
        return
    
    # Draft has started - show the full interface
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
        # Show different options based on draft status
        if not draft_engine.draft_complete:
            # During draft - show reset with confirmation
            if 'show_reset_confirm' not in st.session_state:
                st.session_state.show_reset_confirm = False
            
            if not st.session_state.show_reset_confirm:
                if st.button("🔄 Reset Draft", use_container_width=True,
                            help="Start over from the beginning - requires confirmation"):
                    st.session_state.show_reset_confirm = True
                    st.rerun()
            else:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.show_reset_confirm = False
                    st.rerun()
                if st.button("✅ Confirm Reset", use_container_width=True, type="primary"):
                    st.session_state.show_reset_confirm = False
                    st.session_state.draft_in_progress = False
                    draft_engine.reset_draft()
                    st.session_state.draft_board = {}
                    # Re-apply keepers
                    draft_engine._restore_keepers_from_session()
                    st.rerun()
        else:
            # Draft complete - no button here, will be handled below
            pass
    
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
            # Use a placeholder for the status message that will auto-update
            logger.info(f"Auto-drafting: current_team={current_team}, user_position={draft_engine.user_position}")
            status_container = st.empty()
            status_container.info(f"🤖 Auto-drafting for {draft_engine.teams[current_team].owner_name}...")
            
            # Autopick for CPU team
            try:
                player_id = draft_engine.autopick(current_team)
                logger.info(f"Autopick returned player_id: {player_id} for team {current_team}")
                if player_id is not None:
                    if draft_engine.make_pick(player_id):
                        # Clear the status message before rerun
                        status_container.empty()
                        st.rerun()
                    else:
                        logger.error(f"make_pick failed for player_id {player_id}, team {current_team}")
                        status_container.error(f"Failed to make pick for {draft_engine.teams[current_team].owner_name}")
                else:
                    logger.error(f"Autopick returned None for team {current_team}")
                    status_container.error(f"No valid player found for {draft_engine.teams[current_team].owner_name}")
            except Exception as e:
                logger.error(f"Exception during autopick: {str(e)}")
                status_container.error(f"Error during autopick: {str(e)}")
    
    # Show instructions expander (collapsed during active draft)
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
        - Green header indicates your team
        - Bold players with thick borders are keepers
        - Colors indicate positions: RB (teal), WR (blue), QB (red), TE (green)
        
        **Draft Format:**
        - Snake draft: Order reverses each round
        - CPU teams auto-draft when it's their turn
        """)
    
    ui.render_draft_board(draft_engine, st.session_state.total_rounds)
    
    # Export section and restart options
    if draft_engine.draft_complete:
        st.divider()
        
        # Success message
        st.success("🎉 **Draft Complete!** All teams have filled their rosters.")
        
        # Export section
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
        
        # Restart options
        st.divider()
        st.subheader("🔄 Start Another Draft")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Run Another Mock Draft**
            - Keep same league settings
            - Keep same keepers
            - Keep same draft position
            - Start a fresh draft
            """)
            if st.button("🔁 **Run Another Mock**", type="primary", use_container_width=True,
                        help="Start a new draft with the same settings and keepers"):
                # Reset only the draft-specific data, keep settings
                draft_engine.reset_draft()
                st.session_state.draft_board = {}
                st.session_state.show_reset_confirm = False
                st.session_state.draft_in_progress = False  # Reset to show Start Draft screen
                # Re-apply keepers
                draft_engine._restore_keepers_from_session()
                st.rerun()
        
        with col2:
            st.markdown("""
            **Start Over Completely**
            - Upload new rankings
            - Configure new league
            - Set new keepers
            - Fresh start
            """)
            if st.button("🆕 **Start Fresh**", type="secondary", use_container_width=True,
                        help="Start completely over with new rankings and settings"):
                # Clear everything and go back to upload
                st.session_state.app_stage = 'upload'
                for key in ['players_df', 'draft_engine', 'draft_started', 'draft_board', 
                           'num_teams', 'draft_position', 'roster_config', 'total_rounds',
                           'keeper_data', 'show_reset_confirm', 'draft_in_progress']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

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