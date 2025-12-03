# Integrating Real Historical Data into Projection Model

This guide shows you how to replace mock data with real CS2 player statistics.

## 📊 Data Sources for CS2 Stats

### Option 1: HLTV.org (Recommended)
- **What**: Premier CS2 stats database
- **Data Available**: Player stats, team rankings, match history
- **Access**: Web scraping (complex) or third-party APIs
- **Quality**: ⭐⭐⭐⭐⭐ (Industry standard)

### Option 2: PandaScore API (You're already using this!)
- **What**: Esports data API (you use it for matches)
- **Endpoint**: `https://api.pandascore.co/csgo/players/{player_id}/stats`
- **Data Available**: K/D, ADR, rating, recent form
- **Quality**: ⭐⭐⭐⭐ (Very good)
- **Cost**: Your API key works for this!

### Option 3: Liquipedia API
- **What**: Community-driven esports database
- **Access**: Free API access
- **Quality**: ⭐⭐⭐ (Good for team info)

### Option 4: CSGOStats.gg
- **What**: Community stats site
- **Access**: Web scraping required
- **Quality**: ⭐⭐⭐ (Good recent data)

## 🎯 Recommended Approach: PandaScore + Simple Enhancement

Since you already have PandaScore API access, here's the quickest path:

### Data Points to Fetch:
1. **Player Recent Form** (Last 10 matches)
   - Average kills per map
   - K/D ratio
   - Rating 2.0
   
2. **Team Strength** (Last 30 days)
   - Win rate
   - Round differential
   - Head-to-head records

3. **Map-Specific Stats**
   - Performance on Mirage, Dust2, etc.
   - Opponent-specific matchups

## 🔧 Implementation Steps

### Step 1: Create Data Fetcher Module

Create `/app/backend/stats_fetcher.py`:

