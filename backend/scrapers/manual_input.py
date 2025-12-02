"""
Manual data input helper for PrizePicks and CS2 matches
This allows users to manually input data when scraping is blocked
"""
import logging
from typing import List, Dict
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

class ManualDataProvider:
    """Provides interface for manual data input when scraping fails"""
    
    def get_sample_cs2_data(self) -> tuple[List[Dict], List[Dict]]:
        """
        Returns sample/template CS2 data structure
        Users can modify this to input real data from PrizePicks
        """
        logger.info("Using sample data template - replace with real PrizePicks data")
        
        # Sample matches structure
        matches = [
            {
                'team1': 'Team Liquid',
                'team2': 'Natus Vincere',
                'tournament': 'IEM Katowice 2025',
                'start_time': datetime.now(timezone.utc) + timedelta(hours=3),
                'map1': 'Mirage',
                'map2': 'Dust2',
                'status': 'upcoming'
            }
        ]
        
        # Sample props structure from PrizePicks
        props = [
            {
                'player_name': 'EliGE',
                'stat_type': 'kills',
                'line': 42.5,
                'platform': 'prizepicks',
                'maps': 'Map1+Map2'
            },
            {
                'player_name': 'EliGE',
                'stat_type': 'headshots',
                'line': 18.5,
                'platform': 'prizepicks',
                'maps': 'Map1+Map2'
            },
            {
                'player_name': 's1mple',
                'stat_type': 'kills',
                'line': 45.5,
                'platform': 'prizepicks',
                'maps': 'Map1+Map2'
            },
            {
                'player_name': 's1mple',
                'stat_type': 'headshots',
                'line': 19.5,
                'platform': 'prizepicks',
                'maps': 'Map1+Map2'
            },
        ]
        
        return matches, props
    
    def parse_manual_input(self, raw_text: str) -> List[Dict]:
        """
        Parse manually pasted PrizePicks data
        Expected format: Player Name, Stat Type, Line
        Example: s1mple, kills, 45.5
        """
        props = []
        
        try:
            lines = raw_text.strip().split('\n')
            for line in lines:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 3:
                    props.append({
                        'player_name': parts[0],
                        'stat_type': parts[1].lower(),
                        'line': float(parts[2]),
                        'platform': 'prizepicks',
                        'maps': 'Map1+Map2'
                    })
            
            logger.info(f"Parsed {len(props)} manual props")
            return props
            
        except Exception as e:
            logger.error(f"Error parsing manual input: {e}")
            return []
