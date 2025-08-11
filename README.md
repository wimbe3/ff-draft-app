# Fantasy Football Mock Draft Simulator

**Version 1.2.0** - Updated 2025-08-11

A comprehensive Fantasy Football Mock Draft Simulator built with Streamlit, featuring smart autopick algorithms, keeper support, and a beautiful Sleeper-style interface.

## Recent Updates (v1.2.0)
- Fixed autopick algorithm to correctly handle player selection
- Fixed draft position tracking - users can now draft from any position  
- Enhanced SOS display with text labels and visual indicators
- Improved debugging and error handling
- Performance optimizations for large player pools

## Features

### Core Functionality
- **File Upload**: Upload custom player rankings CSV or use the included sample file
- **League Configuration**: Support for 8-14 teams with customizable roster positions
- **Snake Draft**: Proper snake draft order implementation
- **Keeper System**: Pre-assign players to teams in specific rounds
- **Smart Autopick**: Advanced algorithm balancing best player available with positional scarcity
- **Live Draft Board**: Sleeper-style grid with position-based color coding
- **Player Rankings**: Searchable/filterable player list with real-time availability
- **Team Rosters**: Track each team's roster with position requirements
- **Export Options**: Save results to CSV, Excel, JSON, or HTML formats

### Autopick Algorithm
The intelligent autopick system considers:
- Player ranking and value
- Positional needs based on roster requirements
- Position scarcity (remaining quality players)
- Tier breaks (last player in a tier gets priority)
- ADP value (players falling past their ADP)
- Strategy adjustments (Zero-RB, Zero-WR detection)

### Visual Features
- Position-specific color coding:
  - QB: Red (#FF6B6B)
  - RB: Teal (#4ECDC4)
  - WR: Blue (#45B7D1)
  - TE: Green (#96CEB4)
  - K: Yellow (#FFEAA7)
  - DST: Purple (#DDA0DD)
- Animated current pick indicator
- Hover effects and smooth transitions
- Mobile-responsive design
- Dark mode sidebar with gradient backgrounds

## 🚀 Deployment

### Live Demo (Streamlit Community Cloud)
Visit the app at: [Your App URL - Will be added after deployment]

### Local Installation

#### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git (for cloning repository)

#### Setup
1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/ff-draft-app.git
cd ff-draft-app
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Application
Run the following command in the project directory:
```bash
streamlit run streamlit_app.py
```

The application will open in your default web browser at `http://localhost:8501`

### Quick Start Guide

1. **Upload Rankings** (optional)
   - Use the file uploader in the sidebar to upload a custom rankings CSV
   - If no file is uploaded, the sample FantasyPros rankings will be used

2. **Configure League Settings**
   - Set number of teams (8-14)
   - Choose your draft position
   - Configure roster requirements for each position

3. **Enable Keepers** (optional)
   - Check "Enable Keepers" in the sidebar
   - Assign players to teams in the Keepers tab

4. **Start the Draft**
   - Click "Start Draft" to begin
   - The draft board will appear with the current pick highlighted

5. **Making Picks**
   - **Manual Pick**: Select a player from the Available Players table and click "Make Pick"
   - **Autopick**: Click "Autopick" to let the AI make the current pick
   - **Simulate**: Click "Sim to Pick" to simulate all picks until your next turn

6. **Track Progress**
   - View the draft board to see all picks
   - Check Team Rosters to see each team's selections
   - Monitor the Analysis tab for trends and grades

7. **Export Results**
   - Click export buttons to save the draft in various formats
   - Save draft state to resume later

### CSV File Format
The rankings CSV should include these columns (order doesn't matter):
- `RK` or `RANK`: Overall ranking
- `PLAYER NAME` or `PLAYER`: Player's full name
- `TEAM`: NFL team abbreviation
- `POS` or `POSITION`: Position with rank (e.g., "WR1", "RB2")
- `BYE`: Bye week number
- `TIERS`: Tier grouping (optional)
- `ADP`: Average Draft Position (optional)
- `ECR VS ADP`: Difference between ECR and ADP (optional)

## File Structure
```
FF_Draft_App/
├── streamlit_app.py          # Main application entry point
├── data_processor.py          # CSV handling and data processing
├── draft_logic.py            # Draft mechanics and autopick algorithm
├── ui_components.py          # UI rendering components
├── session_manager.py        # Session state management
├── styles.py                 # CSS styling and themes
├── export_manager.py         # Export functionality
├── requirements.txt          # Python dependencies
├── README.md                # This file
└── FantasyPros_2025_Draft_ALL_Rankings.csv  # Sample rankings data
```

## Features in Detail

### Smart Autopick Algorithm
The autopick system uses a weighted scoring model:
- **40%** - Base player value (ranking)
- **30%** - Positional need based on roster requirements
- **15%** - Position scarcity in remaining player pool
- **10%** - Tier considerations (bonus for last player in tier)
- **5%** - ADP value (players falling past their ADP)

Additional adjustments:
- Avoids drafting backup QB/TE/K/DST too early
- Recognizes Zero-RB and Zero-WR strategies
- Penalizes extreme reaches
- Adds slight randomness for realism

### Keeper System
- Assign any undrafted player to any team
- Specify the round for each keeper
- Keepers are locked into their assigned rounds
- Visual indicators show keeper selections

### Export Options
- **CSV**: Simple draft results table
- **Excel**: Multi-sheet workbook with detailed analysis
- **JSON**: Structured data for programmatic use
- **HTML**: Formatted report with styling

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all packages are installed: `pip install -r requirements.txt`
   - Update pip if needed: `pip install --upgrade pip`

2. **File Upload Issues**
   - Ensure CSV file follows the expected format
   - Check for special characters in player names
   - Verify column names match expected values

3. **Performance Issues**
   - Clear browser cache
   - Restart the Streamlit server
   - Reduce number of rounds if needed

## Tips for Best Experience

1. **Draft Strategy**
   - Use the tier information to identify value picks
   - Monitor position runs in the Analysis tab
   - Watch for players falling past their ADP

2. **Keyboard Shortcuts**
   - Use browser refresh (F5) to reset if needed
   - Ctrl+F to search for specific players

3. **Mobile Usage**
   - The app is mobile-responsive
   - Use landscape mode for best draft board view
   - Zoom out to see more of the board at once

## Future Enhancements
- Trade analyzer
- Dynasty league support
- Custom scoring settings
- Mock draft history tracking
- AI draft grades and recommendations
- Integration with live draft platforms

## License
This project is provided as-is for educational and personal use.

## Credits
Built with ❤️ using Streamlit and Python"# ff-draft-app" 
