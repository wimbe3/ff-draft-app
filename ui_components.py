"""
UI components module for Fantasy Football Mock Draft Simulator
Handles all UI rendering and user interactions
"""

import streamlit as st
import pandas as pd
import logging
from typing import Dict, List, Optional, Any
from functools import partial
import plotly.graph_objects as go
import plotly.express as px
from config import (
    POSITION_COLORS, POSITION_EMOJI, MAX_PLAYER_NAME_LENGTH,
    PLAYER_NAME_TRUNCATE_SUFFIX, BOARD_ROUND_LABEL_WIDTH,
    BOARD_TEAM_COLUMN_WIDTH, ERROR_MESSAGES, setup_logging
)

# Setup logging
logger = setup_logging()

class UIComponents:
    """Handles all UI component rendering"""
    
    def __init__(self):
        self.position_colors = POSITION_COLORS
        self.position_emoji = POSITION_EMOJI
        logger.debug("UIComponents initialized with config values")
    
    def render_draft_board(self, draft_engine, total_rounds: int):
        """Render the main draft board grid with team owners"""
        
        st.subheader("📋 Draft Board")
        
        # Display team owners header with round label column
        header_cols = st.columns([0.5] + [1] * draft_engine.num_teams)
        
        # Empty space for round column
        with header_cols[0]:
            st.markdown(
                """<div style='
                    background-color: #e9ecef;
                    color: #495057;
                    padding: 6px;
                    border-radius: 4px;
                    text-align: center;
                    font-weight: bold;
                    font-size: 12px;
                    border: 1px solid #dee2e6;
                '>Round</div>""",
                unsafe_allow_html=True
            )
        
        # Team headers
        for i in range(draft_engine.num_teams):
            team_id = i + 1
            owner_name = draft_engine.teams[team_id].owner_name
            with header_cols[i + 1]:
                is_user = team_id == draft_engine.user_position
                bg_color = '#28a745' if is_user else '#f8f9fa'
                border_color = '#1e7e34' if is_user else '#dee2e6'
                text_color = 'white' if is_user else '#495057'
                
                st.markdown(
                    f"""<div style='
                        background-color: {bg_color};
                        color: {text_color};
                        padding: 8px 4px;
                        border-radius: 4px;
                        text-align: center;
                        font-size: 11px;
                        font-weight: bold;
                        border: 1px solid {border_color};
                    '>
                        <div>#{team_id}</div>
                        <div style='font-weight: normal; font-size: 10px;'>{owner_name}</div>
                    </div>""",
                    unsafe_allow_html=True
                )
        
        st.divider()
        
        # Create draft board grid
        board_data = []
        
        for round_num in range(1, total_rounds + 1):  # Show all rounds
            round_picks = []
            
            for team_num in range(1, draft_engine.num_teams + 1):
                # Get pick from draft board - always use team_num as position
                pick_data = st.session_state.draft_board.get(round_num, {}).get(team_num)
                
                if pick_data:
                    # Format player name - truncate if too long
                    player_name = pick_data.player_name
                    if len(player_name) > 18:
                        player_name = player_name[:18] + "."
                    
                    # Include team abbreviation if available
                    team_abbr = getattr(pick_data, 'team_abbr', '')
                    if team_abbr:
                        pick_display = f"{player_name}\n{pick_data.position} - {team_abbr}"
                    else:
                        pick_display = f"{player_name}\n{pick_data.position}"
                    
                    color = self.position_colors.get(pick_data.position, '#CCCCCC')
                    is_keeper = getattr(pick_data, 'is_keeper', False)
                else:
                    pick_display = ""  # Empty cell until picked
                    color = '#F8F8F8'
                    is_keeper = False
                
                round_picks.append({
                    'team': team_num,
                    'display': pick_display,
                    'color': color,
                    'picked': pick_data is not None,
                    'is_keeper': is_keeper,
                    'round': round_num,
                    'position': team_num
                })
            
            board_data.append(round_picks)
        
        # Render as grid with round numbers
        for round_idx, round_picks in enumerate(board_data):
            # Create columns with extra space for round number
            all_cols = st.columns([0.5] + [1] * draft_engine.num_teams)
            
            # Round number in first column
            with all_cols[0]:
                st.markdown(
                    f"""<div style='
                        background-color: #e9ecef;
                        color: #495057;
                        padding: 6px;
                        border-radius: 4px;
                        text-align: center;
                        font-weight: bold;
                        font-size: 12px;
                        margin-top: 2px;
                        border: 1px solid #dee2e6;
                    '>R{round_idx + 1}</div>""",
                    unsafe_allow_html=True
                )
            
            # Player picks in remaining columns
            for col_idx, pick_info in enumerate(round_picks):
                with all_cols[col_idx + 1]:
                    # Highlight current pick
                    current_round = ((draft_engine.current_pick - 1) // draft_engine.num_teams) + 1
                    current_pos = ((draft_engine.current_pick - 1) % draft_engine.num_teams) + 1
                    
                    is_current = (round_idx + 1 == current_round and col_idx + 1 == current_pos)
                    
                    if pick_info['picked']:
                        # Drafted player cell
                        font_weight = 'bold' if pick_info['is_keeper'] else 'normal'
                        border_style = '2px solid #333' if pick_info['is_keeper'] else '1px solid #ddd'
                        
                        st.markdown(
                            f"""<div style='
                                background-color: {pick_info['color']};
                                border: {border_style};
                                padding: 6px 4px;
                                border-radius: 4px;
                                text-align: center;
                                font-size: 11px;
                                font-weight: {font_weight};
                                white-space: pre-line;
                                line-height: 1.3;
                                color: white;
                                text-shadow: 1px 1px 1px rgba(0,0,0,0.3);
                            '>{pick_info['display']}</div>""",
                            unsafe_allow_html=True
                        )
                    elif is_current:
                        # Current pick cell (on the clock)
                        st.markdown(
                            f"""<div style='
                                background-color: #FFE4B5;
                                border: 3px solid #FFD700;
                                padding: 6px 4px;
                                border-radius: 4px;
                                text-align: center;
                                font-weight: bold;
                                animation: pulse 2s infinite;
                                min-height: 40px;
                            '>On Clock</div>""",
                            unsafe_allow_html=True
                        )
                    else:
                        # Empty cell
                        st.markdown(
                            f"""<div style='
                                background-color: {pick_info['color']};
                                border: 1px solid #e0e0e0;
                                padding: 6px 4px;
                                border-radius: 4px;
                                text-align: center;
                                font-size: 11px;
                                min-height: 40px;
                            '>&nbsp;</div>""",
                            unsafe_allow_html=True
                        )
        
        # Show available players instead of team rosters
        st.divider()
        self.render_player_rankings(draft_engine)
    
    def render_player_rankings(self, draft_engine):
        """Render the available players panel"""
        
        st.subheader("📊 Available Players")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input("🔍 Search", placeholder="Player name, team...",
                                       help="Filter players by name or team")
        
        with col2:
            position_filter = st.selectbox(
                "Position",
                ["All"] + list(self.position_colors.keys()),
                key="position_filter",
                help="Filter by position group"
            )
        
        with col3:
            show_drafted = st.checkbox("Show Drafted", value=False,
                                      help="Include already drafted players in the list")
        
        # Get available players
        players_df = draft_engine.players_df.copy()
        
        # Apply filters
        if not show_drafted:
            players_df = players_df[~players_df['drafted']]
        
        if search_term:
            players_df = players_df[
                players_df['search_field'].str.contains(search_term.lower(), na=False)
            ]
        
        if position_filter != "All":
            players_df = players_df[players_df['base_position'] == position_filter]
        
        # Display controls - Key action buttons side by side
        # Add custom CSS for larger draft buttons
        st.markdown("""
        <style>
        /* Make draft action buttons larger and more prominent */
        div[data-testid="column"]:has(button:has-text("Make Pick")),
        div[data-testid="column"]:has(button:has-text("Autopick")),
        div[data-testid="column"]:has(button:has-text("Skip Keeper")) {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* Target the specific draft buttons and make them larger */
        button[kind="primary"]:has-text("Make Pick"),
        button[kind="secondary"]:has-text("Autopick"),
        button[kind="primary"]:has-text("Skip Keeper"),
        div:has(> button:has-text("Make Pick")) button,
        div:has(> button:has-text("Autopick")) button,
        div:has(> button:has-text("Skip Keeper")) button {
            font-size: 18px !important;
            padding: 15px 30px !important;
            height: auto !important;
            min-height: 60px !important;
            font-weight: bold !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Check if current pick is a keeper slot
        current_team = draft_engine.get_team_on_clock(draft_engine.current_pick)
        current_round = ((draft_engine.current_pick - 1) // draft_engine.num_teams) + 1
        is_keeper_slot = False
        
        if current_team in draft_engine.keepers:
            for keeper_player_id, keeper_round in draft_engine.keepers[current_team]:
                if keeper_round == current_round:
                    is_keeper_slot = True
                    break
        
        if is_keeper_slot and current_team == draft_engine.user_position:
            # Skip keeper slot for user - centered button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("⏭️ Skip Keeper", type="primary", use_container_width=True,
                            help="Skip this pick (already filled by keeper)"):
                    draft_engine.current_pick += 1
                    st.rerun()
        else:
            # Make Pick and Autopick buttons side by side - minimal spacing
            col1, col2, col3, col4 = st.columns([0.8, 0.8, 0.1, 3.3])
            
            with col1:
                if st.button("🎯 **Make Pick**", type="primary", disabled=draft_engine.draft_complete, 
                            use_container_width=True,
                            help="Draft the selected player for your team"):
                    selected_rows = st.session_state.get('selected_player_rows', [])
                    if selected_rows:
                        player_id = players_df.iloc[selected_rows[0]].name
                        if draft_engine.make_pick(player_id):
                            st.success(f"Drafted {players_df.iloc[selected_rows[0]]['player_name']}!")
                            st.rerun()
                        else:
                            st.error("Failed to make pick")
                    else:
                        st.warning("Please select a player first")
            
            with col2:
                if st.button("🤖 **Autopick**", type="secondary",
                            use_container_width=True,
                            help="Let the AI make the best pick for the team currently on the clock"):
                    team_id = draft_engine.get_team_on_clock(draft_engine.current_pick)
                    player_id = draft_engine.autopick(team_id)
                    if player_id and draft_engine.make_pick(player_id):
                        st.rerun()
        
        # Display players table - show SOS instead of tier/adp
        display_columns = ['rank', 'player_name', 'team', 'base_position', 'bye']
        
        # Add SOS if it exists in the data
        sos_column = None
        if 'sos' in players_df.columns:
            display_columns.append('sos')
            sos_column = 'sos'
        elif 'SOS' in players_df.columns:
            display_columns.append('SOS')
            sos_column = 'SOS'
        
        # Rename columns for display
        display_df = players_df[display_columns].head(50).copy()
        
        # Convert SOS star ratings to text labels with visual indicators
        if sos_column:
            sos_mapping = {
                '5 out of 5 stars': 'Great',
                '4 out of 5 stars': 'Favorable',
                '3 out of 5 stars': 'Neutral',
                '2 out of 5 stars': 'Unfavorable',
                '1 out of 5 stars': 'Poor',
                # Handle any variations
                '5': 'Great',
                '4': 'Favorable',
                '3': 'Neutral',
                '2': 'Unfavorable',
                '1': 'Poor',
                5: 'Great',
                4: 'Favorable',
                3: 'Neutral',
                2: 'Unfavorable',
                1: 'Poor'
            }
            
            # Map to text labels first
            display_df[sos_column] = display_df[sos_column].map(lambda x: sos_mapping.get(x, x))
            
            # Then add emoji indicators for visual clarity
            def format_sos_with_indicator(val):
                if val == 'Great':
                    return '🟢 Great'
                elif val == 'Favorable':
                    return '✅ Favorable'  
                elif val == 'Neutral':
                    return '➖ Neutral'
                elif val == 'Unfavorable':
                    return '⚠️ Unfavorable'
                elif val == 'Poor':
                    return '🔴 Poor'
                return val
            
            display_df[sos_column] = display_df[sos_column].apply(format_sos_with_indicator)
        
        column_rename = {
            'rank': 'Rank',
            'player_name': 'Player',
            'team': 'Team',
            'base_position': 'Pos',
            'bye': 'Bye',
            'sos': 'SOS',
            'SOS': 'SOS'
        }
        display_df = display_df.rename(columns=column_rename)
        
        # Add custom CSS for clean table styling
        st.markdown("""
        <style>
        /* Container styling with border */
        div[data-testid="stDataFrame"] {
            border: 1px solid #dee2e6 !important;
            border-radius: 8px !important;
            overflow: hidden !important;
            background-color: white !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        }
        
        /* White background for dataframe */
        div[data-testid="stDataFrame"] > div {
            background-color: white !important;
        }
        
        /* Table styling */
        div[data-testid="stDataFrame"] table {
            background-color: white !important;
            border-collapse: collapse !important;
        }
        
        /* Header styling */
        div[data-testid="stDataFrame"] thead tr {
            background-color: #f8f9fa !important;
            border-bottom: 2px solid #dee2e6 !important;
        }
        
        div[data-testid="stDataFrame"] thead th {
            color: #495057 !important;
            font-weight: 600 !important;
            padding: 12px 8px !important;
            border-right: 1px solid #e9ecef !important;
        }
        
        /* Body cell styling */
        div[data-testid="stDataFrame"] tbody td {
            padding: 10px 8px !important;
            border-right: 1px solid #f1f3f5 !important;
            border-bottom: 1px solid #f1f3f5 !important;
            color: #212529 !important;
        }
        
        /* Row hover effect */
        div[data-testid="stDataFrame"] tbody tr:hover {
            background-color: rgba(0, 123, 255, 0.05) !important;
            cursor: pointer;
        }
        
        /* Selected row styling */
        div[data-testid="stDataFrame"] tbody tr[aria-selected="true"] {
            background-color: rgba(0, 123, 255, 0.1) !important;
            border-left: 3px solid #007bff !important;
        }
        
        /* Checkbox column styling */
        div[data-testid="stDataFrame"] tbody td:first-child {
            text-align: center !important;
            border-left: none !important;
        }
        
        /* Remove last column border */
        div[data-testid="stDataFrame"] tbody td:last-child,
        div[data-testid="stDataFrame"] thead th:last-child {
            border-right: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Make dataframe selectable with clean styling
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            selection_mode="single-row",
            on_select="rerun",
            key="player_selection"
        )
        
        # Store selected rows
        if "player_selection" in st.session_state:
            st.session_state.selected_player_rows = st.session_state.player_selection.selection.rows
    
    def render_team_rosters(self, draft_engine):
        """Render team rosters view"""
        
        st.subheader("👥 Team Rosters")
        
        # Team selector with owner names
        team_options = {}
        for i in range(1, draft_engine.num_teams + 1):
            owner_name = draft_engine.teams[i].owner_name
            display_name = f"Pick #{i} - {owner_name}"
            team_options[display_name] = i
        
        selected_team_name = st.selectbox("Select Team", list(team_options.keys()))
        selected_team_id = team_options[selected_team_name]
        
        team = draft_engine.teams[selected_team_id]
        
        # Display roster
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("**Current Roster:**")
            
            if team.roster:
                roster_df = pd.DataFrame([
                    {
                        'Round': pick.round,
                        'Pick': pick.pick_number if pick.pick_number > 0 else 'K',
                        'Player': pick.player_name,
                        'Position': pick.position
                    }
                    for pick in team.roster
                ])
                
                st.dataframe(
                    roster_df,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No players drafted yet")
        
        with col2:
            st.write("**Position Summary:**")
            
            roster_by_pos = team.get_roster_by_position()
            needs = draft_engine._calculate_team_needs(team)
            
            for position in ['QB', 'RB', 'WR', 'TE', 'FLEX', 'K', 'DST']:
                current = len(roster_by_pos.get(position, []))
                required = draft_engine.roster_config.get(position, 0)
                need_score = needs.get(position, 0)
                
                if need_score > 0.7:
                    status = "🔴"
                elif need_score > 0.3:
                    status = "🟡"
                else:
                    status = "🟢"
                
                st.write(f"{status} **{position}:** {current}/{required}")
    
    def render_keeper_configuration(self, draft_engine):
        """Render keeper configuration interface with editable table"""
        
        st.markdown("""
        Configure keepers for each team by selecting players and rounds from the dropdowns.
        Each team can have multiple keepers, but only one keeper per round.
        
        **Instructions:**
        1. Select a player and round for each team that has a keeper
        2. Review all your selections
        3. Click "Set All Keepers" to apply all changes at once
        """)
        
        # Get all players (including those already kept, since we need to be able to reassign them)
        all_players = draft_engine.players_df.copy()
        # For dropdowns, we'll use all players
        player_options = ['None'] + all_players['player_name'].tolist()
        # For finding player IDs when setting keepers, we'll also use all players
        available_players = all_players
        
        # Create editable keeper table for all teams
        st.write("### Keeper Assignments")
        
        # Initialize keeper selections in session state if not present
        if 'pending_keeper_selections' not in st.session_state:
            st.session_state.pending_keeper_selections = {}
            # Pre-populate with existing keepers
            for team_id in range(1, draft_engine.num_teams + 1):
                current_keeper = None
                current_round = 1
                for keeper in draft_engine.teams[team_id].keepers:
                    current_keeper = keeper.player_name
                    current_round = keeper.round
                    break
                st.session_state.pending_keeper_selections[team_id] = {
                    'player': current_keeper if current_keeper else 'None',
                    'round': current_round
                }
        
        # Helper function to update player selection
        def update_player_selection(team_id):
            st.session_state.pending_keeper_selections[team_id]['player'] = st.session_state[f"keeper_player_{team_id}"]
        
        # Helper function to update round selection
        def update_round_selection(team_id):
            st.session_state.pending_keeper_selections[team_id]['round'] = st.session_state[f"keeper_round_{team_id}"]
        
        # Create columns for the table header (removed Action column)
        col1, col2, col3, col4, col5 = st.columns([1, 2.5, 3.5, 1.5, 1])
        with col1:
            st.markdown("**Draft Pick**")
        with col2:
            st.markdown("**Team Owner**")
        with col3:
            st.markdown("**Player**")
        with col4:
            st.markdown("**Round**")
        with col5:
            st.markdown("**Status**")
        
        st.divider()
        
        # Track pending changes
        has_pending_changes = False
        
        # Get all currently selected players (to filter from dropdowns)
        # Only track players selected in the pending selections, not already drafted players
        selected_players = set()
        for tid in range(1, draft_engine.num_teams + 1):
            player = st.session_state.pending_keeper_selections[tid]['player']
            if player != 'None':
                selected_players.add(player)
        
        # Create a row for each team
        for team_id in range(1, draft_engine.num_teams + 1):
            col1, col2, col3, col4, col5 = st.columns([1, 2.5, 3.5, 1.5, 1])
            
            with col1:
                # Draft Pick (non-editable)
                draft_pick_text = f"#{team_id}"
                if team_id == draft_engine.user_position:
                    st.markdown(f"**{draft_pick_text}** 📍")
                else:
                    st.write(draft_pick_text)
            
            with col2:
                # Team Owner (editable text input)
                owner_name = st.text_input(
                    "Owner",
                    value=draft_engine.teams[team_id].owner_name,
                    key=f"owner_{team_id}",
                    label_visibility="collapsed"
                )
                # Update owner name immediately when changed
                if owner_name != draft_engine.teams[team_id].owner_name:
                    draft_engine.update_team_owner(team_id, owner_name)
            
            with col3:
                # Player dropdown - use pending selection
                current_selection = st.session_state.pending_keeper_selections[team_id]['player']
                
                # Filter out players already selected by other teams
                available_for_team = ['None']
                for player in player_options[1:]:  # Skip 'None'
                    # Include if not selected by anyone, or if it's this team's current selection
                    if player not in selected_players or player == current_selection:
                        available_for_team.append(player)
                
                selected_player = st.selectbox(
                    "Player",
                    available_for_team,
                    index=available_for_team.index(current_selection) if current_selection in available_for_team else 0,
                    key=f"keeper_player_{team_id}",
                    label_visibility="collapsed",
                    on_change=partial(update_player_selection, team_id)
                )
            
            with col4:
                # Round selection - use pending selection
                current_round = st.session_state.pending_keeper_selections[team_id]['round']
                
                selected_round = st.selectbox(
                    "Round",
                    range(1, draft_engine.total_rounds + 1),
                    index=current_round - 1,
                    key=f"keeper_round_{team_id}",
                    label_visibility="collapsed",
                    on_change=partial(update_round_selection, team_id)
                )
            
            with col5:
                # Status indicator
                # Check if this selection differs from current keeper
                current_keeper_name = None
                current_keeper_round = None
                for keeper in draft_engine.teams[team_id].keepers:
                    current_keeper_name = keeper.player_name
                    current_keeper_round = keeper.round
                    break
                
                if selected_player != 'None':
                    if current_keeper_name != selected_player or current_keeper_round != selected_round:
                        st.markdown("🔄 **Pending**")
                        has_pending_changes = True
                    else:
                        st.markdown("✅ **Set**")
                elif current_keeper_name is not None:
                    # Had a keeper but now selecting None
                    st.markdown("❌ **Remove**")
                    has_pending_changes = True
                else:
                    st.markdown("➖")
        
        st.divider()
        
        # Action buttons - Set All Keepers and Clear Pending
        if has_pending_changes:
            col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
            with col2:
                if st.button("🎯 **Set All Keepers**", type="primary", use_container_width=True,
                            help="Apply all pending keeper changes at once"):
                    # Validate and apply all keeper changes
                    success_messages = []
                    error_messages = []
                    
                    # First, clear all existing keepers (this will unmark them as drafted)
                    for team_id in range(1, draft_engine.num_teams + 1):
                        for keeper in draft_engine.teams[team_id].keepers[:]:
                            draft_engine.remove_keeper(team_id, keeper.player_id)
                    
                    # Now get fresh player data after clearing keepers
                    # This ensures previously kept players are now available
                    fresh_players_df = draft_engine.players_df.copy()
                    
                    # Then apply all new selections
                    for team_id in range(1, draft_engine.num_teams + 1):
                        player_name = st.session_state.pending_keeper_selections[team_id]['player']
                        selected_round = st.session_state.pending_keeper_selections[team_id]['round']
                        
                        if player_name != 'None':
                            # Find player ID using fresh data
                            player_row = fresh_players_df[fresh_players_df['player_name'] == player_name]
                            if not player_row.empty:
                                player_id = player_row.index[0]
                                if draft_engine.set_keeper(team_id, player_id, selected_round):
                                    success_messages.append(f"Set {player_name} for {draft_engine.teams[team_id].owner_name} (Round {selected_round})")
                                else:
                                    # Debug why it failed
                                    is_drafted = draft_engine.players_df.loc[player_id, 'drafted']
                                    error_messages.append(f"Failed to set {player_name} for {draft_engine.teams[team_id].owner_name} (drafted={is_drafted})")
                            else:
                                error_messages.append(f"Could not find player {player_name}")
                    
                    # Show results
                    if success_messages:
                        for msg in success_messages:
                            st.success(msg)
                    if error_messages:
                        for msg in error_messages:
                            st.error(msg)
                    
                    if success_messages and not error_messages:
                        st.balloons()
                    
                    # Update session state to reflect current keepers
                    for team_id in range(1, draft_engine.num_teams + 1):
                        current_keeper = None
                        current_round = 1
                        for keeper in draft_engine.teams[team_id].keepers:
                            current_keeper = keeper.player_name
                            current_round = keeper.round
                            break
                        st.session_state.pending_keeper_selections[team_id] = {
                            'player': current_keeper if current_keeper else 'None',
                            'round': current_round
                        }
                    
                    st.rerun()
            
            with col3:
                if st.button("🔄 Reset Changes", type="secondary", use_container_width=True,
                            help="Reset all pending changes to current keeper settings"):
                    # Reset pending selections to current keepers
                    for team_id in range(1, draft_engine.num_teams + 1):
                        current_keeper = None
                        current_round = 1
                        for keeper in draft_engine.teams[team_id].keepers:
                            current_keeper = keeper.player_name
                            current_round = keeper.round
                            break
                        st.session_state.pending_keeper_selections[team_id] = {
                            'player': current_keeper if current_keeper else 'None',
                            'round': current_round
                        }
                    st.info("Reset all pending changes")
                    st.rerun()
        
        # Summary tables
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Current Keepers")
            keeper_data = []
            for team_id, team in draft_engine.teams.items():
                for keeper in team.keepers:
                    keeper_data.append({
                        'Pick': f"#{team_id}",
                        'Owner': team.owner_name,
                        'Player': keeper.player_name,
                        'Pos': keeper.position,
                        'Round': keeper.round
                    })
            
            if keeper_data:
                keeper_df = pd.DataFrame(keeper_data)
                st.dataframe(
                    keeper_df.sort_values(['Round', 'Pick']),
                    use_container_width=True,
                    hide_index=True,
                    height=300
                )
            else:
                st.info("No keepers have been set yet.")
        
        with col2:
            st.write("### Pending Changes")
            pending_data = []
            for team_id in range(1, draft_engine.num_teams + 1):
                player_name = st.session_state.pending_keeper_selections[team_id]['player']
                selected_round = st.session_state.pending_keeper_selections[team_id]['round']
                
                # Check current keeper
                current_keeper_name = None
                current_keeper_round = None
                for keeper in draft_engine.teams[team_id].keepers:
                    current_keeper_name = keeper.player_name
                    current_keeper_round = keeper.round
                    break
                
                # Only show if there's a change
                if player_name != 'None':
                    if current_keeper_name != player_name or current_keeper_round != selected_round:
                        # Find position for new player
                        player_row = available_players[available_players['player_name'] == player_name]
                        position = player_row['base_position'].iloc[0] if not player_row.empty else 'N/A'
                        
                        pending_data.append({
                            'Pick': f"#{team_id}",
                            'Owner': draft_engine.teams[team_id].owner_name,
                            'Player': player_name,
                            'Pos': position,
                            'Round': selected_round,
                            'Change': '🔄 Update' if current_keeper_name else '➕ Add'
                        })
                elif current_keeper_name is not None:
                    # Removing a keeper
                    pending_data.append({
                        'Pick': f"#{team_id}",
                        'Owner': draft_engine.teams[team_id].owner_name,
                        'Player': current_keeper_name,
                        'Pos': '-',
                        'Round': '-',
                        'Change': '❌ Remove'
                    })
            
            if pending_data:
                pending_df = pd.DataFrame(pending_data)
                st.dataframe(
                    pending_df,
                    use_container_width=True,
                    hide_index=True,
                    height=300
                )
            else:
                st.info("No pending changes.")
    
    def render_draft_analysis(self, draft_engine):
        """Render draft analysis and statistics"""
        
        st.subheader("📈 Draft Analysis")
        
        tab1, tab2, tab3 = st.tabs(["Position Distribution", "Team Grades", "Draft Trends"])
        
        with tab1:
            # Position distribution chart
            if draft_engine.draft_history:
                positions_drafted = [pick.position for pick in draft_engine.draft_history]
                position_counts = pd.Series(positions_drafted).value_counts()
                
                fig = px.bar(
                    x=position_counts.index,
                    y=position_counts.values,
                    labels={'x': 'Position', 'y': 'Count'},
                    title="Positions Drafted",
                    color=position_counts.index,
                    color_discrete_map=self.position_colors
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No picks made yet")
        
        with tab2:
            # Team grades
            st.write("**Team Draft Grades:**")
            
            team_grades = []
            for team_id, team in draft_engine.teams.items():
                if team.roster:
                    # Calculate grade based on average rank of picks
                    picks_ranks = []
                    for pick in team.roster:
                        if not pick.is_keeper:
                            player_data = draft_engine.players_df[
                                draft_engine.players_df['player_name'] == pick.player_name
                            ]
                            if not player_data.empty:
                                picks_ranks.append(player_data.iloc[0]['rank'])
                    
                    if picks_ranks:
                        avg_rank = sum(picks_ranks) / len(picks_ranks)
                        expected_rank = (team_id + draft_engine.num_teams) / 2 * len(picks_ranks)
                        
                        # Grade based on how much better than expected
                        grade_score = (expected_rank - avg_rank) / expected_rank * 100 + 80
                        
                        if grade_score >= 95:
                            grade = "A+"
                        elif grade_score >= 90:
                            grade = "A"
                        elif grade_score >= 85:
                            grade = "B+"
                        elif grade_score >= 80:
                            grade = "B"
                        elif grade_score >= 75:
                            grade = "C+"
                        elif grade_score >= 70:
                            grade = "C"
                        else:
                            grade = "D"
                        
                        team_grades.append({
                            'Team': f"Team {team_id}",
                            'Grade': grade,
                            'Avg Pick Value': round(avg_rank, 1)
                        })
            
            if team_grades:
                grades_df = pd.DataFrame(team_grades)
                st.dataframe(grades_df, use_container_width=True, hide_index=True)
            else:
                st.info("Draft some players to see grades")
        
        with tab3:
            # Draft trends
            st.write("**Draft Trends:**")
            
            if len(draft_engine.draft_history) > 0:
                # Runs on positions
                last_5_positions = [pick.position for pick in draft_engine.draft_history[-5:]]
                position_run = max(set(last_5_positions), key=last_5_positions.count)
                
                if last_5_positions.count(position_run) >= 3:
                    st.warning(f"🔥 Run on {position_run}! ({last_5_positions.count(position_run)} of last 5 picks)")
                
                # Value picks (fell past ADP)
                value_picks = []
                for pick in draft_engine.draft_history[-10:]:
                    player_data = draft_engine.players_df[
                        draft_engine.players_df['player_name'] == pick.player_name
                    ]
                    if not player_data.empty:
                        player = player_data.iloc[0]
                        if 'adp' in player and player['adp'] < player['rank'] - 5:
                            value_picks.append(f"{player['player_name']} (ADP: {player['adp']}, Pick: {pick.pick_number})")
                
                if value_picks:
                    st.success(f"💎 Recent value picks: {', '.join(value_picks[:3])}")
                
                # Positional scarcity alerts
                for position in ['RB', 'WR', 'TE']:
                    available = draft_engine.players_df[
                        (draft_engine.players_df['base_position'] == position) &
                        (~draft_engine.players_df['drafted']) &
                        (draft_engine.players_df['rank'] <= 100)
                    ]
                    
                    if len(available) <= 5:
                        st.warning(f"⚠️ Only {len(available)} quality {position}s remaining!")
            else:
                st.info("Draft will begin soon...")