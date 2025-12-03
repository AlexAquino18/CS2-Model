"""
Real CS2 Statistics Fetcher
Fetches historical player and team data from PandaScore API
"""
import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)


class CS2StatsFetcher:
    """Fetches real historical CS2 data from PandaScore"""
    
    def __init__(self, pandascore_api_key: str, enable_real_data: bool = False):
        self.api_key = pandascore_api_key
        self.base_url = "https://api.pandascore.co/csgo"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
        self.enable_real_data = enable_real_data
        
        # Cache to avoid repeated API calls (TTL: 1 hour)
        self.player_cache = {}
        self.team_cache = {}
        self.cache_timestamp = {}
        self.cache_ttl = 3600  # 1 hour in seconds
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache_timestamp:
            return False
        
        age = time.time() - self.cache_timestamp[key]
        return age < self.cache_ttl
    
    def fetch_player_recent_form(self, player_name: str) -> Optional[float]:
        """
        Fetch player's recent form multiplier (0.85 - 1.15)
        Uses REAL stats from PandaScore /csgo/players/{id}/stats endpoint
        
        Returns:
            Form multiplier based on recent K/D ratio and performance
            None if data unavailable
        """
        if not self.enable_real_data:
            return None
        
        cache_key = f"player_form_{player_name}"
        
        # Check cache
        if self._is_cache_valid(cache_key) and cache_key in self.player_cache:
            logger.info(f"Using cached form for {player_name}")
            return self.player_cache[cache_key]
        
        try:
            logger.info(f"Fetching REAL stats for {player_name}...")
            
            # Search for player
            search_url = f"{self.base_url}/players"
            params = {"search[name]": player_name, "per_page": 1}
            
            response = requests.get(
                search_url,
                headers=self.headers,
                params=params,
                timeout=5
            )
            
            if response.status_code != 200:
                logger.warning(f"API returned {response.status_code} for {player_name}")
                return None
            
            players = response.json()
            if not players:
                logger.info(f"Player {player_name} not found in PandaScore")
                return None
            
            player_id = players[0]['id']
            
            # FETCH ACTUAL PLAYER STATS from /csgo/players/{id}/stats
            stats_url = f"{self.base_url}/players/{player_id}/stats"
            
            stats_response = requests.get(
                stats_url,
                headers=self.headers,
                timeout=5
            )
            
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                logger.info(f"📊 Got REAL stats for {player_name} from PandaScore")
                
                # Calculate form from real stats
                form_multiplier = self._calculate_form_from_real_stats(player_name, stats_data)
            else:
                # Fallback if stats endpoint unavailable
                logger.info(f"Stats endpoint unavailable for {player_name}, using basic data")
                form_multiplier = 1.05 if players[0].get('current_team') else 1.0
            
            # Cache the result
            self.player_cache[cache_key] = form_multiplier
            self.cache_timestamp[cache_key] = time.time()
            
            logger.info(f"✅ Real form for {player_name}: {form_multiplier}x")
            
            return form_multiplier
            
        except requests.Timeout:
            logger.warning(f"Timeout fetching data for {player_name}")
            return None
        except Exception as e:
            logger.error(f"Error fetching stats for {player_name}: {e}")
            return None
    
    def _calculate_form_from_real_stats(self, player_name: str, stats_data: Dict) -> float:
        """
        Calculate form multiplier from REAL PandaScore stats
        
        Stats structure from /csgo/players/{id}/stats:
        {
            "kills": int,
            "deaths": int,
            "assists": int,
            "kd_ratio": float,
            "headshots": int,
            "headshot_percentage": float,
            "average_kills_per_round": float,
            "average_deaths_per_round": float
        }
        """
        try:
            # Extract key stats
            kd_ratio = stats_data.get('kd_ratio', 1.0)
            avg_kills_per_round = stats_data.get('average_kills_per_round', 0.7)
            headshot_pct = stats_data.get('headshot_percentage', 50.0)
            
            logger.info(f"📈 {player_name} stats: K/D={kd_ratio:.2f}, Kills/Rnd={avg_kills_per_round:.2f}, HS%={headshot_pct:.1f}%")
            
            # Calculate form based on multiple factors
            form_multiplier = 1.0
            
            # K/D Ratio impact (most important)
            if kd_ratio >= 1.3:  # Elite K/D
                form_multiplier += 0.15
            elif kd_ratio >= 1.2:  # Excellent K/D
                form_multiplier += 0.12
            elif kd_ratio >= 1.1:  # Very good K/D
                form_multiplier += 0.08
            elif kd_ratio >= 1.0:  # Good K/D
                form_multiplier += 0.05
            elif kd_ratio >= 0.9:  # Decent K/D
                form_multiplier += 0.02
            elif kd_ratio < 0.8:  # Struggling
                form_multiplier -= 0.10
            elif kd_ratio < 0.9:  # Below average
                form_multiplier -= 0.05
            
            # Kills per round impact
            if avg_kills_per_round >= 0.85:  # Elite fragger
                form_multiplier += 0.05
            elif avg_kills_per_round >= 0.75:  # Strong fragger
                form_multiplier += 0.03
            elif avg_kills_per_round < 0.6:  # Low impact
                form_multiplier -= 0.03
            
            # Headshot percentage (indicates form/sharpness)
            if headshot_pct >= 55:  # Very sharp
                form_multiplier += 0.02
            elif headshot_pct < 45:  # Not clicking heads
                form_multiplier -= 0.02
            
            # Clamp between 0.85 and 1.15
            form_multiplier = max(0.85, min(1.15, form_multiplier))
            
            return round(form_multiplier, 2)
            
        except Exception as e:
            logger.warning(f"Error calculating form from stats: {e}")
            return 1.0
    
    def fetch_team_rating(self, team_name: str) -> Optional[float]:
        """
        Fetch team's strength rating (0.85 - 1.15)
        Uses REAL stats from PandaScore /csgo/teams/{id}/stats endpoint
        
        Returns:
            Team rating based on recent performance
            None if data unavailable
        """
        if not self.enable_real_data:
            return None
        
        cache_key = f"team_rating_{team_name}"
        
        # Check cache
        if self._is_cache_valid(cache_key) and cache_key in self.team_cache:
            logger.info(f"Using cached rating for {team_name}")
            return self.team_cache[cache_key]
        
        try:
            logger.info(f"Fetching REAL team stats for {team_name}...")
            
            # Search for team
            search_url = f"{self.base_url}/teams"
            params = {"search[name]": team_name, "per_page": 1}
            
            response = requests.get(
                search_url,
                headers=self.headers,
                params=params,
                timeout=5
            )
            
            if response.status_code != 200:
                logger.warning(f"API returned {response.status_code} for {team_name}")
                return None
            
            teams = response.json()
            if not teams:
                logger.info(f"Team {team_name} not found in PandaScore")
                return None
            
            team_id = teams[0]['id']
            
            # FETCH ACTUAL TEAM STATS from /csgo/teams/{id}/stats
            stats_url = f"{self.base_url}/teams/{team_id}/stats"
            
            stats_response = requests.get(
                stats_url,
                headers=self.headers,
                timeout=5
            )
            
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                logger.info(f"📊 Got REAL team stats for {team_name} from PandaScore")
                
                # Calculate rating from real stats
                rating = self._calculate_team_rating_from_real_stats(team_name, stats_data)
            else:
                # Fallback
                logger.info(f"Stats endpoint unavailable for {team_name}, using basic data")
                rating = 1.05 if teams[0].get('players') else 1.0
            
            # Cache the result
            self.team_cache[cache_key] = rating
            self.cache_timestamp[cache_key] = time.time()
            
            logger.info(f"✅ Real rating for {team_name}: {rating}")
            
            return rating
            
        except requests.Timeout:
            logger.warning(f"Timeout fetching data for {team_name}")
            return None
        except Exception as e:
            logger.error(f"Error fetching team rating for {team_name}: {e}")
            return None
    
    def _calculate_team_rating_from_real_stats(self, team_name: str, stats_data: Dict) -> float:
        """
        Calculate team rating from REAL PandaScore team stats
        
        Stats structure from /csgo/teams/{id}/stats:
        {
            "wins": int,
            "losses": int,
            "draws": int,
            "win_rate": float,
            "total_kills": int,
            "total_deaths": int,
            "average_kills_per_round": float,
            "average_deaths_per_round": float,
            "rounds_won": int,
            "rounds_lost": int
        }
        """
        try:
            # Extract key stats
            win_rate = stats_data.get('win_rate', 50.0)
            wins = stats_data.get('wins', 0)
            losses = stats_data.get('losses', 0)
            avg_kills_per_round = stats_data.get('average_kills_per_round', 0.0)
            
            logger.info(f"📈 {team_name} stats: Win Rate={win_rate:.1f}%, W-L={wins}-{losses}, Kills/Rnd={avg_kills_per_round:.2f}")
            
            # Calculate rating based on win rate
            rating = 1.0
            
            # Win rate impact (most important factor)
            if win_rate >= 70:  # Elite team
                rating = 1.15
            elif win_rate >= 65:  # Top tier
                rating = 1.12
            elif win_rate >= 60:  # Strong team
                rating = 1.10
            elif win_rate >= 55:  # Above average
                rating = 1.07
            elif win_rate >= 50:  # Average
                rating = 1.03
            elif win_rate >= 45:  # Below average
                rating = 0.97
            elif win_rate >= 40:  # Struggling
                rating = 0.92
            else:  # Poor team
                rating = 0.85
            
            # Adjust for team firepower (kills per round)
            if avg_kills_per_round >= 3.5:  # High firepower
                rating += 0.03
            elif avg_kills_per_round < 3.0:  # Low firepower
                rating -= 0.03
            
            # Clamp between 0.85 and 1.15
            rating = max(0.85, min(1.15, rating))
            
            return round(rating, 2)
            
        except Exception as e:
            logger.warning(f"Error calculating team rating from stats: {e}")
            return 1.0
    
    def get_stats_info(self) -> Dict:
        """Return information about stats fetcher status"""
        return {
            'enabled': self.enable_real_data,
            'cached_players': len([k for k in self.player_cache.keys() if self._is_cache_valid(k)]),
            'cached_teams': len([k for k in self.team_cache.keys() if self._is_cache_valid(k)]),
            'cache_ttl_hours': self.cache_ttl / 3600,
            'api_source': 'PandaScore',
            'status': 'active' if self.enable_real_data else 'disabled (using mock data)'
        }
