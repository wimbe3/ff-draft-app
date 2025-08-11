"""
Central configuration module for Fantasy Football Mock Draft Simulator
Contains all shared constants, settings, and configuration values
"""

from typing import Dict, Any, Tuple
from dataclasses import dataclass, field
import logging

# ==================== POSITION CONFIGURATION ====================

POSITION_COLORS: Dict[str, str] = {
    'QB': '#FF6B6B',  # Red
    'RB': '#4ECDC4',  # Teal
    'WR': '#45B7D1',  # Blue
    'TE': '#96CEB4',  # Green
    'K': '#FFEAA7',   # Yellow
    'DST': '#DDA0DD'  # Purple
}

POSITION_MAP: Dict[str, str] = {
    'QB': 'QB',
    'RB': 'RB',
    'WR': 'WR',
    'TE': 'TE',
    'K': 'K',
    'DST': 'DST',
    'DEF': 'DST',
    'D/ST': 'DST'
}

POSITION_EMOJI: Dict[str, str] = {
    'QB': '🎯',
    'RB': '🏃',
    'WR': '💨',
    'TE': '🏈',
    'K': '🦵',
    'DST': '🛡️'
}

# ==================== DRAFT CONFIGURATION ====================

@dataclass
class DraftConfig:
    """Draft configuration settings"""
    MIN_TEAMS: int = 8
    MAX_TEAMS: int = 14
    DEFAULT_TEAMS: int = 12
    DEFAULT_DRAFT_POSITION: int = 1
    DEFAULT_PICK_TIMER: int = 90  # seconds
    
    # Autopick algorithm weights by round
    EARLY_ROUND_THRESHOLD: int = 3
    MID_ROUND_THRESHOLD: int = 6
    
    # Autopick randomness
    OPTIMAL_PICK_PROBABILITY: float = 0.85
    TOP_CHOICES_CONSIDERED: int = 3
    CHOICE_WEIGHTS: Tuple[float, ...] = (0.6, 0.3, 0.1)

@dataclass
class RosterConfig:
    """Default roster configuration"""
    DEFAULT_ROSTER: Dict[str, int] = None
    
    def __post_init__(self):
        if self.DEFAULT_ROSTER is None:
            self.DEFAULT_ROSTER = {
                'QB': 1,
                'RB': 2,
                'WR': 2,
                'TE': 1,
                'FLEX': 1,
                'K': 1,
                'DST': 1,
                'BENCH': 6
            }
    
    @property
    def total_roster_size(self) -> int:
        return sum(self.DEFAULT_ROSTER.values())
    
    @property
    def starting_lineup_size(self) -> int:
        return sum(v for k, v in self.DEFAULT_ROSTER.items() if k != 'BENCH')

# ==================== SCORING CONFIGURATION ====================

# Value Over Replacement (VOR) baseline ranks by position
VOR_BASELINE_RANKS: Dict[str, int] = {
    'QB': 12,
    'RB': 24,
    'WR': 30,
    'TE': 12,
    'K': 12,
    'DST': 12
}

# Position scarcity weights for autopick algorithm
POSITION_SCARCITY_WEIGHTS: Dict[str, float] = {
    'RB': 1.2,
    'WR': 1.1,
    'QB': 0.9,
    'TE': 1.0,
    'K': 0.5,
    'DST': 0.6
}

# Autopick scoring weights by draft phase
AUTOPICK_WEIGHTS = {
    'early': {  # Rounds 1-3
        'rank': 70,
        'need': 15,
        'scarcity': 10,
        'other': 5
    },
    'mid': {    # Rounds 4-6
        'rank': 50,
        'need': 25,
        'scarcity': 15,
        'other': 10
    },
    'late': {   # Rounds 7+
        'rank': 35,
        'need': 35,
        'scarcity': 20,
        'other': 10
    }
}

# ==================== DATA PROCESSING CONFIGURATION ====================

# Column mappings for CSV standardization
CSV_COLUMN_MAPPINGS: Dict[str, str] = {
    'RK': 'rank',
    'RANK': 'rank',
    'OVERALL RANK': 'rank',
    'PLAYER NAME': 'player_name',
    'PLAYER': 'player_name',
    'NAME': 'player_name',
    'TEAM': 'team',
    'POS': 'position',
    'POSITION': 'position',
    'BYE': 'bye',
    'BYE WEEK': 'bye',
    'TIERS': 'tier',
    'TIER': 'tier',
    'ECR VS ADP': 'ecr_vs_adp',
    'ADP': 'adp',
    'SOS': 'sos',
    'POINTS': 'projected_points',
    'PROJ PTS': 'projected_points',
    'PROJECTED POINTS': 'projected_points'
}

REQUIRED_CSV_COLUMNS = ['rank', 'player_name', 'position', 'team']

NUMERIC_COLUMNS = ['rank', 'bye', 'tier', 'position_rank', 'adp', 'projected_points']

# ==================== UI CONFIGURATION ====================

# Player name display settings
MAX_PLAYER_NAME_LENGTH: int = 18
PLAYER_NAME_TRUNCATE_SUFFIX: str = "."

# Draft board display settings
BOARD_ROUND_LABEL_WIDTH: float = 0.5
BOARD_TEAM_COLUMN_WIDTH: float = 1.0

# Session state keys that should be persisted
PERSISTENT_SESSION_KEYS = [
    'draft_started',
    'num_teams',
    'draft_position',
    'roster_config',
    'total_rounds',
    'players_df',
    'draft_board',
    'current_pick',
    'draft_history',
    'keepers',
    'pick_timer',
    'enable_keepers',
    'selected_player_rows',
    'team_owners',
    'saved_drafts'
]

# ==================== LOGGING CONFIGURATION ====================

# Logging settings
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_LEVEL = logging.INFO

def setup_logging(level=LOG_LEVEL):
    """Setup application logging configuration"""
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT
    )
    return logging.getLogger(__name__)

# ==================== VALIDATION CONFIGURATION ====================

# Validation rules
VALIDATION_RULES = {
    'num_teams': lambda x: 8 <= x <= 14,
    'draft_position': lambda x, num_teams: 1 <= x <= num_teams,
    'roster_size': lambda x: x > 0 and x <= 30,
    'player_name': lambda x: x and len(x.strip()) > 0,
    'round_number': lambda x, total_rounds: 1 <= x <= total_rounds
}

# ==================== EXPORT CONFIGURATION ====================

# Export file formats
EXPORT_FORMATS = {
    'csv': {
        'extension': '.csv',
        'mime_type': 'text/csv'
    },
    'json': {
        'extension': '.json',
        'mime_type': 'application/json'
    },
    'html': {
        'extension': '.html',
        'mime_type': 'text/html'
    }
}

# ==================== ERROR MESSAGES ====================

ERROR_MESSAGES = {
    'invalid_csv': "Failed to load rankings. Please check your CSV format.",
    'no_player_data': "No player data loaded. Please go back and upload a rankings file.",
    'draft_pick_failed': "Failed to make pick. Player may already be drafted.",
    'save_failed': "Failed to save draft state.",
    'load_failed': "Failed to load draft state.",
    'validation_failed': "Validation failed: {field} has invalid value.",
    'keeper_conflict': "Round {round} already taken by another team"
}

# ==================== SINGLETON INSTANCES ====================

# Create singleton instances
draft_config = DraftConfig()
roster_config = RosterConfig()