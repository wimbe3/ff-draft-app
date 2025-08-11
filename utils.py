"""
Utility functions module for Fantasy Football Mock Draft Simulator
Contains helper functions, caching decorators, and optimized operations
"""

import streamlit as st
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Any, Tuple
from functools import lru_cache
from config import setup_logging

# Setup logging
logger = setup_logging()


@st.cache_data(ttl=3600)
def process_player_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cached function to process player data
    TTL set to 1 hour since player data doesn't change frequently
    """
    logger.debug(f"Processing {len(df)} player records")
    return df.copy()


@st.cache_data
def calculate_position_tiers(df: pd.DataFrame, position: str, tier_size: int = 6) -> pd.DataFrame:
    """
    Calculate tier breaks for a specific position using clustering
    """
    position_df = df[df['base_position'] == position].copy()
    
    if len(position_df) == 0:
        return position_df
    
    if 'projected_points' in position_df.columns:
        # Use projected points for tier calculation
        position_df['tier'] = pd.qcut(
            position_df['projected_points'], 
            q=min(tier_size, len(position_df)), 
            labels=False,
            duplicates='drop'
        )
    else:
        # Fall back to rank-based tiers
        position_df['tier'] = (position_df['rank'] - 1) // tier_size
    
    return position_df


@lru_cache(maxsize=128)
def get_position_depth(position: str, num_teams: int) -> int:
    """
    Cached calculation of recommended position depth for a league size
    """
    base_depth = {
        'QB': 1.5,
        'RB': 2.5,
        'WR': 2.5,
        'TE': 1.5,
        'K': 1.0,
        'DST': 1.0
    }
    
    depth = base_depth.get(position, 1.0) * num_teams
    return int(np.ceil(depth))


def optimize_dataframe_operations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize DataFrame for better performance
    """
    # Convert object columns to category where appropriate
    categorical_cols = ['base_position', 'team', 'position']
    for col in categorical_cols:
        if col in df.columns and df[col].dtype == 'object':
            df[col] = df[col].astype('category')
    
    # Ensure numeric columns are proper dtype
    numeric_cols = ['rank', 'adp', 'bye', 'tier']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


@st.cache_data
def calculate_team_grades(team_roster: List[Dict], league_size: int) -> Dict[str, Any]:
    """
    Calculate grades for a team's draft performance
    """
    if not team_roster:
        return {'overall': 'N/A', 'positions': {}}
    
    # Calculate average draft position vs actual pick
    total_value = 0
    position_values = {}
    
    for pick in team_roster:
        if 'adp' in pick and 'draft_position' in pick:
            value = pick['adp'] - pick['draft_position']
            total_value += value
            
            pos = pick.get('position', 'Unknown')
            if pos not in position_values:
                position_values[pos] = []
            position_values[pos].append(value)
    
    # Calculate overall grade
    avg_value = total_value / len(team_roster) if team_roster else 0
    
    # Convert to letter grade
    if avg_value >= 10:
        overall_grade = 'A+'
    elif avg_value >= 5:
        overall_grade = 'A'
    elif avg_value >= 2:
        overall_grade = 'B'
    elif avg_value >= -2:
        overall_grade = 'C'
    elif avg_value >= -5:
        overall_grade = 'D'
    else:
        overall_grade = 'F'
    
    # Calculate position grades
    position_grades = {}
    for pos, values in position_values.items():
        avg_pos_value = sum(values) / len(values)
        if avg_pos_value >= 5:
            position_grades[pos] = 'A'
        elif avg_pos_value >= 0:
            position_grades[pos] = 'B'
        elif avg_pos_value >= -5:
            position_grades[pos] = 'C'
        else:
            position_grades[pos] = 'D'
    
    return {
        'overall': overall_grade,
        'positions': position_grades,
        'total_value': total_value,
        'avg_value': avg_value
    }


