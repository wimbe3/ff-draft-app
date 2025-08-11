"""
Data processing module for Fantasy Football Mock Draft Simulator
Handles CSV loading, data cleaning, and player data management
"""

import pandas as pd
import streamlit as st
import logging
from typing import Optional, Dict, List, Tuple, Any
from config import (
    POSITION_MAP, POSITION_COLORS, CSV_COLUMN_MAPPINGS,
    REQUIRED_CSV_COLUMNS, NUMERIC_COLUMNS, VOR_BASELINE_RANKS,
    POSITION_SCARCITY_WEIGHTS, ERROR_MESSAGES, setup_logging
)

# Setup logging
logger = setup_logging()

class DataProcessor:
    """Handles all data processing operations for the draft simulator"""
    
    def __init__(self):
        self.position_map = POSITION_MAP
        self.position_colors = POSITION_COLORS
        logger.debug("DataProcessor initialized with config values")
    
    @st.cache_data
    def load_csv(self, filepath: str) -> Optional[pd.DataFrame]:
        """Load CSV file from filesystem with caching"""
        try:
            logger.info(f"Loading CSV from {filepath}")
            df = pd.read_csv(filepath)
            return self.process_dataframe(df)
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            st.error(f"File not found: {filepath}")
            return None
        except pd.errors.EmptyDataError:
            logger.error("CSV file is empty")
            st.error("The CSV file appears to be empty")
            return None
        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            st.error(ERROR_MESSAGES['invalid_csv'])
            return None
    
    def load_uploaded_file(self, uploaded_file: Any) -> Optional[pd.DataFrame]:
        """Load CSV from Streamlit uploaded file with validation"""
        try:
            logger.info(f"Loading uploaded file: {uploaded_file.name}")
            df = pd.read_csv(uploaded_file)
            
            # Validate required columns exist
            if not self._validate_dataframe(df):
                return None
                
            return self.process_dataframe(df)
        except pd.errors.EmptyDataError:
            logger.error("Uploaded CSV file is empty")
            st.error("The uploaded CSV file appears to be empty")
            return None
        except Exception as e:
            logger.error(f"Error loading uploaded file: {str(e)}")
            st.error(ERROR_MESSAGES['invalid_csv'])
            return None
    
    def _validate_dataframe(self, df: pd.DataFrame) -> bool:
        """Validate that dataframe has minimum required structure"""
        if df.empty:
            st.error("The uploaded file contains no data")
            return False
        
        if len(df.columns) < 3:
            st.error("The CSV file doesn't have enough columns. Please check the format.")
            return False
            
        return True
    
    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process and clean the dataframe"""
        
        # Standardize column names
        df = self.standardize_columns(df)
        
        # Extract position and rank
        df = self.extract_position_info(df)
        
        # Clean numeric columns
        df = self.clean_numeric_columns(df)
        
        # Add additional calculated fields
        df = self.add_calculated_fields(df)
        
        # Add draft status columns
        df['drafted'] = False
        df['drafted_by'] = None
        df['draft_position'] = None
        df['draft_round'] = None
        
        # Sort by rank
        df = df.sort_values('rank').reset_index(drop=True)
        
        return df
    
    def standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names for consistency"""
        
        # Use column mappings from config
        column_map = CSV_COLUMN_MAPPINGS
        
        # Rename columns
        df.columns = [col.upper() for col in df.columns]
        for old_col, new_col in column_map.items():
            if old_col in df.columns:
                df = df.rename(columns={old_col: new_col})
        
        # Ensure required columns exist
        required_columns = REQUIRED_CSV_COLUMNS
        for col in required_columns:
            if col not in df.columns:
                if col == 'rank':
                    df['rank'] = range(1, len(df) + 1)
                else:
                    df[col] = 'Unknown'
        
        return df
    
    def extract_position_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract position and position rank from position column"""
        
        if 'position' in df.columns:
            # Extract base position and rank (e.g., "WR1" -> "WR", 1)
            df['position_rank'] = df['position'].str.extract(r'(\d+)$')
            df['base_position'] = df['position'].str.replace(r'\d+$', '', regex=True)
            
            # Map to standard positions
            df['base_position'] = df['base_position'].map(
                lambda x: self.position_map.get(x.upper(), x.upper()) if pd.notna(x) else 'Unknown'
            )
            
            # Add position color
            df['position_color'] = df['base_position'].map(self.position_colors)
        
        return df
    
    def clean_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and convert numeric columns"""
        
        numeric_columns = NUMERIC_COLUMNS
        
        for col in numeric_columns:
            if col in df.columns:
                # Handle various formats
                if col == 'ecr_vs_adp' and col in df.columns:
                    # Handle "+5", "-3", "0" format
                    df[col] = df[col].astype(str).str.replace('+', '').str.replace('−', '-')
                
                # Convert to numeric
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Fill missing values
        if 'tier' in df.columns:
            df['tier'] = df['tier'].fillna(df.groupby('base_position')['tier'].transform('max') + 1)
        
        if 'adp' in df.columns:
            df['adp'] = df['adp'].fillna(df['rank'])
        else:
            df['adp'] = df['rank']
        
        # Convert bye to integer (no decimals)
        if 'bye' in df.columns:
            df['bye'] = df['bye'].fillna(0).astype('Int64')  # Use Int64 to handle NaN properly
        
        return df
    
    def add_calculated_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add calculated fields for draft analysis"""
        
        # Calculate value over replacement (VOR) by position
        if 'projected_points' in df.columns:
            for pos in df['base_position'].unique():
                if pos in ['QB', 'RB', 'WR', 'TE']:
                    pos_df = df[df['base_position'] == pos].copy()
                    if len(pos_df) > 0:
                        # Use VOR baseline ranks from config
                        replacement_rank = VOR_BASELINE_RANKS.get(pos, 12)
                        if len(pos_df) >= replacement_rank:
                            replacement_value = pos_df.iloc[replacement_rank - 1]['projected_points']
                            df.loc[df['base_position'] == pos, 'vor'] = \
                                df.loc[df['base_position'] == pos, 'projected_points'] - replacement_value
        
        # Calculate ADP difference
        df['adp_diff'] = df['rank'] - df['adp']
        
        # Add search field for easier filtering
        df['search_field'] = df['player_name'].str.lower() + ' ' + \
                             df['team'].str.lower() + ' ' + \
                             df['base_position'].str.lower()
        
        return df
    
    def get_position_scarcity(self, df: pd.DataFrame, position: str) -> float:
        """Calculate position scarcity score"""
        
        available = df[(df['base_position'] == position) & (~df['drafted'])].shape[0]
        total = df[df['base_position'] == position].shape[0]
        
        if total == 0:
            return 0
        
        scarcity = 1 - (available / total)
        
        # Adjust for position importance
        position_weight = POSITION_SCARCITY_WEIGHTS.get(position, 1.0)
        
        return scarcity * position_weight
    
    def get_tier_break_info(self, df: pd.DataFrame, player_row: pd.Series) -> Dict:
        """Get information about tier breaks for a player"""
        
        if 'tier' not in df.columns:
            return {'is_tier_break': False}
        
        position = player_row['base_position']
        current_tier = player_row['tier']
        
        # Find next available player at same position
        next_players = df[
            (df['base_position'] == position) & 
            (~df['drafted']) & 
            (df['rank'] > player_row['rank'])
        ]
        
        if next_players.empty:
            return {'is_tier_break': True, 'tier_drop': 0}
        
        next_tier = next_players.iloc[0]['tier']
        
        return {
            'is_tier_break': next_tier > current_tier,
            'tier_drop': next_tier - current_tier,
            'next_player': next_players.iloc[0]['player_name']
        }
    
    def calculate_team_needs(self, team_roster: pd.DataFrame, roster_config: Dict) -> Dict:
        """Calculate positional needs for a team"""
        
        needs = {}
        
        for position, required in roster_config.items():
            if position == 'BENCH':
                continue
            
            if position == 'FLEX':
                # FLEX can be RB, WR, or TE
                flex_filled = len(team_roster[
                    team_roster['base_position'].isin(['RB', 'WR', 'TE'])
                ])
                # Account for starters
                rb_starters = roster_config.get('RB', 0)
                wr_starters = roster_config.get('WR', 0)
                te_starters = roster_config.get('TE', 0)
                
                flex_available = max(0, flex_filled - rb_starters - wr_starters - te_starters)
                needs['FLEX'] = max(0, required - flex_available)
            else:
                current = len(team_roster[team_roster['base_position'] == position])
                needs[position] = max(0, required - current)
        
        return needs
    
    def get_best_available(self, df: pd.DataFrame, position: Optional[str] = None) -> pd.DataFrame:
        """Get best available players, optionally filtered by position"""
        
        available = df[~df['drafted']].copy()
        
        if position:
            if position == 'FLEX':
                available = available[available['base_position'].isin(['RB', 'WR', 'TE'])]
            else:
                available = available[available['base_position'] == position]
        
        return available.sort_values('rank')
    
    def search_players(self, df: pd.DataFrame, search_term: str) -> pd.DataFrame:
        """Search for players by name, team, or position"""
        
        search_term = search_term.lower()
        mask = df['search_field'].str.contains(search_term, na=False)
        return df[mask]