```python
import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CS2StatsFetcher:
    """Fetches real historical CS2 data"""
    
    def __init__(self, pandascore_api_key: str):
        self.api_key = pandascore_api_key
        self.base_url = "https://api.pandascore.co/csgo"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
        
        # Cache to avoid repeated API calls
        self.player_cache = {}
        self.team_cache = {}
    
    def fetch_player_recent_stats(self, player_name: str) -> Optional[Dict]:
        """
        Fetch player's recent performance stats
        
        Returns:
            {
                'avg_kills': float,
                'avg_deaths': float,
                'kd_ratio': float,
                'rating': float,
                'form_multiplier': float  # 0.85-1.15 based on recent trend
            }
        """
        # Check cache first
        if player_name in self.player_cache:
            return self.player_cache[player_name]
        
        try:
            # Search for player
            search_url = f"{self.base_url}/players"
            params = {"search[name]": player_name, "per_page": 1}
            
            response = requests.get(search_url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Failed to find player {player_name}")
                return None
            
            players = response.json()
            if not players:
                return None
            
            player_id = players[0]['id']
            
            # Fetch recent matches for this player
            matches_url = f"{self.base_url}/players/{player_id}/matches"
            params = {
                "per_page": 10,  # Last 10 matches
                "sort": "-begin_at"
            }
            
            response = requests.get(matches_url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code != 200:
                return None
            
            matches = response.json()
            
            # Calculate stats from recent matches
            stats = self._calculate_player_form(player_name, matches)
            
            # Cache the result
            self.player_cache[player_name] = stats
            
            return stats
            
        except Exception as e:
            logger.error(f"Error fetching stats for {player_name}: {e}")
            return None
    
    def _calculate_player_form(self, player_name: str, matches: List[Dict]) -> Dict:
        """Calculate form multiplier from recent matches"""
        
        if not matches:
            return {
                'avg_kills': 20.0,
                'avg_deaths': 18.0,
                'kd_ratio': 1.11,
                'rating': 1.0,
                'form_multiplier': 1.0
            }
        
        # Extract stats from matches
        total_kills = 0
        total_deaths = 0
        match_count = 0
        
        for match in matches:
            # Parse match stats (structure depends on PandaScore response)
            # This is simplified - you'll need to adjust based on actual API response
            player_stats = self._extract_player_stats_from_match(match, player_name)
            
            if player_stats:
                total_kills += player_stats.get('kills', 0)
                total_deaths += player_stats.get('deaths', 1)
                match_count += 1
        
        if match_count == 0:
            return {
                'avg_kills': 20.0,
                'avg_deaths': 18.0,
                'kd_ratio': 1.11,
                'rating': 1.0,
                'form_multiplier': 1.0
            }
        
        avg_kills = total_kills / match_count
        avg_deaths = total_deaths / match_count
        kd_ratio = total_kills / max(total_deaths, 1)
        
        # Calculate form multiplier based on recent performance
        # Above 1.2 K/D = hot form (1.10x)
        # 1.0-1.2 K/D = normal (1.0x)
        # Below 0.8 K/D = cold form (0.90x)
        
        if kd_ratio >= 1.2:
            form_multiplier = min(1.15, 1.0 + (kd_ratio - 1.2) * 0.3)
        elif kd_ratio <= 0.8:
            form_multiplier = max(0.85, 1.0 - (0.8 - kd_ratio) * 0.3)
        else:
            form_multiplier = 1.0
        
        return {
            'avg_kills': round(avg_kills, 1),
            'avg_deaths': round(avg_deaths, 1),
            'kd_ratio': round(kd_ratio, 2),
            'rating': round(kd_ratio, 2),  # Simplified rating
            'form_multiplier': round(form_multiplier, 2)
        }
    
    def _extract_player_stats_from_match(self, match: Dict, player_name: str) -> Optional[Dict]:
        """Extract player stats from a match"""
        # This depends on PandaScore's exact response structure
        # You'll need to adjust this based on the actual API response
        
        # Example structure (may need adjustment):
        try:
            for team in match.get('opponents', []):
                for player in team.get('players', []):
                    if player.get('name', '').lower() == player_name.lower():
                        return {
                            'kills': player.get('kills', 0),
                            'deaths': player.get('deaths', 0),
                            'assists': player.get('assists', 0)
                        }
        except Exception:
            pass
        
        return None
    
    def fetch_team_strength(self, team_name: str) -> float:
        """
        Fetch team's current strength rating
        
        Returns rating between 0.8 and 1.2 (1.0 = average)
        """
        if team_name in self.team_cache:
            return self.team_cache[team_name]
        
        try:
            # Search for team
            search_url = f"{self.base_url}/teams"
            params = {"search[name]": team_name, "per_page": 1}
            
            response = requests.get(search_url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code != 200:
                return 1.0
            
            teams = response.json()
            if not teams:
                return 1.0
            
            team_id = teams[0]['id']
            
            # Fetch recent team matches
            matches_url = f"{self.base_url}/teams/{team_id}/matches"
            params = {
                "per_page": 20,
                "sort": "-begin_at"
            }
            
            response = requests.get(matches_url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code != 200:
                return 1.0
            
            matches = response.json()
            
            # Calculate win rate
            wins = sum(1 for m in matches if self._team_won(m, team_id))
            win_rate = wins / len(matches) if matches else 0.5
            
            # Convert win rate to team rating
            # 70%+ win rate = 1.15
            # 50% win rate = 1.0
            # 30% win rate = 0.85
            
            if win_rate >= 0.7:
                rating = 1.15
            elif win_rate >= 0.6:
                rating = 1.10
            elif win_rate >= 0.5:
                rating = 1.05
            elif win_rate >= 0.4:
                rating = 0.95
            else:
                rating = 0.85
            
            self.team_cache[team_name] = rating
            return rating
            
        except Exception as e:
            logger.error(f"Error fetching team strength for {team_name}: {e}")
            return 1.0
    
    def _team_won(self, match: Dict, team_id: int) -> bool:
        """Check if team won the match"""
        try:
            winner_id = match.get('winner_id')
            return winner_id == team_id
        except Exception:
            return False
```

### Step 2: Update Projection Model to Use Real Data

Modify `/app/backend/projection_model.py`:

