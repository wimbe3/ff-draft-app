"""
Session management module for Fantasy Football Mock Draft Simulator
Handles session state persistence and management
"""

import streamlit as st
import json
import pickle
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from config import (
    PERSISTENT_SESSION_KEYS, DraftConfig, RosterConfig,
    ERROR_MESSAGES, VALIDATION_RULES, setup_logging
)

# Setup logging
logger = setup_logging()

class SessionManager:
    """Manages Streamlit session state for the draft simulator"""
    
    def __init__(self):
        self.session_keys = PERSISTENT_SESSION_KEYS
        self.draft_config = DraftConfig()
        self.roster_config = RosterConfig()
        logger.debug("SessionManager initialized")
    
    def initialize_session(self):
        """Initialize all required session state variables"""
        
        # App flow state
        if 'app_stage' not in st.session_state:
            st.session_state.app_stage = 'upload'
        
        # Draft configuration
        if 'draft_started' not in st.session_state:
            st.session_state.draft_started = False
        
        if 'num_teams' not in st.session_state:
            st.session_state.num_teams = self.draft_config.DEFAULT_TEAMS
        
        if 'draft_position' not in st.session_state:
            st.session_state.draft_position = self.draft_config.DEFAULT_DRAFT_POSITION
        
        if 'roster_config' not in st.session_state:
            st.session_state.roster_config = self.roster_config.DEFAULT_ROSTER.copy()
        
        if 'total_rounds' not in st.session_state:
            st.session_state.total_rounds = 15
        
        # Team owners
        if 'team_owners' not in st.session_state:
            st.session_state.team_owners = {}
        
        # Draft state
        if 'current_pick' not in st.session_state:
            st.session_state.current_pick = 1
        
        if 'draft_board' not in st.session_state:
            st.session_state.draft_board = {}
        
        if 'draft_history' not in st.session_state:
            st.session_state.draft_history = []
        
        if 'keepers' not in st.session_state:
            st.session_state.keepers = {}
        
        # UI state
        if 'pick_timer' not in st.session_state:
            st.session_state.pick_timer = self.draft_config.DEFAULT_PICK_TIMER
        
        if 'selected_player_rows' not in st.session_state:
            st.session_state.selected_player_rows = []
        
        # Draft saves
        if 'saved_drafts' not in st.session_state:
            st.session_state.saved_drafts = {}
    
    def reset_draft(self):
        """Reset the draft to initial state"""
        
        # Reset draft state variables
        st.session_state.draft_started = False
        st.session_state.current_pick = 1
        st.session_state.draft_board = {}
        st.session_state.draft_history = []
        st.session_state.keepers = {}
        st.session_state.selected_player_rows = []
        
        # Clear players dataframe
        if 'players_df' in st.session_state:
            del st.session_state.players_df
        
        # Keep configuration settings
        # (num_teams, draft_position, roster_config remain)
    
    def save_draft_state(self, draft_engine):
        """Save current draft state"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        draft_data = {
            'timestamp': timestamp,
            'configuration': {
                'num_teams': st.session_state.num_teams,
                'draft_position': st.session_state.draft_position,
                'roster_config': st.session_state.roster_config,
                'total_rounds': st.session_state.total_rounds
            },
            'state': {
                'current_pick': draft_engine.current_pick,
                'draft_complete': draft_engine.draft_complete,
                'draft_history': [
                    {
                        'pick_number': pick.pick_number,
                        'round': pick.round,
                        'team': pick.team,
                        'player_id': pick.player_id,
                        'player_name': pick.player_name,
                        'position': pick.position,
                        'is_keeper': pick.is_keeper
                    }
                    for pick in draft_engine.draft_history
                ],
                'keepers': draft_engine.keepers,
                'draft_board': st.session_state.draft_board
            },
            'players_drafted': draft_engine.players_df[draft_engine.players_df['drafted']][
                ['player_name', 'drafted_by', 'draft_position', 'draft_round']
            ].to_dict('records')
        }
        
        # Store in session state
        st.session_state.saved_drafts[timestamp] = draft_data
        
        # Also save to file for persistence
        self._save_to_file(draft_data, timestamp)
        
        return timestamp
    
    def load_draft_state(self, timestamp: str) -> bool:
        """Load a saved draft state"""
        
        if timestamp not in st.session_state.saved_drafts:
            # Try loading from file
            draft_data = self._load_from_file(timestamp)
            if not draft_data:
                return False
            st.session_state.saved_drafts[timestamp] = draft_data
        else:
            draft_data = st.session_state.saved_drafts[timestamp]
        
        # Restore configuration
        config = draft_data['configuration']
        st.session_state.num_teams = config['num_teams']
        st.session_state.draft_position = config['draft_position']
        st.session_state.roster_config = config['roster_config']
        st.session_state.total_rounds = config['total_rounds']
        
        # Restore state
        state = draft_data['state']
        st.session_state.current_pick = state['current_pick']
        st.session_state.draft_board = state['draft_board']
        st.session_state.draft_history = state['draft_history']
        st.session_state.keepers = state['keepers']
        
        # Mark draft as started
        st.session_state.draft_started = True
        
        return True
    
    def _save_to_file(self, draft_data: Dict, timestamp: str):
        """Save draft data to a JSON file"""
        
        try:
            filename = f"draft_save_{timestamp}.json"
            
            # Convert non-serializable objects
            save_data = draft_data.copy()
            
            # Handle draft_board which might have complex objects
            if 'draft_board' in save_data.get('state', {}):
                board_data = {}
                for round_num, round_picks in save_data['state']['draft_board'].items():
                    board_data[str(round_num)] = {}
                    for pick_num, pick_data in round_picks.items():
                        if pick_data:
                            board_data[str(round_num)][str(pick_num)] = {
                                'player_name': pick_data.player_name,
                                'position': pick_data.position,
                                'team': pick_data.team
                            }
                        else:
                            board_data[str(round_num)][str(pick_num)] = None
                save_data['state']['draft_board'] = board_data
            
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Failed to save draft: {str(e)}")
            st.error(ERROR_MESSAGES['save_failed'])
            return False
    
    def _load_from_file(self, timestamp: str) -> Optional[Dict]:
        """Load draft data from a JSON file"""
        
        try:
            filename = f"draft_save_{timestamp}.json"
            
            with open(filename, 'r') as f:
                draft_data = json.load(f)
            
            return draft_data
        except Exception:
            return None
    
    def get_saved_drafts(self) -> Dict[str, str]:
        """Get list of saved drafts"""
        
        saved = {}
        for timestamp, data in st.session_state.saved_drafts.items():
            # Create display name
            dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
            display_name = dt.strftime("%B %d, %Y at %I:%M %p")
            
            # Add pick information
            picks = len(data['state']['draft_history'])
            total_picks = data['configuration']['num_teams'] * data['configuration']['total_rounds']
            
            saved[timestamp] = f"{display_name} ({picks}/{total_picks} picks)"
        
        return saved
    
    def export_session_state(self) -> Dict:
        """Export current session state for debugging"""
        
        export_data = {}
        
        for key in self.session_keys:
            if key in st.session_state:
                value = st.session_state[key]
                
                # Handle non-serializable objects
                if key == 'players_df':
                    export_data[key] = f"DataFrame with {len(value)} rows"
                elif key == 'draft_board':
                    export_data[key] = f"Draft board with {len(value)} rounds"
                else:
                    try:
                        # Test if serializable
                        json.dumps(value)
                        export_data[key] = value
                    except:
                        export_data[key] = str(value)
        
        return export_data
    
    def validate_session_state(self) -> Dict[str, bool]:
        """Validate that session state is properly configured"""
        
        validation = {}
        
        # Check required keys exist
        for key in self.session_keys:
            validation[f"{key}_exists"] = key in st.session_state
        
        # Check data integrity
        if 'num_teams' in st.session_state:
            validation['valid_num_teams'] = (
                self.draft_config.MIN_TEAMS <= st.session_state.num_teams <= self.draft_config.MAX_TEAMS
            )
        
        if 'draft_position' in st.session_state and 'num_teams' in st.session_state:
            validation['valid_draft_position'] = (
                1 <= st.session_state.draft_position <= st.session_state.num_teams
            )
        
        if 'roster_config' in st.session_state:
            validation['valid_roster_config'] = (
                isinstance(st.session_state.roster_config, dict) and
                sum(st.session_state.roster_config.values()) > 0
            )
        
        if 'current_pick' in st.session_state and 'total_rounds' in st.session_state:
            max_picks = st.session_state.get('num_teams', 12) * st.session_state.total_rounds
            validation['valid_current_pick'] = (
                1 <= st.session_state.current_pick <= max_picks + 1
            )
        
        return validation