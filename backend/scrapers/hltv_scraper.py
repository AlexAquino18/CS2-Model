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
    
    def _parse_matches(self, html: str) -> List[Dict]:
        """Parse matches from HLTV HTML"""
        matches = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find upcoming match containers
            match_containers = soup.find_all('div', class_='upcomingMatch')
            
            for container in match_containers[:10]:  # Limit to first 10 matches
                try:
                    match_data = self._extract_match_data(container)
                    if match_data:
                        matches.append(match_data)
                except Exception as e:
                    logger.debug(f"Error parsing individual match: {e}")
                    continue
            
            logger.info(f"Parsed {len(matches)} HLTV matches")
            return matches
            
        except Exception as e:
            logger.error(f"Error parsing HLTV HTML: {e}")
            return []
    
    def _extract_match_data(self, container) -> Optional[Dict]:
        """Extract match data from a match container"""
        try:
            # Extract team names
            teams = container.find_all('div', class_='teamName')
            if len(teams) < 2:
                return None
            
            team1 = teams[0].text.strip()
            team2 = teams[1].text.strip()
            
            # Extract match time
            time_elem = container.find('div', class_='matchTime')
            match_time = self._parse_match_time(time_elem.text if time_elem else '')
            
            # Extract event name
            event_elem = container.find('div', class_='matchEvent')
            tournament = event_elem.text.strip() if event_elem else 'Unknown Tournament'
            
            # Extract match format (BO1, BO3, etc.)
            format_elem = container.find('div', class_='bestOf')
            match_format = format_elem.text.strip() if format_elem else 'BO3'
            
            return {
                'team1': team1,
                'team2': team2,
                'start_time': match_time,
                'tournament': tournament,
                'format': match_format,
                'status': 'upcoming'
            }
            
        except Exception as e:
            logger.debug(f"Error extracting match data: {e}")
            return None
    
    def _parse_match_time(self, time_str: str) -> datetime:
        """Parse match time string to datetime"""
        # This is simplified - HLTV times can be complex
        # For now, return a future time
        from datetime import timedelta
        return datetime.now(timezone.utc) + timedelta(hours=2)
    
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
