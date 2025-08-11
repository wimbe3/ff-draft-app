# Fantasy Football Mock Draft App - Complete Implementation Guide

## Project Overview
Build a Streamlit-based fantasy football mock draft application with keeper support, autopick intelligence, and Sleeper-style grid visualization.

## Core Architecture & File Structure

```
fantasy-draft-app/
├── app.py                 # Main Streamlit application
├── draft_logic.py         # Draft mechanics and autopick algorithm
├── data_processor.py      # CSV parsing and data management
├── ui_components.py       # Reusable UI components
├── export_handler.py      # CSV/PDF export functionality
├── requirements.txt       # Dependencies
└── FantasyPros_2025_Draft_ALL_Rankings.csv  # Sample data file
```

## Implementation Specifications

### 1. **Data Processing Module** (`data_processor.py`)

```python
# Core data structure after CSV processing
players_df = {
    'rank': int,
    'tier': int,
    'name': str,
    'team': str,
    'position': str,
    'bye': str,
    'sos': str,  # Convert to 1-5 star rating
    'ecr_vs_adp': str,
    'drafted': bool,
    'drafted_by': str,
    'draft_position': int
}
```

**SOS Conversion Logic:**
- Parse SOS string and map to 1-5 star rating
- Create gradient: 5 stars = green (#10B981), 1 star = red (#EF4444)

### 2. **Session State Management**

```python
st.session_state structure:
{
    'rankings_data': DataFrame,
    'league_settings': {
        'num_teams': int (default: 12),
        'user_pick': int (1-12),
        'roster': {
            'QB': 1, 'RB': 2, 'WR': 2, 'TE': 1,
            'FLEX': 2, 'K': 1, 'DST': 1, 'BENCH': 7
        },
        'undo_enabled': bool
    },
    'keepers': {
        'team_1': {'player': str, 'round': int},
        # ... for each team
    },
    'draft_board': 2D array [round][pick],
    'current_pick': {'round': int, 'pick': int},
    'team_rosters': {team_id: [player_objects]},
    'draft_history': [],
    'draft_complete': bool
}
```

### 3. **UI Flow & Components**

#### **Page Layout Structure:**

```python
# Sidebar Configuration
with st.sidebar:
    # Step 1: Instructions & File Upload
    # Step 2: League Settings
    # Step 3: Keeper Configuration
    # Step 4: Draft Controls (during draft)
    
# Main Area
if not draft_started:
    # Setup view with keeper table
else:
    # Draft board (Sleeper-style grid)
    # Available players rankings
    # Team rosters view
```

#### **Sleeper-Style Draft Board:**

```python
# Visual Grid Specifications:
- Columns: Team names (1-12)
- Rows: Rounds (1-16 typical)
- Cell styling:
  * QB: #FF6B6B (red)
  * RB: #4ECDC4 (teal)
  * WR: #45B7D1 (blue)
  * TE: #FFA07A (light salmon)
  * FLEX-eligible: gradient border
  * K: #FFD700 (gold)
  * DST: #8B4513 (brown)
- Keeper cells: Bold with star icon ⭐
- Current pick: Pulsing border animation
```

### 4. **Keeper System Implementation**

```python
def configure_keepers():
    # For each team:
    # - Dropdown: Available players (no duplicates across teams)
    # - Dropdown: Round selection (1-16)
    # - Validation: No duplicate players
    # - Update draft board and mark as unavailable
    
keeper_widget = st.columns([3, 1, 1])  # [Player, Round, Remove]
```

### 5. **Autopick Algorithm**

```python
def autopick_player(team_roster, available_players, round_num):
    """
    Balanced BPA + Positional Scarcity Algorithm
    
    Factors:
    1. Player ranking (40% weight)
    2. Positional scarcity (30% weight)
    3. Roster needs (30% weight)
    
    Early rounds (1-6): Favor RB/WR
    Mid rounds (7-10): Fill starting lineup gaps
    Late rounds (11+): Best available + bench depth
    """
    
    # Calculate positional scarcity score
    # Check roster needs vs limits
    # Apply round-based strategy modifier
    # Return best candidate
```

### 6. **Draft Mechanics**

```python
def execute_draft():
    # Snake draft order calculation
    # Pick timer display (visual only)
    # Undo functionality with confirmation
    # Auto-advance after user pick
    # Position run detection & highlighting
```

### 7. **Rankings Display Panel**

```python
# Live updating available players table
columns = ['Rank', 'Player', 'Team', 'Pos', 'Bye', 'SOS ⭐']

# Features:
# - Search/filter by position
# - Hide drafted players
# - Sort by any column
# - Highlight value picks (ECR vs ADP)
# - SOS star visualization with color gradient
```

### 8. **Export Functionality**

```python
def export_draft_results():
    # CSV Export: Full draft board with picks
    # PDF Export: 
    #   - Draft board grid
    #   - Team rosters
    #   - Draft grades
    #   - Position distribution chart
```

### 9. **Post-Draft Analysis**

```python
def generate_draft_grades():
    """
    Grade each team A-F based on:
    - Average pick value vs ADP
    - Roster balance
    - Strength of starters
    - Bench depth
    - Bye week distribution
    """
```

## Critical Implementation Details

### **State Persistence:**
- Use `st.session_state` for all draft data
- Implement "Reset Draft" button with confirmation
- Auto-save after each pick

### **Performance Optimizations:**
- Cache rankings data processing with `@st.cache_data`
- Lazy load player images if implementing
- Efficient DataFrame filtering for available players

### **Error Handling:**
- Validate CSV format matches expected columns
- Handle missing keeper selections gracefully
- Prevent invalid roster configurations

### **Responsive Design:**
- Use `st.columns()` for adaptive layouts
- Implement container scrolling for draft board
- Mobile-friendly button sizes

## Visual Polish Elements

```python
# CSS Injection for Enhanced UI
st.markdown("""
<style>
    .draft-cell {
        border-radius: 8px;
        padding: 8px;
        transition: all 0.3s ease;
    }
    .current-pick {
        animation: pulse 2s infinite;
        border: 3px solid #FFD700;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 215, 0, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 215, 0, 0); }
    }
</style>
""", unsafe_allow_html=True)
```

## Detailed Feature Specifications

### **Draft Setup Phase**

1. **Welcome Screen**
   - App title: "Fantasy Football Mock Draft Simulator"
   - Brief description of features
   - Clear CTA button: "Start New Draft"

2. **File Upload Section**
   - Instructions with link to FantasyPros
   - Drag-and-drop area or file browser
   - Sample file download option
   - Auto-validation of CSV format

3. **League Configuration**
   - Number of teams slider (8-14, default 12)
   - Draft position selector (1-N based on teams)
   - Scoring format (PPR selected by default)
   - Roster setup with position limits

4. **Keeper Configuration Table**
   - Dynamic table based on number of teams
   - Player name dropdown (searchable)
   - Round selector (1-16)
   - Clear visual feedback for conflicts

### **Draft Execution Phase**

1. **Draft Board Grid**
   - Responsive grid layout
   - Color-coded by position
   - Keeper picks marked with ⭐
   - Current pick highlighted
   - Hover effects for interactivity

2. **Player Rankings Panel**
   - Searchable/filterable list
   - Real-time updates as players drafted
   - SOS rating with star visualization
   - Quick-draft buttons for each player

3. **Team Roster Sidebar**
   - Collapsible team sections
   - Position counts vs requirements
   - Bye week distribution
   - Team strength indicator

4. **Draft Controls**
   - "Draft Player" button
   - "Undo Last Pick" (if enabled)
   - "Autopick for CPU" toggle
   - Round/Pick indicator

### **Post-Draft Phase**

1. **Draft Summary**
   - Complete draft board view
   - Team-by-team breakdown
   - Best/worst picks analysis

2. **Team Grades**
   - Letter grades (A-F)
   - Scoring breakdown
   - Strengths/weaknesses

3. **Export Options**
   - Download CSV button
   - Generate PDF report
   - Copy shareable link (if deployed)

## Testing Checklist

- [ ] CSV upload and parsing works with sample file
- [ ] Keeper assignments prevent duplicates
- [ ] Snake draft order correct
- [ ] Autopick respects roster limits
- [ ] Undo functionality works properly
- [ ] Export generates valid CSV/PDF
- [ ] Session persists through page refresh
- [ ] Draft grades calculate correctly
- [ ] All positions color-coded on board
- [ ] Mobile responsive layout
- [ ] Position scarcity properly calculated
- [ ] FLEX eligibility correctly assigned
- [ ] Bye week conflicts highlighted
- [ ] Value picks identified (ECR vs ADP)

## Sample Data Structure

### Input CSV Columns (from FantasyPros)
- RK: Overall rank
- TIERS: Tier grouping
- PLAYER NAME: Full player name
- TEAM: NFL team abbreviation
- POS: Position (QB/RB/WR/TE/K/DST)
- BYE: Bye week number
- SOS: Strength of schedule
- ECR VS ADP: Expected vs actual draft position

### Processed Player Object
```python
{
    'id': 'unique_player_id',
    'rank': 1,
    'tier': 1,
    'name': 'Christian McCaffrey',
    'team': 'SF',
    'position': 'RB',
    'bye_week': 9,
    'sos_rating': 4.5,  # 1-5 stars
    'ecr_vs_adp': '+2.3',
    'is_drafted': False,
    'drafted_by_team': None,
    'draft_position': None,
    'is_keeper': False,
    'flex_eligible': True  # RB/WR/TE
}
```

## Deployment Configuration

```python
# requirements.txt
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0  # For interactive charts
reportlab>=4.0.0  # For PDF generation
numpy>=1.24.0
```

```python
# .streamlit/config.toml
[theme]
primaryColor = "#4ECDC4"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"

[server]
maxUploadSize = 10
enableCORS = false
```

## Performance Considerations

1. **Data Caching Strategy**
   - Cache parsed CSV data
   - Cache positional scarcity calculations
   - Invalidate cache on roster changes

2. **State Management**
   - Minimize session state updates
   - Batch UI updates where possible
   - Use callbacks efficiently

3. **Rendering Optimization**
   - Virtual scrolling for large player lists
   - Lazy load team roster views
   - Debounce search inputs

## Future Enhancement Ideas

1. **Advanced Features**
   - Trade analyzer
   - Dynasty league support
   - Auction draft mode
   - Custom scoring systems
   - Historical draft analysis

2. **Integrations**
   - Direct FantasyPros API integration
   - ESPN/Yahoo league import
   - Discord bot for draft updates
   - Mobile app companion

3. **Analytics**
   - Advanced autopick AI
   - Predictive draft flow
   - Optimal draft strategy calculator
   - Post-draft trade suggestions

## Notes for Implementation

- Start with core functionality, then add visual polish
- Prioritize user experience over complex features
- Ensure mobile responsiveness from the start
- Build modular components for easy testing
- Comment autopick algorithm logic thoroughly
- Use clear variable names for maintainability