def validate_csv_structure(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate CSV file structure and return issues if any
    """
    issues = []
    
    # Check for minimum required columns
    required_cols = ['player_name', 'position']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        issues.append(f"Missing required columns: {', '.join(missing_cols)}")
    
    # Check for empty dataframe
    if df.empty:
        issues.append("CSV file contains no data")
    
    # Check for duplicate player names
    if 'player_name' in df.columns:
        duplicates = df[df.duplicated(subset=['player_name'], keep=False)]
        if not duplicates.empty:
            issues.append(f"Found {len(duplicates)} duplicate player entries")
    
    # Check for valid positions
    if 'position' in df.columns:
        valid_positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DST', 'DEF', 'D/ST']
        invalid_positions = df[~df['position'].str.upper().isin(valid_positions)]
        if not invalid_positions.empty:
            unique_invalid = invalid_positions['position'].unique()[:5]
            issues.append(f"Invalid positions found: {', '.join(map(str, unique_invalid))}")
    
    return len(issues) == 0, issues


def get_draft_summary_stats(draft_engine: Any) -> Dict[str, Any]:
    """
    Get summary statistics for the current draft
    """
    stats = {
        'total_picks': draft_engine.current_pick - 1,
        'rounds_complete': (draft_engine.current_pick - 1) // draft_engine.num_teams,
        'picks_remaining': (draft_engine.total_rounds * draft_engine.num_teams) - (draft_engine.current_pick - 1),
        'positions_drafted': {},
        'teams_summary': {}
    }
    
    # Count positions drafted
    for team_id, team in draft_engine.teams.items():
        team_positions = {}
        for pick in team.roster:
            pos = pick.position
            if pos not in team_positions:
                team_positions[pos] = 0
            team_positions[pos] += 1
            
            if pos not in stats['positions_drafted']:
                stats['positions_drafted'][pos] = 0
            stats['positions_drafted'][pos] += 1
        
        stats['teams_summary'][team_id] = {
            'picks': len(team.roster),
            'positions': team_positions
        }
    
    return stats


@st.cache_data
def generate_mock_rankings(num_players: int = 300) -> pd.DataFrame:
    """
    Generate mock player rankings for testing
    """
    positions = ['QB'] * 40 + ['RB'] * 80 + ['WR'] * 100 + ['TE'] * 40 + ['K'] * 20 + ['DST'] * 20
    
    players = []
    for i, pos in enumerate(positions[:num_players]):
        players.append({
            'rank': i + 1,
            'player_name': f"Player {i+1}",
            'position': pos,
            'team': np.random.choice(['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE']),
            'bye': np.random.randint(4, 15),
            'adp': i + 1 + np.random.randint(-5, 6),
            'projected_points': 300 - (i * 0.8) + np.random.randn() * 10
        })
    
    return pd.DataFrame(players)


def format_player_display(player: pd.Series, include_team: bool = True) -> str:
    """
    Format player information for display
    """
    name = player.get('player_name', 'Unknown')
    position = player.get('base_position', player.get('position', 'Unknown'))
    
    if include_team:
        team = player.get('team', 'FA')
        return f"{name} ({position} - {team})"
    else:
        return f"{name} ({position})"


def calculate_pick_value(pick_number: int, total_teams: int) -> float:
    """
    Calculate the theoretical value of a draft pick
    Uses a logarithmic decay model
    """
    # Earlier picks have higher value
    base_value = 100
    decay_rate = 0.95
    
    value = base_value * (decay_rate ** (pick_number - 1))
    return round(value, 2)


def get_next_picks_for_team(team_id: int, current_pick: int, 
                            num_teams: int, total_rounds: int) -> List[int]:
    """
    Calculate the next 3 picks for a specific team
    """
    next_picks = []
    pick = current_pick
    
    while len(next_picks) < 3 and pick <= (num_teams * total_rounds):
        round_num = ((pick - 1) // num_teams) + 1
        
        if round_num % 2 == 1:  # Odd round
            team_picking = ((pick - 1) % num_teams) + 1
        else:  # Even round (snake)
            team_picking = num_teams - ((pick - 1) % num_teams)
        
        if team_picking == team_id:
            next_picks.append(pick)
        
        pick += 1
    
    return next_picks