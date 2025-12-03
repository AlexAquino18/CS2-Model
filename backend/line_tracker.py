"""
PrizePicks Line Movement Tracker
Tracks historical line changes for value opportunity identification
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class LineMovementTracker:
    """Tracks PrizePicks line movements over time"""
    
    def __init__(self):
        # Store line history: {player_name: {stat_type: [(timestamp, line, platform)]}}
        self.line_history = defaultdict(lambda: defaultdict(list))
        
        # Store latest lines for quick access
        self.current_lines = {}
        
        # Movement thresholds
        self.significant_movement_threshold = 1.5  # kills
        self.significant_movement_threshold_hs = 1.0  # headshots
    
    def record_lines(self, props: List[Dict]) -> None:
        """
        Record current lines from scraped props
        
        Args:
            props: List of prop dictionaries with player_name, stat_type, line, platform
        """
        timestamp = datetime.now(timezone.utc)
        
        for prop in props:
            player_name = prop.get('player_name')
            stat_type = prop.get('stat_type')
            line = prop.get('line')
            platform = prop.get('platform', 'prizepicks')
            
            if not all([player_name, stat_type, line]):
                continue
            
            # Create unique key
            key = f"{player_name}_{stat_type}_{platform}"
            
            # Store in history
            self.line_history[player_name][f"{stat_type}_{platform}"].append({
                'timestamp': timestamp,
                'line': float(line),
                'platform': platform
            })
            
            # Keep only last 50 entries per player/stat
            if len(self.line_history[player_name][f"{stat_type}_{platform}"]) > 50:
                self.line_history[player_name][f"{stat_type}_{platform}"] = \
                    self.line_history[player_name][f"{stat_type}_{platform}"][-50:]
            
            # Update current lines
            self.current_lines[key] = {
                'line': float(line),
                'timestamp': timestamp,
                'platform': platform
            }
        
        logger.info(f"📊 Recorded {len(props)} lines for tracking")
    
    def get_line_movement(self, player_name: str, stat_type: str, platform: str = 'prizepicks') -> Optional[Dict]:
        """
        Get line movement information for a player stat
        
        Returns:
            {
                'current_line': float,
                'previous_line': float,
                'movement': float,  # positive = line moved up
                'movement_direction': 'up'|'down'|'stable',
                'is_significant': bool,
                'history_count': int,
                'first_seen': datetime,
                'last_updated': datetime
            }
        """
        history_key = f"{stat_type}_{platform}"
        
        if player_name not in self.line_history:
            return None
        
        if history_key not in self.line_history[player_name]:
            return None
        
        history = self.line_history[player_name][history_key]
        
        if len(history) < 2:
            # Not enough history to determine movement
            if len(history) == 1:
                return {
                    'current_line': history[0]['line'],
                    'previous_line': None,
                    'movement': 0.0,
                    'movement_direction': 'new',
                    'is_significant': False,
                    'history_count': 1,
                    'first_seen': history[0]['timestamp'],
                    'last_updated': history[0]['timestamp']
                }
            return None
        
        # Get current and previous lines
        current = history[-1]
        previous = history[-2]
        
        current_line = current['line']
        previous_line = previous['line']
        movement = current_line - previous_line
        
        # Determine significance
        threshold = self.significant_movement_threshold if 'kill' in stat_type.lower() else self.significant_movement_threshold_hs
        is_significant = abs(movement) >= threshold
        
        # Determine direction
        if movement > 0.5:
            direction = 'up'
        elif movement < -0.5:
            direction = 'down'
        else:
            direction = 'stable'
        
        return {
            'current_line': current_line,
            'previous_line': previous_line,
            'movement': round(movement, 1),
            'movement_direction': direction,
            'is_significant': is_significant,
            'history_count': len(history),
            'first_seen': history[0]['timestamp'],
            'last_updated': current['timestamp']
        }
    
    def get_all_movements(self) -> Dict[str, Dict]:
        """
        Get all line movements for all players
        
        Returns:
            Dictionary of movements keyed by player_stat_platform
        """
        movements = {}
        
        for player_name, stats in self.line_history.items():
            for stat_platform_key, history in stats.items():
                # Parse stat_type and platform from key
                parts = stat_platform_key.rsplit('_', 1)
                if len(parts) == 2:
                    stat_type, platform = parts
                else:
                    stat_type = stat_platform_key
                    platform = 'prizepicks'
                
                movement = self.get_line_movement(player_name, stat_type, platform)
                if movement:
                    key = f"{player_name}_{stat_type}_{platform}"
                    movements[key] = {
                        'player_name': player_name,
                        'stat_type': stat_type,
                        'platform': platform,
                        **movement
                    }
        
        return movements
    
    def get_significant_movements(self) -> List[Dict]:
        """Get only significant line movements"""
        all_movements = self.get_all_movements()
        
        significant = [
            movement for movement in all_movements.values()
            if movement.get('is_significant', False) and movement.get('movement_direction') != 'new'
        ]
        
        # Sort by absolute movement size
        significant.sort(key=lambda x: abs(x['movement']), reverse=True)
        
        return significant
    
    def clear_old_history(self, hours: int = 24) -> None:
        """Clear line history older than specified hours"""
        cutoff = datetime.now(timezone.utc).timestamp() - (hours * 3600)
        
        for player_name in list(self.line_history.keys()):
            for stat_key in list(self.line_history[player_name].keys()):
                # Filter history
                self.line_history[player_name][stat_key] = [
                    entry for entry in self.line_history[player_name][stat_key]
                    if entry['timestamp'].timestamp() > cutoff
                ]
                
                # Remove empty stat keys
                if not self.line_history[player_name][stat_key]:
                    del self.line_history[player_name][stat_key]
            
            # Remove empty players
            if not self.line_history[player_name]:
                del self.line_history[player_name]
        
        logger.info(f"🧹 Cleaned up line history older than {hours} hours")
    
    def get_tracker_stats(self) -> Dict:
        """Get statistics about tracked lines"""
        total_players = len(self.line_history)
        total_stat_lines = sum(len(stats) for stats in self.line_history.values())
        total_history_entries = sum(
            len(history) 
            for player_stats in self.line_history.values()
            for history in player_stats.values()
        )
        
        movements = self.get_all_movements()
        significant_count = len([m for m in movements.values() if m.get('is_significant', False)])
        
        return {
            'tracked_players': total_players,
            'tracked_stat_lines': total_stat_lines,
            'total_history_entries': total_history_entries,
            'movements_detected': len(movements),
            'significant_movements': significant_count
        }