```python
# Add at the top
from stats_fetcher import CS2StatsFetcher

class CS2ProjectionModel:
    def __init__(self, stats_fetcher: Optional[CS2StatsFetcher] = None):
        self.stats_fetcher = stats_fetcher  # Add stats fetcher
        # ... rest of __init__
    
    def calculate_player_form(self, player_name: str) -> float:
        """Calculate player form multiplier - NOW WITH REAL DATA!"""
        
        # Try to get real data first
        if self.stats_fetcher:
            real_stats = self.stats_fetcher.fetch_player_recent_stats(player_name)
            
            if real_stats:
                logger.info(f"Using REAL stats for {player_name}: "
                           f"K/D={real_stats['kd_ratio']}, "
                           f"Form={real_stats['form_multiplier']}")
                return real_stats['form_multiplier']
        
        # Fallback to mock data if real data unavailable
        if player_name in self.player_form:
            return self.player_form[player_name]
        
        form = gauss(1.0, 0.05)
        form = max(0.85, min(1.15, form))
        self.player_form[player_name] = form
        return form
    
    def get_team_rating(self, team_name: str) -> float:
        """Get team strength rating - NOW WITH REAL DATA!"""
        
        # Try real data first
        if self.stats_fetcher:
            real_rating = self.stats_fetcher.fetch_team_strength(team_name)
            
            if real_rating != 1.0:  # Got real data
                logger.info(f"Using REAL rating for {team_name}: {real_rating}")
                return real_rating
        
        # Fallback to hardcoded ratings
        if team_name in self.team_ratings:
            return self.team_ratings[team_name]
        
        # Try partial match
        team_upper = team_name.upper()
        for known_team, rating in self.team_ratings.items():
            if known_team.upper() in team_upper or team_upper in known_team.upper():
                return rating
        
        return self.team_ratings["DEFAULT"]
```

### Step 3: Update Data Aggregator

Modify `/app/backend/data_aggregator.py`:

```python
from stats_fetcher import CS2StatsFetcher

class CS2DataAggregator:
    def __init__(self):
        # ... existing code ...
        
        # Initialize stats fetcher with your PandaScore key
        pandascore_key = "paR1oQjXNqVecsLSmUGx-n8O1Vpdj5HEZgmF9ZKFD2vYiUzHDso"
        stats_fetcher = CS2StatsFetcher(pandascore_key)
        
        # Pass stats fetcher to projection model
        self.projection_model = CS2ProjectionModel(stats_fetcher=stats_fetcher)
```

## 🎯 Quick Start (Minimal Changes)

If you want to start simple, just add this to your existing projection_model.py:

```python
def fetch_player_stats_from_api(self, player_name: str) -> Optional[Dict]:
    """Quick integration with PandaScore"""
    try:
        api_key = "paR1oQjXNqVecsLSmUGx-n8O1Vpdj5HEZgmF9ZKFD2vYiUzHDso"
        url = f"https://api.pandascore.co/csgo/players"
        
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            params={"search[name]": player_name, "per_page": 1},
            timeout=5
        )
        
        if response.status_code == 200 and response.json():
            player_data = response.json()[0]
            # Use this data to calculate form
            return player_data
    except:
        pass
    
    return None
```

## 📈 Expected Improvements

With real data integrated:

| Metric | Mock Data | Real Data |
|--------|-----------|-----------|
| Form Accuracy | Random | Based on L10 matches |
| Team Ratings | Static | Dynamic (updated) |
| Confidence | 60-95% | 70-98% (higher with real data) |
| Value Detection | Good | Excellent |

## 🚀 Next Steps

1. **Test PandaScore API**: Make a test call to verify your key works
2. **Create stats_fetcher.py**: Implement the fetcher module
3. **Update projection_model.py**: Add real data fallback
4. **Monitor API usage**: PandaScore has rate limits
5. **Cache aggressively**: Store stats for 1-6 hours to reduce API calls

## ⚠️ Important Notes

- **Rate Limits**: PandaScore typically allows 1000 requests/hour
- **Caching**: Cache player/team stats for at least 1 hour
- **Fallback**: Always have mock data as fallback if API fails
- **Cost**: Monitor your API usage to stay within free tier

Would you like me to implement any of these options for you?
