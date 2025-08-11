"""
Draft logic module for Fantasy Football Mock Draft Simulator
Implements autopick algorithm, draft mechanics, and keeper system
"""

import pandas as pd
import numpy as np
import streamlit as st
import logging
from typing import Dict, List, Optional, Tuple, Any
import random
from dataclasses import dataclass, field
from config import (
    DraftConfig, VOR_BASELINE_RANKS, POSITION_SCARCITY_WEIGHTS,
    AUTOPICK_WEIGHTS, ERROR_MESSAGES, setup_logging
)

# Setup logging
logger = setup_logging()

@dataclass
class DraftPick:
    """Represents a single draft pick"""
    pick_number: int
    round: int
    team: int
    player_id: int
    player_name: str
    position: str
    team_abbr: str = ""  # NFL team abbreviation
    is_keeper: bool = False
    
@dataclass
class Team:
    """Represents a fantasy team"""
    team_id: int
    team_name: str
    owner_name: str
    draft_position: int
    roster: List[DraftPick] = field(default_factory=list)
    keepers: List[DraftPick] = field(default_factory=list)
    
    def get_roster_by_position(self) -> Dict[str, List[DraftPick]]:
        """Get roster organized by position"""
        roster_dict = {}
        for pick in self.roster:
            if pick.position not in roster_dict:
                roster_dict[pick.position] = []
            roster_dict[pick.position].append(pick)
        return roster_dict

