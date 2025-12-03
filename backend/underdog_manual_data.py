"""
Manual Underdog Data Import
Parses and stores manually input Underdog Fantasy lines
"""
import re
import json
import os

# File to store lines persistently
LINES_FILE = '/app/backend/underdog_lines.json'

# Default Underdog lines from PDF
DEFAULT_UNDERDOG_LINES = [
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
]

def load_lines():
    """Load lines from file or use defaults"""
    try:
        if os.path.exists(LINES_FILE):
            with open(LINES_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return DEFAULT_UNDERDOG_LINES

def save_lines(lines):
    """Save lines to file"""
    try:
        with open(LINES_FILE, 'w') as f:
            json.dump(lines, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving lines: {e}")
        return False

def parse_line_text(text):
    """
    Parse various formats of Underdog lines
    
    Supports formats like:
    - "PlayerName, kills, 28.5, TeamName"
    - "PlayerName kills 28.5"
    - "PlayerName: 28.5 kills (TeamName)"
    """
    lines = []
    
    for line_text in text.strip().split('\n'):
        line_text = line_text.strip()
        if not line_text:
            continue
        
        # Try to extract: player name, stat type, value, team
        # Pattern 1: CSV format
        csv_match = re.search(r'([^,]+),\s*(kills|headshots|hs),\s*([\d.]+)(?:,\s*(.+))?', line_text, re.IGNORECASE)
        if csv_match:
            player_name = csv_match.group(1).strip()
            stat_type = 'headshots' if 'head' in csv_match.group(2).lower() or csv_match.group(2).lower() == 'hs' else 'kills'
            line_value = float(csv_match.group(3))
            team = csv_match.group(4).strip() if csv_match.group(4) else ''
            
            lines.append({
                'player_name': player_name,
                'stat_type': stat_type,
                'line': line_value,
                'team': team
            })
            continue
        
        # Pattern 2: Space-separated
        space_match = re.search(r'(\S+)\s+(kills|headshots|hs)\s+([\d.]+)(?:\s+(.+))?', line_text, re.IGNORECASE)
        if space_match:
            player_name = space_match.group(1).strip()
            stat_type = 'headshots' if 'head' in space_match.group(2).lower() or space_match.group(2).lower() == 'hs' else 'kills'
            line_value = float(space_match.group(3))
            team = space_match.group(4).strip() if space_match.group(4) else ''
            
            lines.append({
                'player_name': player_name,
                'stat_type': stat_type,
                'line': line_value,
                'team': team
            })
            continue
    
    return lines

def parse_and_save_lines(text):
    """Parse input text and save as Underdog lines"""
    parsed_lines = parse_line_text(text)
    
    if parsed_lines:
        save_lines(parsed_lines)
    
    return len(parsed_lines)

def get_underdog_props():
    """
    Returns Underdog props in the same format as scrapers
    """
    lines = load_lines()
    props = []
    
    for line_data in lines:
        props.append({
            'player_name': line_data['player_name'],
            'team': line_data.get('team', ''),
            'stat_type': line_data['stat_type'],
            'line': line_data['line'],
            'platform': 'underdog',
            'maps': 'Map1+Map2'
        })
    return props
