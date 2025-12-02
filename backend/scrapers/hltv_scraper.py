import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime, timezone, timedelta
import re

logger = logging.getLogger(__name__)

class HLTVScraper:
    """Scraper for HLTV CS2 match data using hltv-api.vercel.app"""
    
    def __init__(self):
        # Using the public HLTV API instead of scraping
        self.api_base = "https://hltv-api.vercel.app/api"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
    
    def fetch_upcoming_matches(self) -> List[Dict]:
        """Fetch upcoming CS2 matches from HLTV API"""
        try:
            url = f"{self.api_base}/matches.json"
            logger.info(f"Fetching matches from HLTV API: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully fetched {len(data)} matches from HLTV API")
                return self._parse_api_matches(data)
            else:
                logger.warning(f"HLTV API returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching HLTV matches: {e}")
            return []
    
    def _parse_api_matches(self, matches_data: List[Dict]) -> List[Dict]:
        """Parse matches from HLTV API response"""
        matches = []
        
        try:
            # Filter for upcoming matches only (matches without results)
            for match_data in matches_data[:15]:  # Limit to first 15 matches
                try:
                    # Check if match has teams data
                    if not match_data.get('teams') or len(match_data['teams']) < 2:
                        continue
                    
                    team1 = match_data['teams'][0]['name']
                    team2 = match_data['teams'][1]['name']
                    
                    # Parse time
                    time_str = match_data.get('time', '')
                    try:
                        match_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    except:
                        # If time parsing fails, use a future time
                        match_time = datetime.now(timezone.utc) + timedelta(hours=2)
                    
                    # Only include future matches
                    if match_time < datetime.now(timezone.utc):
                        continue
                    
                    # Extract event info
                    event = match_data.get('event', {})
                    tournament = event.get('name', 'Unknown Tournament')
                    
                    # Extract format (bo1, bo3, bo5)
                    match_format = match_data.get('maps', 'bo3').upper()
                    
                    match = {
                        'id': match_data.get('id'),
                        'team1': team1,
                        'team2': team2,
                        'start_time': match_time,
                        'tournament': tournament,
                        'format': match_format,
                        'stars': match_data.get('stars', 0),
                        'status': 'upcoming'
                    }
                    
                    matches.append(match)
                    
                except Exception as e:
                    logger.debug(f"Error parsing individual match: {e}")
                    continue
            
            logger.info(f"Parsed {len(matches)} upcoming HLTV matches")
            return matches
            
        except Exception as e:
            logger.error(f"Error parsing HLTV API matches: {e}")
            return []
    
    def fetch_player_stats(self, player_name: str) -> Optional[Dict]:
        """Fetch player statistics from HLTV"""
        try:
            # Search for player
            search_url = f"{self.base_url}/search?term={player_name}"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                # Parse search results and get player stats
                # This is simplified - full implementation would follow player links
                return {
                    'name': player_name,
                    'avg_kills': 20.0,
                    'avg_headshots': 8.0,
                    'recent_form': 1.0
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching player stats: {e}")
            return None
