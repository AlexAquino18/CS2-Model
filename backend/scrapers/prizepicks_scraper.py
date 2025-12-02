import requests
import logging
import json
from typing import List, Dict, Optional
import time

logger = logging.getLogger(__name__)

class PrizePicksScraper:
    """Scraper for PrizePicks CS2 props - Using dannyphantomSS/prizepickAPI approach"""
    
    def __init__(self):
        self.base_url = "https://api.prizepicks.com"
        # Simpler headers that work (from GitHub repo)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        })
    
    def fetch_cs2_props(self) -> List[Dict]:
        """Fetch CS2 projections from PrizePicks API - GitHub dannyphantomSS approach"""
        try:
            # Get all available leagues
            leagues = self._get_all_leagues()
            
            # Look for CS2/CSGO/Counter-Strike
            cs2_league_id = None
            for name, league_id in leagues.items():
                if any(term in name.upper() for term in ['CS2', 'CS:2', 'COUNTER-STRIKE', 'CSGO', 'COUNTER STRIKE']):
                    cs2_league_id = league_id
                    logger.info(f"Found CS2 league: {name} (ID: {league_id})")
                    break
            
            if cs2_league_id:
                props = self._fetch_league_props(cs2_league_id, "CS2")
                if props:
                    logger.info(f"Successfully fetched {len(props)} CS2 props")
                    return props
            
            logger.warning("No CS2 league found or no props available")
            return []
                
        except Exception as e:
            logger.error(f"Error fetching PrizePicks data: {e}")
            return []
    
    def _discover_cs2_league_id(self) -> Optional[int]:
        """Discover CS2 league ID by fetching leagues endpoint using HTTP/2"""
        try:
            leagues_url = "https://api.prizepicks.com/leagues"
            
            # Use httpx with HTTP/2 support
            with httpx.Client(http2=True, timeout=15) as client:
                response = client.get(leagues_url, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Successfully fetched leagues list")
                    
                    if 'data' in data:
                        for league in data['data']:
                            name = league.get('attributes', {}).get('name', '').lower()
                            league_id = league.get('id')
                            
                            logger.debug(f"Found league: {name} (ID: {league_id})")
                            
                            # Look for CS2, CSGO, or Counter-Strike
                            if any(term in name for term in ['cs2', 'cs:2', 'counter-strike 2', 'csgo', 'counter strike']):
                                logger.info(f"Found CS2/CSGO league: {name} (ID: {league_id})")
                                return int(league_id)
                else:
                    logger.warning(f"Leagues API returned status {response.status_code}")
            
            logger.info("CS2 league not found in leagues list")
            return None
            
        except Exception as e:
            logger.error(f"Error discovering CS2 league ID: {e}")
            return None
    
    def _fetch_league_props(self, league_id: int) -> List[Dict]:
        """Fetch props for a specific league using correct API format with HTTP/2"""
        try:
            # Use the exact format from StackOverflow
            url = f"{self.base_url}?league_id={league_id}&per_page=250&single_stat=true&game_mode=pickem"
            
            logger.info(f"Fetching props from: {url}")
            
            # Use httpx with HTTP/2 support
            with httpx.Client(http2=True, timeout=15) as client:
                response = client.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Successfully fetched projections for league {league_id}")
                    return self._parse_projections(data)
                else:
                    logger.warning(f"PrizePicks API returned status {response.status_code} for league {league_id}")
                    return []
                
        except Exception as e:
            logger.error(f"Error fetching league {league_id} props: {e}")
            return []
    
    def _fetch_all_props(self) -> List[Dict]:
        """Fetch all props without league filter using HTTP/2"""
        try:
            url = f"{self.base_url}?per_page=250&single_stat=true&game_mode=pickem"
            
            # Use httpx with HTTP/2 support
            with httpx.Client(http2=True, timeout=15) as client:
                response = client.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info("Successfully fetched all projections")
                    return self._parse_projections(data)
                else:
                    logger.warning(f"PrizePicks API returned status {response.status_code}")
                    return []
                
        except Exception as e:
            logger.error(f"Error fetching all props: {e}")
            return []
    
    def _is_cs2_prop(self, prop: Dict) -> bool:
        """Check if a prop is for CS2"""
        game_info = prop.get('game_info', '').lower()
        player_name = prop.get('player_name', '').lower()
        
        # Check for CS2/CSGO indicators
        cs2_indicators = ['cs2', 'cs:2', 'counter-strike', 'csgo', 'mirage', 'dust2', 'inferno', 'nuke']
        return any(indicator in game_info or indicator in player_name for indicator in cs2_indicators)
    
    def _parse_projections(self, data: Dict) -> List[Dict]:
        """Parse projections from API response - improved parsing"""
        projections = []
        
        try:
            if 'data' not in data:
                logger.warning("No 'data' field in API response")
                return []
            
            # Also parse included data for additional context
            included_data = {}
            if 'included' in data:
                for item in data['included']:
                    item_type = item.get('type')
                    item_id = item.get('id')
                    if item_type and item_id:
                        if item_type not in included_data:
                            included_data[item_type] = {}
                        included_data[item_type][item_id] = item.get('attributes', {})
            
            for item in data['data']:
                if item.get('type') == 'projection':
                    attrs = item.get('attributes', {})
                    relationships = item.get('relationships', {})
                    
                    # Extract player name - try multiple fields
                    player_name = attrs.get('name', '')
                    if not player_name:
                        # Try to get from description
                        desc = attrs.get('description', '')
                        if desc:
                            # Usually format is "Player Name - Stat Type"
                            parts = desc.split(' - ')
                            if len(parts) > 0:
                                player_name = parts[0].strip()
                    
                    # Get stat type
                    stat_type = attrs.get('stat_type', '')
                    
                    # Get line score
                    line_score = attrs.get('line_score')
                    if line_score:
                        try:
                            line = float(line_score)
                        except (ValueError, TypeError):
                            continue
                    else:
                        continue
                    
                    # Get additional context
                    game_info = attrs.get('description', '')
                    start_time = attrs.get('start_time', '')
                    
                    # Try to get league/game info from relationships
                    league_id = relationships.get('league', {}).get('data', {}).get('id')
                    new_player_id = relationships.get('new_player', {}).get('data', {}).get('id')
                    
                    # Build projection object
                    projection = {
                        'player_name': player_name,
                        'stat_type': self._normalize_stat_type(stat_type),
                        'line': line,
                        'game_info': game_info,
                        'start_time': start_time,
                        'league_id': league_id,
                        'player_id': new_player_id
                    }
                    
                    if player_name and line > 0:
                        projections.append(projection)
            
            logger.info(f"Parsed {len(projections)} PrizePicks projections")
            return projections
            
        except Exception as e:
            logger.error(f"Error parsing projections: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def _normalize_stat_type(self, stat_type: str) -> str:
        """Normalize stat type to our format"""
        stat_type_lower = stat_type.lower()
        
        if 'kill' in stat_type_lower:
            return 'kills'
        elif 'headshot' in stat_type_lower or 'hs' in stat_type_lower:
            return 'headshots'
        else:
            return stat_type_lower
    
    def _scrape_with_selenium(self) -> List[Dict]:
        """Selenium-based scraping for PrizePicks"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                driver.get("https://app.prizepicks.com/")
                
                # Wait for page to load and look for CS2/Counter-Strike content
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Look for CS2 or Counter-Strike elements
                # This is a basic implementation - would need to be refined based on actual site structure
                projections = []
                
                # Try to find CS2 related content
                cs2_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'CS2') or contains(text(), 'Counter-Strike')]")
                
                if cs2_elements:
                    logger.info(f"Found {len(cs2_elements)} CS2-related elements")
                    # Parse the elements to extract projection data
                    # This would need more specific implementation based on site structure
                
                return projections
                
            finally:
                driver.quit()
                
        except ImportError:
            logger.error("Selenium not available for web scraping")
            return []
        except Exception as e:
            logger.error(f"Error with Selenium scraping: {e}")
            return []


class UnderdogScraper:
    """Scraper for Underdog Fantasy CS2 props"""
    
    def __init__(self):
        self.base_url = "https://api.underdogfantasy.com/v1/games"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
    
    def fetch_cs2_props(self) -> List[Dict]:
        """Fetch CS2 projections from Underdog"""
        try:
            # Underdog API endpoint - may need authentication
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_props(data)
            else:
                logger.warning(f"Underdog API returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching Underdog data: {e}")
            return []
    
    def _parse_props(self, data: Dict) -> List[Dict]:
        """Parse props from Underdog API response"""
        # Implementation depends on actual API structure
        logger.info("Underdog parsing not fully implemented")
        return []
