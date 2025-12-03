"""
Manual Underdog Data Import
Parses and stores manually input Underdog Fantasy lines
"""

# Extracted Underdog lines from PDF
UNDERDOG_LINES = [
    {"player_name": "Djon8", "stat_type": "kills", "line": 32.5, "team": "SPARTA"},
    {"player_name": "Djon8", "stat_type": "headshots", "line": 18.5, "team": "SPARTA"},
    {"player_name": "Ryujin", "stat_type": "kills", "line": 29.5, "team": ""},
    {"player_name": "Ryujin", "stat_type": "headshots", "line": 16.5, "team": ""},
    {"player_name": "Get_Jeka", "stat_type": "kills", "line": 25.5, "team": "ARCRED"},
    {"player_name": "Get_Jeka", "stat_type": "headshots", "line": 15.5, "team": "ARCRED"},
    {"player_name": "SoLb", "stat_type": "kills", "line": 25.5, "team": "SPARTA"},
    {"player_name": "SoLb", "stat_type": "headshots", "line": 12.5, "team": "SPARTA"},
    {"player_name": "Chill", "stat_type": "kills", "line": 25.5, "team": "ARCRED"},
    {"player_name": "Chill", "stat_type": "headshots", "line": 16.5, "team": "ARCRED"},
    {"player_name": "yuramyata", "stat_type": "kills", "line": 31.5, "team": "SPARTA"},
    {"player_name": "yuramyata", "stat_type": "headshots", "line": 10.5, "team": "SPARTA"},
    {"player_name": "1NVISIBLEE", "stat_type": "kills", "line": 30.5, "team": "SPARTA"},
    {"player_name": "1NVISIBLEE", "stat_type": "headshots", "line": 16.5, "team": "SPARTA"},
    {"player_name": "DSSj", "stat_type": "kills", "line": 29.5, "team": "ARCRED"},
    {"player_name": "DSSj", "stat_type": "headshots", "line": 11.5, "team": "ARCRED"},
    {"player_name": "Raijin", "stat_type": "kills", "line": 28.5, "team": "ARCRED"},
    {"player_name": "Raijin", "stat_type": "headshots", "line": 17.5, "team": "ARCRED"},
    {"player_name": "k4nfuz", "stat_type": "kills", "line": 26.5, "team": "SPARTA"},
    {"player_name": "k4nfuz", "stat_type": "headshots", "line": 16.5, "team": "SPARTA"},
    # Add more as needed...
]

def get_underdog_props():
    """
    Returns Underdog props in the same format as scrapers
    """
    props = []
    for line_data in UNDERDOG_LINES:
        props.append({
            'player_name': line_data['player_name'],
            'team': line_data.get('team', ''),
            'stat_type': line_data['stat_type'],
            'line': line_data['line'],
            'platform': 'underdog',
            'maps': 'Map1+Map2'
        })
    return props
