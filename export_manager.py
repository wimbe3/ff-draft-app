"""
Export management module for Fantasy Football Mock Draft Simulator
Handles exporting draft results to various formats
"""

import pandas as pd
import io
from datetime import datetime
from typing import Dict, List, Optional
import base64

class ExportManager:
    """Handles export functionality for draft results"""
    
    def __init__(self):
        self.export_formats = ['csv', 'excel', 'json', 'html']
    
    def export_to_csv(self, draft_engine) -> str:
        """Export draft results to CSV format"""
        
        # Create draft summary
        draft_data = []
        
        # Add draft picks
        for pick in draft_engine.draft_history:
            player_data = draft_engine.players_df[
                draft_engine.players_df['player_name'] == pick.player_name
            ]
            
            if not player_data.empty:
                player = player_data.iloc[0]
                draft_data.append({
                    'Pick': pick.pick_number,
                    'Round': pick.round,
                    'Team': draft_engine.teams[pick.team].team_name,
                    'Player': pick.player_name,
                    'Position': pick.position,
                    'NFL Team': player.get('team', 'N/A'),
                    'Bye Week': player.get('bye', 'N/A'),
                    'Rank': player.get('rank', 'N/A'),
                    'ADP': player.get('adp', 'N/A'),
                    'Tier': player.get('tier', 'N/A'),
                    'Keeper': 'Yes' if pick.is_keeper else 'No'
                })
        
        # Create DataFrame
        df = pd.DataFrame(draft_data)
        
        # Convert to CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_str = csv_buffer.getvalue()
        
        return csv_str
    
    def export_to_excel(self, draft_engine) -> bytes:
        """Export draft results to Excel format with multiple sheets"""
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Sheet 1: Draft Results
            draft_df = self._create_draft_dataframe(draft_engine)
            draft_df.to_excel(writer, sheet_name='Draft Results', index=False)
            
            # Sheet 2: Team Rosters
            rosters_df = self._create_rosters_dataframe(draft_engine)
            rosters_df.to_excel(writer, sheet_name='Team Rosters', index=False)
            
            # Sheet 3: Position Summary
            position_df = self._create_position_summary(draft_engine)
            position_df.to_excel(writer, sheet_name='Position Summary', index=False)
            
            # Sheet 4: Draft Analysis
            analysis_df = self._create_draft_analysis(draft_engine)
            analysis_df.to_excel(writer, sheet_name='Draft Analysis', index=False)
        
        output.seek(0)
        return output.getvalue()
    
    def export_to_json(self, draft_engine) -> str:
        """Export draft results to JSON format"""
        
        export_data = {
            'meta': {
                'export_date': datetime.now().isoformat(),
                'num_teams': draft_engine.num_teams,
                'total_rounds': draft_engine.total_rounds,
                'user_position': draft_engine.user_position,
                'roster_config': draft_engine.roster_config
            },
            'draft_picks': [],
            'teams': {},
            'keepers': []
        }
        
        # Add draft picks
        for pick in draft_engine.draft_history:
            player_data = draft_engine.players_df[
                draft_engine.players_df['player_name'] == pick.player_name
            ]
            
            if not player_data.empty:
                player = player_data.iloc[0]
                export_data['draft_picks'].append({
                    'pick_number': pick.pick_number,
                    'round': pick.round,
                    'team_id': pick.team,
                    'player': {
                        'name': pick.player_name,
                        'position': pick.position,
                        'team': player.get('team', 'N/A'),
                        'bye': int(player.get('bye', 0)) if pd.notna(player.get('bye')) else None,
                        'rank': int(player.get('rank', 0)) if pd.notna(player.get('rank')) else None,
                        'adp': float(player.get('adp', 0)) if pd.notna(player.get('adp')) else None,
                        'tier': int(player.get('tier', 0)) if pd.notna(player.get('tier')) else None
                    },
                    'is_keeper': pick.is_keeper
                })
        
        # Add team rosters
        for team_id, team in draft_engine.teams.items():
            export_data['teams'][str(team_id)] = {
                'name': team.team_name,
                'draft_position': team.draft_position,
                'roster': [
                    {
                        'player': pick.player_name,
                        'position': pick.position,
                        'round': pick.round
                    }
                    for pick in team.roster
                ]
            }
        
        # Add keepers
        for team_id, keepers in draft_engine.keepers.items():
            for player_id, round_num in keepers:
                player = draft_engine.players_df.loc[player_id]
                export_data['keepers'].append({
                    'team_id': team_id,
                    'player': player['player_name'],
                    'round': round_num
                })
        
        import json
        return json.dumps(export_data, indent=2)
    
    def export_to_html(self, draft_engine) -> str:
        """Export draft results to HTML format with styling"""
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Fantasy Football Mock Draft Results</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }
                .container {
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    max-width: 1200px;
                    margin: 0 auto;
                }
                h1 {
                    color: #333;
                    text-align: center;
                    border-bottom: 3px solid #667eea;
                    padding-bottom: 10px;
                }
                h2 {
                    color: #667eea;
                    margin-top: 30px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }
                th {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 10px;
                    text-align: left;
                }
                td {
                    padding: 8px;
                    border-bottom: 1px solid #ddd;
                }
                tr:hover {
                    background-color: rgba(102, 126, 234, 0.1);
                }
                .position-QB { background-color: #FF6B6B; color: white; padding: 2px 5px; border-radius: 3px; }
                .position-RB { background-color: #4ECDC4; color: white; padding: 2px 5px; border-radius: 3px; }
                .position-WR { background-color: #45B7D1; color: white; padding: 2px 5px; border-radius: 3px; }
                .position-TE { background-color: #96CEB4; color: white; padding: 2px 5px; border-radius: 3px; }
                .position-K { background-color: #FFEAA7; color: black; padding: 2px 5px; border-radius: 3px; }
                .position-DST { background-color: #DDA0DD; color: white; padding: 2px 5px; border-radius: 3px; }
                .meta-info {
                    background: #f5f5f5;
                    padding: 10px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }
                .team-section {
                    margin-top: 20px;
                    padding: 15px;
                    background: #f9f9f9;
                    border-radius: 5px;
                }
            </style>
        </head>
        <body>
            <div class="container">
        """
        
        # Add header
        html_content += f"""
            <h1>Fantasy Football Mock Draft Results</h1>
            <div class="meta-info">
                <strong>Date:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br>
                <strong>League Size:</strong> {draft_engine.num_teams} teams<br>
                <strong>Total Rounds:</strong> {draft_engine.total_rounds}<br>
                <strong>Your Draft Position:</strong> #{draft_engine.user_position}
            </div>
        """
        
        # Add draft results table
        html_content += """
            <h2>Draft Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>Pick</th>
                        <th>Round</th>
                        <th>Team</th>
                        <th>Player</th>
                        <th>Position</th>
                        <th>NFL Team</th>
                        <th>Bye</th>
                        <th>Rank</th>
                        <th>ADP</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for pick in draft_engine.draft_history:
            player_data = draft_engine.players_df[
                draft_engine.players_df['player_name'] == pick.player_name
            ]
            
            if not player_data.empty:
                player = player_data.iloc[0]
                html_content += f"""
                    <tr>
                        <td>{pick.pick_number}</td>
                        <td>{pick.round}</td>
                        <td>{draft_engine.teams[pick.team].team_name}</td>
                        <td>{pick.player_name}</td>
                        <td><span class="position-{pick.position}">{pick.position}</span></td>
                        <td>{player.get('team', 'N/A')}</td>
                        <td>{player.get('bye', 'N/A')}</td>
                        <td>{player.get('rank', 'N/A')}</td>
                        <td>{player.get('adp', 'N/A')}</td>
                    </tr>
                """
        
        html_content += """
                </tbody>
            </table>
        """
        
        # Add team rosters
        html_content += "<h2>Team Rosters</h2>"
        
        for team_id, team in draft_engine.teams.items():
            if team.roster:
                html_content += f"""
                    <div class="team-section">
                        <h3>{team.team_name}</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>Round</th>
                                    <th>Player</th>
                                    <th>Position</th>
                                </tr>
                            </thead>
                            <tbody>
                """
                
                for pick in sorted(team.roster, key=lambda x: x.round):
                    html_content += f"""
                        <tr>
                            <td>{pick.round}</td>
                            <td>{pick.player_name}</td>
                            <td><span class="position-{pick.position}">{pick.position}</span></td>
                        </tr>
                    """
                
                html_content += """
                            </tbody>
                        </table>
                    </div>
                """
        
        # Close HTML
        html_content += """
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _create_draft_dataframe(self, draft_engine) -> pd.DataFrame:
        """Create DataFrame of draft results"""
        
        draft_data = []
        
        for pick in draft_engine.draft_history:
            player_data = draft_engine.players_df[
                draft_engine.players_df['player_name'] == pick.player_name
            ]
            
            if not player_data.empty:
                player = player_data.iloc[0]
                draft_data.append({
                    'Pick': pick.pick_number,
                    'Round': pick.round,
                    'Team': draft_engine.teams[pick.team].team_name,
                    'Player': pick.player_name,
                    'Position': pick.position,
                    'NFL Team': player.get('team', 'N/A'),
                    'Bye Week': player.get('bye', 'N/A'),
                    'Rank': player.get('rank', 'N/A'),
                    'ADP': player.get('adp', 'N/A'),
                    'Tier': player.get('tier', 'N/A'),
                    'Keeper': 'Yes' if pick.is_keeper else 'No'
                })
        
        return pd.DataFrame(draft_data)
    
    def _create_rosters_dataframe(self, draft_engine) -> pd.DataFrame:
        """Create DataFrame of team rosters"""
        
        roster_data = []
        
        for team_id, team in draft_engine.teams.items():
            for pick in team.roster:
                roster_data.append({
                    'Team': team.team_name,
                    'Round': pick.round,
                    'Player': pick.player_name,
                    'Position': pick.position,
                    'Keeper': 'Yes' if pick.is_keeper else 'No'
                })
        
        return pd.DataFrame(roster_data)
    
    def _create_position_summary(self, draft_engine) -> pd.DataFrame:
        """Create position summary DataFrame"""
        
        position_data = []
        
        for team_id, team in draft_engine.teams.items():
            roster_by_pos = team.get_roster_by_position()
            
            summary = {'Team': team.team_name}
            for pos in ['QB', 'RB', 'WR', 'TE', 'K', 'DST']:
                summary[pos] = len(roster_by_pos.get(pos, []))
            
            position_data.append(summary)
        
        return pd.DataFrame(position_data)
    
    def _create_draft_analysis(self, draft_engine) -> pd.DataFrame:
        """Create draft analysis DataFrame"""
        
        analysis_data = []
        
        for team_id, team in draft_engine.teams.items():
            if team.roster:
                # Calculate average rank
                ranks = []
                for pick in team.roster:
                    if not pick.is_keeper:
                        player_data = draft_engine.players_df[
                            draft_engine.players_df['player_name'] == pick.player_name
                        ]
                        if not player_data.empty:
                            ranks.append(player_data.iloc[0]['rank'])
                
                avg_rank = sum(ranks) / len(ranks) if ranks else 0
                
                analysis_data.append({
                    'Team': team.team_name,
                    'Total Picks': len(team.roster),
                    'Keepers': len(team.keepers),
                    'Avg Player Rank': round(avg_rank, 1),
                    'First Pick': team.roster[0].player_name if team.roster else 'N/A'
                })
        
        return pd.DataFrame(analysis_data)
    
    def create_download_link(self, data: str, filename: str, mime_type: str) -> str:
        """Create a download link for exported data"""
        
        b64 = base64.b64encode(data.encode()).decode()
        href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}">Download {filename}</a>'
        return href