"""
CS2 Projection Model
Generates independent player projections for kills and headshots
"""
import logging
from typing import List, Dict, Optional
from random import uniform, gauss

logger = logging.getLogger(__name__)


class CS2ProjectionModel:
    """Statistical model for projecting CS2 player performance"""
    
    def __init__(self, stats_fetcher=None):
        # Model parameters (tunable)
        self.baseline_variance = 0.10  # 10% variance from DFS baseline
        self.confidence_base = 75.0
        self.value_threshold_kills = 3.0
        self.value_threshold_headshots = 2.0
        
        # Stats fetcher for real data (optional)
        self.stats_fetcher = stats_fetcher
        
        # Team strength adjustments (mock data - can be replaced with real stats)
        self.team_ratings = self._initialize_team_ratings()
        
        # Player form factors (mock - can be replaced with recent match data)
        self.player_form = {}
    
    def _initialize_team_ratings(self) -> Dict[str, float]:
        """Initialize team strength ratings (1.0 = average, >1.0 = stronger)"""
        # Mock ratings - in production, fetch from stats API
        return {
            # Tier 1 teams
            "Navi": 1.15, "NATUS VINCERE": 1.15,
            "FaZe": 1.12, "FAZE CLAN": 1.12,
            "Vitality": 1.14, "TEAM VITALITY": 1.14,
            "G2": 1.10, "G2 ESPORTS": 1.10,
            "MOUZ": 1.08,
            
            # Tier 2 teams
            "Liquid": 1.05, "TEAM LIQUID": 1.05,
            "Heroic": 1.03,
            "Astralis": 1.02,
            "ENCE": 1.00,
            
            # Default for unknown teams
            "DEFAULT": 1.00
        }
    
    def get_team_rating(self, team_name: str) -> float:
        """Get team strength rating"""
        # Try exact match first
        if team_name in self.team_ratings:
            return self.team_ratings[team_name]
        
        # Try case-insensitive partial match
        team_upper = team_name.upper()
        for known_team, rating in self.team_ratings.items():
            if known_team.upper() in team_upper or team_upper in known_team.upper():
                return rating
        
        return self.team_ratings["DEFAULT"]
    
    def calculate_player_form(self, player_name: str) -> float:
        """
        Calculate player form multiplier based on recent performance
        Currently returns mock data - can be replaced with real recent match stats
        Returns: multiplier between 0.85 and 1.15
        """
        # Check cache
        if player_name in self.player_form:
            return self.player_form[player_name]
        
        # Generate realistic form factor (normally distributed around 1.0)
        # In production: calculate from last 5-10 matches
        form = gauss(1.0, 0.05)  # Mean 1.0, std dev 0.05
        form = max(0.85, min(1.15, form))  # Clamp between 0.85 and 1.15
        
        self.player_form[player_name] = form
        return form
    
    def calculate_opponent_adjustment(self, player_team: str, opponent_team: str) -> float:
        """
        Adjust projection based on opponent strength
        Stronger opponent = slightly lower projection
        """
        player_rating = self.get_team_rating(player_team)
        opponent_rating = self.get_team_rating(opponent_team)
        
        # Calculate relative strength
        relative_strength = player_rating / opponent_rating
        
        # Convert to adjustment multiplier (subtle effect)
        # relative_strength 1.2 -> 1.05 multiplier
        # relative_strength 0.8 -> 0.95 multiplier
        adjustment = 1.0 + (relative_strength - 1.0) * 0.25
        
        return adjustment
    
    def generate_projection(
        self,
        player_name: str,
        team: str,
        opponent_team: str,
        stat_type: str,
        dfs_lines: List[Dict]
    ) -> Dict:
        """
        Generate independent projection for a player stat
        
        Args:
            player_name: Player name
            team: Player's team
            opponent_team: Opposing team
            stat_type: 'kills' or 'headshots'
            dfs_lines: List of DFS lines from PrizePicks/Underdog
        
        Returns:
            Dict with projection value, confidence, and value opportunity flag
        """
        
        # Use DFS lines as baseline (average if multiple sources)
        if not dfs_lines:
            return None
        
        baseline = sum([line['line'] for line in dfs_lines]) / len(dfs_lines)
        
        # Apply model factors
        form_multiplier = self.calculate_player_form(player_name)
        opponent_adjustment = self.calculate_opponent_adjustment(team, opponent_team)
        
        # Add some variance for more realistic projections
        variance = gauss(0, self.baseline_variance)
        
        # Calculate projection
        projection = baseline * form_multiplier * opponent_adjustment * (1 + variance)
        projection = round(projection, 1)
        
        # Calculate confidence (higher when we're close to consensus)
        # Lower when we disagree significantly with DFS lines
        diff_from_baseline = abs(projection - baseline)
        threshold = self.value_threshold_kills if stat_type == 'kills' else self.value_threshold_headshots
        
        confidence = self.confidence_base - (diff_from_baseline / threshold) * 10
        confidence = max(60.0, min(95.0, confidence))
        confidence = round(confidence, 1)
        
        # Determine value opportunity
        difference = projection - baseline
        value_opportunity = abs(difference) >= threshold
        
        return {
            'projected_value': projection,
            'confidence': confidence,
            'difference': round(difference, 1),
            'value_opportunity': value_opportunity,
            'baseline': baseline,
            'form_factor': form_multiplier,
            'opponent_factor': opponent_adjustment
        }
    
    def generate_match_projections(
        self,
        match_id: str,
        team1: str,
        team2: str,
        player_props: List[Dict]
    ) -> List[Dict]:
        """
        Generate projections for all players in a match
        
        Args:
            match_id: Match ID
            team1: First team name
            team2: Second team name
            player_props: List of player props with DFS lines
        
        Returns:
            List of enhanced projections
        """
        projections = []
        
        for prop in player_props:
            player_name = prop['player_name']
            player_team = prop['team']
            stat_type = prop['stat_type']
            dfs_lines = prop.get('dfs_lines', [])
            
            # Determine opponent team
            opponent_team = team2 if player_team == team1 else team1
            
            # Generate projection
            projection_data = self.generate_projection(
                player_name=player_name,
                team=player_team,
                opponent_team=opponent_team,
                stat_type=stat_type,
                dfs_lines=dfs_lines
            )
            
            if projection_data:
                # Create enhanced projection object
                enhanced_proj = {
                    'match_id': match_id,
                    'player_name': player_name,
                    'team': player_team,
                    'stat_type': stat_type,
                    'projected_value': projection_data['projected_value'],
                    'confidence': projection_data['confidence'],
                    'dfs_lines': dfs_lines,
                    'value_opportunity': projection_data['value_opportunity'],
                    'difference': projection_data['difference']
                }
                
                projections.append(enhanced_proj)
        
        return projections
    
    def get_model_info(self) -> Dict:
        """Return model configuration and stats"""
        return {
            'model_version': '1.0',
            'model_type': 'hybrid_statistical',
            'baseline_variance': self.baseline_variance,
            'confidence_base': self.confidence_base,
            'value_thresholds': {
                'kills': self.value_threshold_kills,
                'headshots': self.value_threshold_headshots
            },
            'team_ratings_count': len(self.team_ratings),
            'features': [
                'DFS baseline integration',
                'Player form adjustment',
                'Opponent strength adjustment',
                'Confidence scoring',
                'Value opportunity detection'
            ],
            'data_source': 'mock_historical_data',
            'ready_for_real_data': True
        }