class DraftEngine:
    """Main draft engine handling all draft logic"""
    
    def __init__(self, players_df: pd.DataFrame, num_teams: int, 
                 draft_position: int, roster_config: Dict):
        self.players_df = players_df.copy()
        self.num_teams = num_teams
        self.user_position = draft_position
        self.roster_config = roster_config
        self.total_rounds = sum(roster_config.values())
        
        # Initialize teams
        self.teams = self._initialize_teams()
        
        # Draft state
        self.current_pick = 1
        self.draft_complete = False
        self.draft_history = []
        
        # Keeper settings
        self.keepers = {}  # {team_id: [(player_id, round)]}
        
        # Initialize session state for draft
        if 'draft_board' not in st.session_state:
            st.session_state.draft_board = self._initialize_draft_board()
        
        # Always restore keepers from session state if they exist
        # This ensures keepers are on the board even if DraftEngine is recreated
        if 'keeper_data' in st.session_state:
            # Clear any existing keepers from board first
            for round_num in st.session_state.draft_board:
                for pos in list(st.session_state.draft_board[round_num].keys()):
                    pick = st.session_state.draft_board[round_num][pos]
                    if pick and getattr(pick, 'is_keeper', False):
                        del st.session_state.draft_board[round_num][pos]
            # Now restore keepers
            self._restore_keepers_from_session()
    
    def _initialize_teams(self) -> Dict[int, Team]:
        """Initialize all teams in the draft"""
        teams = {}
        
        # Get owner names from session state if available
        owner_names = st.session_state.get('team_owners', {})
        
        logger.info(f"Initializing teams: user_position={self.user_position}")
        
        for i in range(1, self.num_teams + 1):
            # Use stored owner name or default
            if i in owner_names:
                owner_name = owner_names[i]
            elif i == self.user_position:
                owner_name = "You"
            else:
                owner_name = f"Owner {i}"
            
            teams[i] = Team(
                team_id=i,
                team_name=f"Team {i}" if i != self.user_position else "Your Team",
                owner_name=owner_name,
                draft_position=i
            )
        
        logger.info(f"Team {self.user_position} owner: {teams[self.user_position].owner_name}")
        return teams
    
    def reset_draft(self):
        """Reset the draft while keeping league settings and keepers"""
        # Reset draft state
        self.current_pick = 1
        self.draft_complete = False
        self.draft_history = []
        
        # Reset player data
        self.players_df['drafted'] = False
        self.players_df['drafted_by'] = None
        self.players_df['draft_round'] = None
        
        # Clear team rosters (but not keepers)
        for team in self.teams.values():
            team.roster = []
        
        # Clear session state draft board
        if 'draft_board' in st.session_state:
            st.session_state.draft_board = {}
        
        logger.info("Draft reset - keeping settings and keepers")
    
    def update_team_owner(self, team_id: int, owner_name: str):
        """Update the owner name for a team"""
        if team_id in self.teams:
            self.teams[team_id].owner_name = owner_name
            
            # Store in session state
            if 'team_owners' not in st.session_state:
                st.session_state.team_owners = {}
            st.session_state.team_owners[team_id] = owner_name
    
    def _initialize_draft_board(self) -> Dict:
        """Initialize the draft board structure"""
        board = {}
        for round_num in range(1, self.total_rounds + 1):
            board[round_num] = {}
            if round_num % 2 == 1:  # Odd rounds go 1->12
                for pick in range(1, self.num_teams + 1):
                    board[round_num][pick] = None
            else:  # Even rounds go 12->1 (snake)
                for pick in range(self.num_teams, 0, -1):
                    board[round_num][self.num_teams - pick + 1] = None
        return board
    
    def get_team_on_clock(self, pick_number: int) -> int:
        """Get which team is currently on the clock"""
        round_num = ((pick_number - 1) // self.num_teams) + 1
        
        if round_num % 2 == 1:  # Odd round
            team = ((pick_number - 1) % self.num_teams) + 1
        else:  # Even round (snake)
            team = self.num_teams - ((pick_number - 1) % self.num_teams)
        
        return team
    
    def make_pick(self, player_id: int, team_id: Optional[int] = None) -> bool:
        """Make a draft pick"""
        
        if self.draft_complete:
            return False
        
        # Get current team if not specified
        if team_id is None:
            team_id = self.get_team_on_clock(self.current_pick)
        
        # Verify player is available
        player_row = self.players_df[self.players_df.index == player_id]
        if player_row.empty or player_row.iloc[0]['drafted']:
            return False
        
        # Make the pick
        player = player_row.iloc[0]
        round_num = ((self.current_pick - 1) // self.num_teams) + 1
        
        # Update player as drafted
        self.players_df.loc[player_id, 'drafted'] = True
        self.players_df.loc[player_id, 'drafted_by'] = team_id
        self.players_df.loc[player_id, 'draft_position'] = self.current_pick
        self.players_df.loc[player_id, 'draft_round'] = round_num
        
        # Create draft pick object
        draft_pick = DraftPick(
            pick_number=self.current_pick,
            round=round_num,
            team=team_id,
            player_id=player_id,
            player_name=player['player_name'],
            position=player['base_position'],
            team_abbr=player.get('team', '')  # Get NFL team abbreviation
        )
        
        # Add to team roster
        self.teams[team_id].roster.append(draft_pick)
        
        # Add to draft history
        self.draft_history.append(draft_pick)
        
        # Update draft board in session state
        # Position in draft board is the team_id (column position), not pick order
        if round_num not in st.session_state.draft_board:
            st.session_state.draft_board[round_num] = {}
        st.session_state.draft_board[round_num][team_id] = draft_pick
        
        # Advance to next pick
        self.current_pick += 1
        
        # Check if draft is complete
        if self.current_pick > (self.num_teams * self.total_rounds):
            self.draft_complete = True
        
        return True
    
    def autopick(self, team_id: int) -> Optional[int]:
        """
        Simplified autopick that closely follows uploaded rankings with slight randomization
        Ensures each team drafts one K and one DST (typically in last rounds)
        Returns the player_id of the selected player
        """
        
        team = self.teams[team_id]
        available_players = self.players_df[~self.players_df['drafted']].copy()
        
        if available_players.empty:
            logger.warning(f"No available players for team {team_id}")
            return None
        
        # Sort by rank (following the uploaded rankings)
        available_players = available_players.sort_values('rank')
        logger.info(f"Team {team_id} autopick: {len(available_players)} players available, pick #{self.current_pick}")
        
        current_round = ((self.current_pick - 1) // self.num_teams) + 1
        roster_by_position = team.get_roster_by_position()
        
        # Check if we need K or DST
        has_k = len(roster_by_position.get('K', [])) > 0
        has_dst = len(roster_by_position.get('DST', [])) > 0
        
        # Count remaining picks for this team
        picks_remaining = 0
        for future_pick in range(self.current_pick, (self.num_teams * self.total_rounds) + 1):
            if self.get_team_on_clock(future_pick) == team_id:
                picks_remaining += 1
        
        # Force K/DST selection if running out of picks and still need them
        force_k = not has_k and picks_remaining <= 2  # Need to get K in last 2 picks
        force_dst = not has_dst and picks_remaining <= 2  # Need to get DST in last 2 picks
        
        # If we must draft K or DST, filter for those positions
        if force_k or force_dst:
            needed_positions = []
            if force_k:
                needed_positions.append('K')
            if force_dst:
                needed_positions.append('DST')
            
            # Get best available K or DST
            position_players = available_players[available_players['base_position'].isin(needed_positions)]
            if not position_players.empty:
                # Take the best ranked one - return its index
                return position_players.index[0]
        
        # Filter out players that would violate roster constraints
        valid_players = []
        valid_indices = []  # Store the corresponding indices
        checked_count = 0
        max_to_check = min(50, len(available_players))  # Check up to 50 players
        
        for idx, player in available_players.iterrows():
            checked_count += 1
            position = player['base_position']
            
            # Handle K and DST drafting strategy
            if position in ['K', 'DST']:
                # Already have one? Skip
                if (position == 'K' and has_k) or (position == 'DST' and has_dst):
                    if checked_count < max_to_check:
                        continue
                # Don't draft K/DST too early (before round 13) unless we're running out of picks
                if current_round < 13 and picks_remaining > 3:
                    if checked_count < max_to_check:
                        continue
            
            # Don't draft backup QB/TE too early
            if position in ['QB', 'TE']:
                if len(roster_by_position.get(position, [])) >= 1 and current_round < 10:
                    if checked_count < max_to_check:
                        continue  # Skip backup QB/TE before round 10
            
            # Add to valid players list
            valid_players.append(player)
            valid_indices.append(idx)  # Store the index
            
            # Stop after finding enough valid options (for performance)
            if len(valid_players) >= 10:
                break
            
            # Also stop if we've checked enough players
            if checked_count >= max_to_check:
                break
        
        if not valid_players:
            # If no valid players found, just take the best available non-K/DST
            for idx, player in available_players.head(20).iterrows():
                if player['base_position'] not in ['K', 'DST']:
                    valid_players.append(player)
                    valid_indices.append(idx)
                    break
            
            # If still no valid players (very unlikely), take absolute best available
            if not valid_players:
                # Just take the top available player
                first_idx = available_players.index[0]
                valid_players = [available_players.iloc[0]]
                valid_indices = [first_idx]
                logger.debug(f"Team {team_id}: Using fallback - best available player")
        
        # Ensure we have valid players to choose from
        if not valid_indices:
            logger.error(f"Team {team_id}: No valid indices found, returning first available")
            if not available_players.empty:
                first_player_idx = available_players.index[0]
                logger.info(f"Returning player at index {first_player_idx}: {available_players.iloc[0]['player_name']}")
                return first_player_idx
            else:
                logger.error(f"No available players at all!")
                return None
        
        logger.info(f"Team {team_id}: Found {len(valid_indices)} valid players to choose from")
        
        # Add randomization to keep drafts varied
        # Early rounds: stick closer to rankings
        # Later rounds: more variation
        if current_round <= 3:
            # Rounds 1-3: Pick from top 3 available with weighted randomness
            num_choices = min(3, len(valid_indices))
            weights = [0.7, 0.2, 0.1][:num_choices]
        elif current_round <= 6:
            # Rounds 4-6: Pick from top 5 available
            num_choices = min(5, len(valid_indices))
            weights = [0.5, 0.25, 0.15, 0.07, 0.03][:num_choices]
        elif current_round <= 10:
            # Rounds 7-10: Pick from top 7 available
            num_choices = min(7, len(valid_indices))
            weights = [0.4, 0.2, 0.15, 0.1, 0.08, 0.05, 0.02][:num_choices]
        else:
            # Rounds 11+: More variation, pick from top 10
            num_choices = min(10, len(valid_indices))
            # Create descending weights
            weights = [0.3 * (0.8 ** i) for i in range(num_choices)]
            # Normalize weights to sum to 1
            weight_sum = sum(weights)
            if weight_sum > 0:
                weights = [w / weight_sum for w in weights]
            else:
                weights = [1.0]  # Fallback to equal weight
        
        # Make the selection with weighted randomness
        selected_idx = random.choices(range(num_choices), weights=weights)[0]
        
        # Return the stored index for the selected player
        player_idx = valid_indices[selected_idx]
        # Verify the player exists and isn't drafted
        if player_idx in self.players_df.index:
            selected_player = self.players_df.loc[player_idx]
            if not selected_player['drafted']:
                logger.info(f"Team {team_id} selected: {selected_player['player_name']} (index {player_idx})")
                return player_idx
            else:
                logger.warning(f"Team {team_id}: Selected player already drafted, trying fallback")
        
        # Fallback - just return the first available
        for idx in available_players.index:
            if not self.players_df.loc[idx, 'drafted']:
                logger.info(f"Team {team_id} fallback selected: {self.players_df.loc[idx, 'player_name']} (index {idx})")
                return idx
        
        logger.error(f"Team {team_id}: No valid players found!")
        return None
    
    def _calculate_team_needs(self, team: Team) -> Dict[str, float]:
        """Calculate positional needs for a team"""
        
        needs = {}
        roster_by_position = team.get_roster_by_position()
        
        # Calculate needs for each position
        for position, required in self.roster_config.items():
            if position == 'BENCH':
                continue
            
            current_count = len(roster_by_position.get(position, []))
            
            if position == 'FLEX':
                # FLEX can be filled by RB, WR, or TE
                flex_eligible = (
                    len(roster_by_position.get('RB', [])) - self.roster_config.get('RB', 0) +
                    len(roster_by_position.get('WR', [])) - self.roster_config.get('WR', 0) +
                    len(roster_by_position.get('TE', [])) - self.roster_config.get('TE', 0)
                )
                current_count = max(0, flex_eligible)
            
            # Calculate need score (1.0 = urgent need, 0.0 = no need)
            if current_count >= required:
                needs[position] = 0.0
            else:
                remaining = required - current_count
                urgency = remaining / max(1, required)
                
                # Adjust urgency based on rounds remaining
                rounds_left = self.total_rounds - ((self.current_pick - 1) // self.num_teams)
                urgency_multiplier = min(2.0, (required - current_count) / max(1, rounds_left))
                
                needs[position] = min(1.0, urgency * urgency_multiplier)
        
        return needs
    
    def _calculate_autopick_score(self, player: pd.Series, team_needs: Dict, team: Team) -> float:
        """
        Calculate autopick score for a player based on multiple factors
        Higher score = better pick
        """
        
        score = 0.0
        position = player['base_position']
        current_round = ((self.current_pick - 1) // self.num_teams) + 1
        
        # Adjust weights based on round - early rounds favor BPA (best player available)
        if current_round <= 3:
            # Early rounds: heavily favor ranking
            rank_weight = 70
            need_weight = 15
            scarcity_weight = 10
            other_weight = 5
        elif current_round <= 6:
            # Mid rounds: balance ranking and need
            rank_weight = 50
            need_weight = 25
            scarcity_weight = 15
            other_weight = 10
        else:
            # Late rounds: focus more on team needs
            rank_weight = 35
            need_weight = 35
            scarcity_weight = 20
            other_weight = 10
        
        # 1. Base value from ranking (primary factor)
        # Inverse of rank, normalized
        rank_score = (300 - player['rank']) / 300  # Assumes ~300 total players
        score += rank_score * rank_weight
        
        # 2. Positional need
        position_need = team_needs.get(position, 0.0)
        
        # Check if position can fill FLEX
        if position in ['RB', 'WR', 'TE'] and position_need == 0:
            position_need = max(position_need, team_needs.get('FLEX', 0.0) * 0.7)
        
        score += position_need * need_weight
        
        # 3. Positional scarcity
        scarcity_score = self._calculate_position_scarcity(position)
        score += scarcity_score * scarcity_weight
        
        # 4. Other factors (tier, ADP, etc.)
        if 'tier' in player.index:
            tier_score = self._calculate_tier_score(player, position)
            score += tier_score * (other_weight * 0.6)
        
        if 'adp' in player.index and not pd.isna(player['adp']):
            # Bonus for players falling past ADP
            adp_diff = player['adp'] - player['rank']
            adp_score = max(0, min(1, adp_diff / 10))  # Cap at 10 spots fallen
            score += adp_score * (other_weight * 0.4)
        
        # Position-specific adjustments
        score = self._apply_position_adjustments(score, player, team)
        
        # Strong penalty for reaching too far in early rounds
        if current_round <= 3 and player['rank'] > self.current_pick + 10:
            reach_penalty = (player['rank'] - self.current_pick - 10) / 20
            score *= (1 - min(0.7, reach_penalty))
        elif player['rank'] > self.current_pick + 20:  # General reach penalty
            reach_penalty = (player['rank'] - self.current_pick - 20) / 40
            score *= (1 - min(0.5, reach_penalty))
        
        return score
    
    def _calculate_position_scarcity(self, position: str) -> float:
        """Calculate scarcity score for a position"""
        
        available = self.players_df[
            (self.players_df['base_position'] == position) & 
            (~self.players_df['drafted'])
        ]
        
        total_at_position = self.players_df[
            self.players_df['base_position'] == position
        ]
        
        if len(total_at_position) == 0:
            return 0.0
        
        # Calculate starter-quality players remaining
        starter_threshold = {
            'QB': 12, 'RB': 24, 'WR': 30, 'TE': 12, 'K': 12, 'DST': 12
        }.get(position, 12)
        
        quality_remaining = len(available[available['rank'] <= starter_threshold * 2])
        picks_until_next = self.num_teams * 2  # Approximate picks until next turn
        
        scarcity = 1 - (quality_remaining / max(1, picks_until_next))
        
        return max(0, min(1, scarcity))
    
    def _calculate_tier_score(self, player: pd.Series, position: str) -> float:
        """Calculate tier-based score adjustments"""
        
        current_tier = player['tier']
        
        # Find next available player at same position
        next_available = self.players_df[
            (self.players_df['base_position'] == position) &
            (~self.players_df['drafted']) &
            (self.players_df['rank'] > player['rank'])
        ]
        
        if next_available.empty:
            return 1.0  # Last player at position
        
        next_tier = next_available.iloc[0]['tier']
        
        # Bonus for last player in tier
        if next_tier > current_tier:
            tier_drop = next_tier - current_tier
            return min(1.0, 0.5 + (tier_drop * 0.25))
        
        return 0.3  # Normal tier score
    
    def _apply_position_adjustments(self, score: float, player: pd.Series, team: Team) -> float:
        """Apply position-specific scoring adjustments"""
        
        position = player['base_position']
        roster = team.get_roster_by_position()
        current_round = ((self.current_pick - 1) // self.num_teams) + 1
        
        # First 2 rounds: strongly discourage QB/TE unless elite (top 3 ranked at position)
        if current_round <= 2:
            if position in ['QB', 'TE']:
                # Count how many of this position have been drafted
                position_rank_among_position = 1
                for _, p in self.players_df[self.players_df['base_position'] == position].iterrows():
                    if p['drafted'] and p['rank'] < player['rank']:
                        position_rank_among_position += 1
                
                if position_rank_among_position > 3:  # Not elite at position
                    score *= 0.3  # Heavy penalty
            elif position in ['K', 'DST']:
                score *= 0.1  # Never draft K/DST in first 2 rounds
        
        # Don't draft backup QB/TE/K/DST too early
        if position in ['QB', 'TE', 'K', 'DST']:
            if len(roster.get(position, [])) >= 1:
                if current_round < 10:  # First 10 rounds
                    score *= 0.2  # Heavy penalty for early backup
                elif current_round < 14:
                    score *= 0.5
        
        # RB/WR depth is valuable
        if position in ['RB', 'WR']:
            current_count = len(roster.get(position, []))
            if current_count >= self.roster_config.get(position, 2):
                # Still valuable for FLEX and depth
                score *= 0.85
        
        # Zero-RB or Zero-WR strategy detection
        if current_round >= 3:
            if position == 'RB' and len(roster.get('RB', [])) == 0:
                score *= 1.3  # Boost RB if implementing Zero-RB
            elif position == 'WR' and len(roster.get('WR', [])) == 0:
                score *= 1.3  # Boost WR if implementing Zero-WR
        
        return score
    
    def set_keeper(self, team_id: int, player_id: int, round: int) -> bool:
        """Set a player as a keeper for a specific team and round"""
        
        # Verify player exists and isn't already kept
        player_row = self.players_df[self.players_df.index == player_id]
        if player_row.empty or player_row.iloc[0]['drafted']:
            return False
        
        # Initialize keepers dict for team if needed
        if team_id not in self.keepers:
            self.keepers[team_id] = []
        
        # Check if round is already taken
        for keeper_player_id, keeper_round in self.keepers[team_id]:
            if keeper_round == round:
                return False
        
        # Add keeper
        self.keepers[team_id].append((player_id, round))
        
        # Mark player as drafted
        player = player_row.iloc[0]
        self.players_df.loc[player_id, 'drafted'] = True
        self.players_df.loc[player_id, 'drafted_by'] = team_id
        self.players_df.loc[player_id, 'draft_round'] = round
        
        # Create keeper pick
        keeper_pick = DraftPick(
            pick_number=0,  # Special value for keepers
            round=round,
            team=team_id,
            player_id=player_id,
            player_name=player['player_name'],
            position=player['base_position'],
            team_abbr=player.get('team', ''),  # Get NFL team abbreviation
            is_keeper=True
        )
        
        self.teams[team_id].keepers.append(keeper_pick)
        self.teams[team_id].roster.append(keeper_pick)
        
        # Add keeper to draft board
        if round not in st.session_state.draft_board:
            st.session_state.draft_board[round] = {}
        st.session_state.draft_board[round][team_id] = keeper_pick
        
        # Save to session state
        self._save_keepers_to_session()
        
        return True
    
    def remove_keeper(self, team_id: int, player_id: int) -> bool:
        """Remove a keeper from a team"""
        
        if team_id not in self.keepers:
            return False
        
        # Find and remove keeper
        for i, (keeper_id, keeper_round) in enumerate(self.keepers[team_id]):
            if keeper_id == player_id:
                self.keepers[team_id].pop(i)
                
                # Mark player as undrafted
                self.players_df.loc[player_id, 'drafted'] = False
                self.players_df.loc[player_id, 'drafted_by'] = None
                self.players_df.loc[player_id, 'draft_round'] = None
                
                # Remove from team roster
                team = self.teams[team_id]
                team.keepers = [k for k in team.keepers if k.player_id != player_id]
                team.roster = [p for p in team.roster if p.player_id != player_id]
                
                # Remove from draft board
                if keeper_round in st.session_state.draft_board:
                    if team_id in st.session_state.draft_board[keeper_round]:
                        del st.session_state.draft_board[keeper_round][team_id]
                
                # Save to session state
                self._save_keepers_to_session()
                
                return True
        
        return False
    
    def _save_keepers_to_session(self):
        """Save keeper data to session state"""
        keeper_data = {}
        for team_id, team in self.teams.items():
            if team.keepers:
                keeper_data[team_id] = [
                    {
                        'player_id': k.player_id,
                        'player_name': k.player_name,
                        'position': k.position,
                        'round': k.round
                    }
                    for k in team.keepers
                ]
        st.session_state.keeper_data = keeper_data
    
    def _restore_keepers_from_session(self):
        """Restore keeper data from session state"""
        if 'keeper_data' not in st.session_state:
            return
        
        keeper_data = st.session_state.keeper_data
        for team_id, keepers in keeper_data.items():
            if team_id in self.teams:
                for keeper_info in keepers:
                    # Find player in dataframe
                    player_rows = self.players_df[
                        self.players_df['player_name'] == keeper_info['player_name']
                    ]
                    
                    if not player_rows.empty:
                        player_id = player_rows.index[0]
                        
                        # Mark as drafted
                        self.players_df.loc[player_id, 'drafted'] = True
                        self.players_df.loc[player_id, 'drafted_by'] = team_id
                        self.players_df.loc[player_id, 'draft_round'] = keeper_info['round']
                        
                        # Create keeper pick
                        player = self.players_df.loc[player_id]
                        keeper_pick = DraftPick(
                            pick_number=0,
                            round=keeper_info['round'],
                            team=team_id,
                            player_id=player_id,
                            player_name=keeper_info['player_name'],
                            position=keeper_info['position'],
                            team_abbr=player.get('team', ''),  # Get NFL team abbreviation
                            is_keeper=True
                        )
                        
                        # Add to team
                        self.teams[team_id].keepers.append(keeper_pick)
                        self.teams[team_id].roster.append(keeper_pick)
                        
                        # Add to keepers dict
                        if team_id not in self.keepers:
                            self.keepers[team_id] = []
                        self.keepers[team_id].append((player_id, keeper_info['round']))
                        
                        # Add keeper to draft board
                        round_num = keeper_info['round']
                        # Position in round is just the team_id (column position)
                        position = int(team_id)  # Ensure it's an int
                        
                        if round_num not in st.session_state.draft_board:
                            st.session_state.draft_board[round_num] = {}
                        
                        st.session_state.draft_board[round_num][position] = keeper_pick
    
    def simulate_picks(self, num_picks: int) -> List[DraftPick]:
        """Simulate a number of autopicks"""
        
        simulated = []
        
        for _ in range(num_picks):
            if self.draft_complete:
                break
            
            team_id = self.get_team_on_clock(self.current_pick)
            
            # Skip if user's turn
            if team_id == self.user_position:
                break
            
            # Make autopick
            player_id = self.autopick(team_id)
            if player_id is not None:
                self.make_pick(player_id, team_id)
                simulated.append(self.draft_history[-1])
        
        return simulated
    
    def get_draft_results(self) -> pd.DataFrame:
        """Get draft results as a DataFrame"""
        
        results = []
        for pick in self.draft_history:
            results.append({
                'Pick': pick.pick_number,
                'Round': pick.round,
                'Team': self.teams[pick.team].team_name,
                'Player': pick.player_name,
                'Position': pick.position,
                'Keeper': pick.is_keeper
            })
        
        return pd.DataFrame(results)
    
    def get_team_summary(self, team_id: int) -> Dict:
        """Get summary statistics for a team"""
        
        team = self.teams[team_id]
        roster_by_pos = team.get_roster_by_position()
        
        summary = {
            'team_name': team.team_name,
            'total_picks': len(team.roster),
            'positions': {}
        }
        
        for pos, players in roster_by_pos.items():
            summary['positions'][pos] = {
                'count': len(players),
                'players': [p.player_name for p in players]
            }
        
        return summary