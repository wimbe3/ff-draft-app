"""
Styling module for Fantasy Football Mock Draft Simulator
Provides custom CSS and theming
"""

import streamlit as st

def apply_custom_styles():
    """Apply custom CSS styles to the Streamlit app"""
    
    st.markdown("""
    <style>
    /* Global styles - Clean white background */
    .stApp {
        background-color: #f5f7fa;
    }
    
    .main {
        background-color: white;
        padding: 0;
    }
    
    /* Fix text color issues */
    .stMarkdown, .stText, p, span, div {
        color: #2c3e50 !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50 !important;
    }
    
    /* Sidebar styling - Clean dark theme */
    section[data-testid="stSidebar"] {
        background-color: #2c3e50;
    }
    
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    /* Position-based colors */
    .position-qb {
        background-color: #FF6B6B !important;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .position-rb {
        background-color: #4ECDC4 !important;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .position-wr {
        background-color: #45B7D1 !important;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .position-te {
        background-color: #96CEB4 !important;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .position-k {
        background-color: #FFEAA7 !important;
        color: black;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .position-dst {
        background-color: #DDA0DD !important;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    
    /* Draft board styles */
    .draft-cell {
        padding: 8px;
        border-radius: 5px;
        text-align: center;
        font-size: 12px;
        margin: 2px;
        transition: all 0.3s ease;
    }
    
    .draft-cell:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .draft-cell-empty {
        background-color: #f0f0f0;
        opacity: 0.6;
        border: 1px dashed #ccc;
    }
    
    .draft-cell-filled {
        opacity: 1;
        border: 1px solid #333;
    }
    
    .draft-cell-current {
        border: 3px solid #FFD700 !important;
        animation: pulse 2s infinite;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
    }
    
    @keyframes pulse {
        0% {
            transform: scale(1);
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
        }
        50% {
            transform: scale(1.05);
            box-shadow: 0 0 30px rgba(255, 215, 0, 0.8);
        }
        100% {
            transform: scale(1);
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
        }
    }
    
    /* Button styles - Clean and professional */
    .stButton > button {
        background-color: #4CAF50;
        color: white !important;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        background-color: #45a049;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    button[kind="primary"] {
        background-color: #2196F3 !important;
    }
    
    button[kind="primary"]:hover {
        background-color: #1976D2 !important;
    }
    
    button[kind="secondary"] {
        background-color: #FF9800 !important;
    }
    
    button[kind="secondary"]:hover {
        background-color: #F57C00 !important;
    }
    
    /* Metric styles - Clean cards */
    [data-testid="metric-container"] {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #6c757d !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #2c3e50 !important;
    }
    
    /* Tab styles - Professional look */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        border-bottom: 2px solid #e0e0e0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #6c757d !important;
        border: none;
        border-bottom: 3px solid transparent;
        border-radius: 0;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f8f9fa;
        color: #2c3e50 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: #2196F3 !important;
        border-bottom: 3px solid #2196F3;
    }
    
    /* Table styles */
    .dataframe {
        font-size: 14px;
    }
    
    .dataframe tbody tr:hover {
        background-color: rgba(102, 126, 234, 0.1);
        cursor: pointer;
    }
    
    /* Alert styles */
    .stAlert {
        border-radius: 10px;
        border-left: 5px solid;
        padding: 15px;
    }
    
    .stSuccess {
        border-left-color: #00d26a;
        background-color: rgba(0, 210, 106, 0.1);
    }
    
    .stWarning {
        border-left-color: #fca311;
        background-color: rgba(252, 163, 17, 0.1);
    }
    
    .stError {
        border-left-color: #f5576c;
        background-color: rgba(245, 87, 108, 0.1);
    }
    
    .stInfo {
        border-left-color: #4facfe;
        background-color: rgba(79, 172, 254, 0.1);
    }
    
    /* Selectbox styles - Enhanced contrast */
    .stSelectbox > div > div {
        background-color: white !important;
        border-radius: 5px;
        border: 2px solid #333 !important;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #2196F3 !important;
        box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.2);
    }
    
    .stSelectbox label {
        color: #2c3e50 !important;
        font-weight: 600 !important;
    }
    
    /* Dropdown menu styling */
    [data-baseweb="popover"] {
        background-color: white !important;
        border: 2px solid #333 !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    
    [data-baseweb="menu"] {
        background-color: white !important;
    }
    
    [role="option"] {
        color: #2c3e50 !important;
        background-color: white !important;
    }
    
    [role="option"]:hover {
        background-color: #f0f0f0 !important;
    }
    
    [aria-selected="true"] {
        background-color: #2196F3 !important;
        color: white !important;
    }
    
    /* Number input styles */
    .stNumberInput > div > div > input {
        background-color: white !important;
        color: #2c3e50 !important;
        border-radius: 5px;
        border: 1px solid #ddd !important;
        transition: all 0.3s ease;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: #2196F3 !important;
        box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
    }
    
    /* Text input styles */
    .stTextInput > div > div > input {
        background-color: white !important;
        color: #2c3e50 !important;
        border: 1px solid #ddd !important;
        border-radius: 5px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2196F3 !important;
        box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
    }
    
    /* Checkbox styles */
    .stCheckbox > label > div {
        transition: all 0.3s ease;
    }
    
    .stCheckbox > label > div:hover {
        transform: scale(1.1);
    }
    
    /* Divider styles */
    .stDivider {
        margin: 20px 0;
        border-top: 2px solid #e0e0e0;
    }
    
    /* Scrollbar styles - Clean and subtle */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .main {
            padding: 10px;
            margin: 5px;
        }
        
        .draft-cell {
            font-size: 10px;
            padding: 5px;
        }
        
        .stButton > button {
            padding: 8px 15px;
            font-size: 14px;
        }
    }
    
    /* Tooltip styles - white text on dark background for better contrast */
    [data-baseweb="tooltip"] {
        background-color: rgba(33, 37, 41, 0.95) !important;
    }
    
    [data-baseweb="tooltip"] > div {
        color: white !important;
        font-size: 14px !important;
        font-weight: 400 !important;
    }
    
    /* Help tooltip icon styling */
    .stTooltipIcon {
        color: #6c757d;
    }
    
    /* Tooltip content styling */
    div[role="tooltip"] {
        background-color: rgba(33, 37, 41, 0.95) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    div[role="tooltip"] * {
        color: white !important;
    }
    
    /* Button tooltip styling */
    button[title] {
        position: relative;
    }
    
    button[title]:hover::after {
        color: white !important;
    }
    
    /* Custom animations */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-slide-in {
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    .animate-fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Draft timer styles - Clean design */
    .draft-timer {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        border-radius: 8px;
        background-color: #2196F3;
        color: white;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .draft-timer.warning {
        background-color: #FF5722;
        animation: pulse 1s infinite;
    }
    
    /* Team roster styles */
    .roster-position {
        display: inline-block;
        padding: 5px 10px;
        margin: 2px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 12px;
    }
    
    .roster-need-high {
        background-color: #ff6b6b;
        color: white;
    }
    
    .roster-need-medium {
        background-color: #fca311;
        color: white;
    }
    
    .roster-need-low {
        background-color: #00d26a;
        color: white;
    }
    
    /* Value indicator styles - Clean badges */
    .value-pick {
        background-color: #4CAF50;
        color: white;
        padding: 3px 8px;
        border-radius: 3px;
        font-size: 11px;
        font-weight: bold;
        margin-left: 5px;
    }
    
    .reach-pick {
        background-color: #f44336;
        color: white;
        padding: 3px 8px;
        border-radius: 3px;
        font-size: 11px;
        font-weight: bold;
        margin-left: 5px;
    }
    
    /* Tier break indicator */
    .tier-break {
        border-top: 3px solid #ffd700;
        margin: 5px 0;
        position: relative;
    }
    
    .tier-break::after {
        content: "TIER BREAK";
        position: absolute;
        top: -12px;
        right: 10px;
        background: #ffd700;
        color: black;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 10px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

def get_position_style(position: str) -> str:
    """Get CSS class for position styling"""
    
    position_map = {
        'QB': 'position-qb',
        'RB': 'position-rb',
        'WR': 'position-wr',
        'TE': 'position-te',
        'K': 'position-k',
        'DST': 'position-dst',
        'DEF': 'position-dst',
        'D/ST': 'position-dst'
    }
    
    return position_map.get(position.upper(), '')

def format_position_badge(position: str, text: str = None) -> str:
    """Format a position badge with appropriate styling"""
    
    if text is None:
        text = position
    
    css_class = get_position_style(position)
    return f'<span class="{css_class}">{text}</span>'

def format_value_indicator(adp_diff: float) -> str:
    """Format value indicator based on ADP difference"""
    
    if adp_diff >= 10:
        return '<span class="value-pick">VALUE</span>'
    elif adp_diff <= -10:
        return '<span class="reach-pick">REACH</span>'
    return ''

def format_roster_need(need_score: float, position: str) -> str:
    """Format roster need indicator"""
    
    if need_score > 0.7:
        css_class = 'roster-need-high'
    elif need_score > 0.3:
        css_class = 'roster-need-medium'
    else:
        css_class = 'roster-need-low'
    
    return f'<span class="roster-position {css_class}">{position}</span>'

def create_gradient_background(start_color: str, end_color: str) -> str:
    """Create CSS gradient background"""
    
    return f"background: linear-gradient(135deg, {start_color} 0%, {end_color} 100%);"

def apply_hover_effect(element_class: str) -> str:
    """Apply hover effect CSS"""
    
    return f"""
    .{element_class} {{
        transition: all 0.3s ease;
        cursor: pointer;
    }}
    
    .{element_class}:hover {{
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }}
    """