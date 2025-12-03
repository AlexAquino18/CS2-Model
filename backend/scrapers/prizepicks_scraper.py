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
        """Fetch CS2 projections from PrizePicks - Try Firecrawl first"""
        try:
            # Try Firecrawl first (bypasses Cloudflare)
            try:
                from scrapers.firecrawl_scraper import FirecrawlPrizePicksScraper
                firecrawl_api_key = "fc-5edd331815bb4517baca807b9903ab29"
                
                firecrawl_scraper = FirecrawlPrizePicksScraper(firecrawl_api_key)
                props = firecrawl_scraper.scrape_prizepicks_api()
                
                if props:
                    logger.info(f"✅ Firecrawl fetched {len(props)} PrizePicks props")
                    
                    # Log sample leagues
                    sample_leagues = set([p.get('league_name', 'Unknown') for p in props[:50]])
                    logger.info(f"Sample leagues in props: {sorted(sample_leagues)}")
                    
                    # Debug first prop
                    if props:
                        first = props[0]
                        logger.info(f"First prop debug - league_id: '{first.get('league_id')}' (type: {type(first.get('league_id'))}), league_name: '{first.get('league_name')}'")
                    
                    # Filter for CS2 only
                    cs2_props = [p for p in props if self._is_cs2_prop(p)]
                    logger.info(f"After filtering, found {len(cs2_props)} CS2 props")
                    
                    if cs2_props:
                        logger.info(f"✅ Found {len(cs2_props)} CS2 props via Firecrawl")
                        return cs2_props
                    else:
                        logger.warning("CS2 props may not be available on PrizePicks right now")
            except Exception as fc_error:
                logger.warning(f"Firecrawl attempt failed: {fc_error}")
            
            # Fallback to direct API (will likely be blocked)
            logger.info("Trying direct API as fallback")
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
    
    def _is_cs2_prop(self, prop: Dict) -> bool:
        """Check if a prop is for CS2"""
        # Check if the prop has CS2-related information
        # CS2 league ID is 265 on PrizePicks (can be string or int)
        league_id = str(prop.get('league_id', ''))
        league_name = prop.get('league_name', '').upper()
        
        result = league_id == '265' or league_name == 'CS2'
        
        # Debug first few calls
        if not hasattr(self, '_debug_count'):
            self._debug_count = 0
        
        if self._debug_count < 3:
            logger.info(f"Filter check #{self._debug_count}: league_id='{league_id}', league_name='{league_name}', result={result}")
            self._debug_count += 1
        
        return result
    
    def _get_all_leagues(self) -> Dict[str, int]:
        """Fetch all available leagues from PrizePicks - GitHub approach"""
        try:
            url = f"{self.base_url}/leagues"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                leagues = {}
                for league in data.get('data', []):
                    name = league.get('attributes', {}).get('name', '').upper()
                    league_id = league.get('id')
                    if name and league_id:
                        leagues[name] = int(league_id)
                
                logger.info(f"Successfully fetched {len(leagues)} leagues from PrizePicks")
                return leagues
            else:
                logger.warning(f"Leagues API returned status {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching leagues: {e}")
            return {}
    
    def _fetch_league_props(self, league_id: int, league_name: str) -> List[Dict]:
        """Fetch props for a specific league - GitHub dannyphantomSS approach"""
        all_props = []
        page = 1
        
        while True:
            try:
                url = f"{self.base_url}/projections"
                params = {
                    'league_id': league_id,
                    'per_page': 250,
                    'page': page,
                    'single_stat': 'true',
                    'game_mode': 'pickem'
                }
                
                response = self.session.get(url, params=params, timeout=15)
                
                if response.status_code == 429:
                    logger.warning(f"Rate limited for {league_name} page {page}")
                    break
                
                if response.status_code != 200:
                    logger.warning(f"Error {response.status_code} for {league_name} page {page}")
                    break
                
                data = response.json()
                props = self._parse_props_response(data, league_name)
                
                if not props:
                    break
                
                all_props.extend(props)
                logger.info(f"{league_name} Page {page}: {len(props)} props (Total: {len(all_props)})")
                
                if len(props) < 250:  # Last page
                    break
                
                page += 1
                
            except Exception as e:
                logger.error(f"Error fetching {league_name} page {page}: {str(e)}")
                break
        
        return all_props
    
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
    
    def _parse_props_response(self, data: Dict, sport: str) -> List[Dict]:
        """Parse props response - GitHub dannyphantomSS approach"""
        props = []
        
        try:
            projections = data.get('data', [])
            included = data.get('included', [])
            
            # Lookup tables for players and picks
            players = {item['id']: item for item in included if item.get('type') == 'new_player'}
            picks = {item['id']: item for item in included if item.get('type') == 'pick'}
            
            for projection in projections:
                try:
                    attrs = projection.get('attributes', {})
                    relationships = projection.get('relationships', {})
                    
                    # Get player info from included data
                    player_id = relationships.get('new_player', {}).get('data', {}).get('id')
                    player_info = players.get(player_id, {}).get('attributes', {}) if player_id else {}
                    
                    # Get player name
                    player_name = player_info.get('display_name', 'Unknown')
                    
                    # Get stat type and line
                    stat_type = attrs.get('stat_type', 'Unknown')
                    line_score = attrs.get('line_score')
                    
                    if not line_score:
                        continue
                    
                    try:
                        line = float(line_score)
                    except (ValueError, TypeError):
                        continue
                    
                    # Build prop object
                    prop = {
                        'player_name': player_name,
                        'stat_type': self._normalize_stat_type(stat_type),
                        'line': line,
                        'game_info': attrs.get('description', ''),
                        'start_time': attrs.get('start_time', ''),
                        'platform': 'prizepicks'
                    }
                    
                    props.append(prop)
                    
                except Exception:
                    continue  # Skip bad prop
            
            return props
            
        except Exception as e:
            logger.error(f"Error parsing {sport} response: {str(e)}")
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
    """Scraper for Underdog Fantasy props - GitHub aidanhall21 approach"""
    
    def __init__(self):
        self.base_url = "https://api.underdogfantasy.com/beta/v5/over_under_lines"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
            'Accept': 'application/json'
        })
    
    def fetch_cs2_props(self) -> List[Dict]:
        """Fetch CS2/esports projections from Underdog"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully fetched Underdog data")
                return self._parse_props(data)
            elif response.status_code == 422:
                logger.warning(f"Underdog API rate limited (CDN circuit breaker)")
                return []
            else:
                logger.warning(f"Underdog API returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching Underdog data: {e}")
            return []
    
    def _parse_props(self, data: Dict) -> List[Dict]:
        """Parse props from Underdog API response - GitHub approach"""
        props = []
        
        try:
            # Underdog returns: players, appearances, over_under_lines
            if 'players' not in data or 'over_under_lines' not in data:
                logger.warning("Underdog API structure unexpected")
                return []
            
            players_data = data.get('players', [])
            over_under_lines = data.get('over_under_lines', [])
            
            # Create lookup for players
            players_dict = {p['id']: p for p in players_data}
            
            # Process over/under lines
            for line in over_under_lines:
                try:
                    # Check if it's esports/CS2
                    sport_id = line.get('sport_id', '')
                    if 'esport' not in sport_id.lower() and 'cs' not in sport_id.lower():
                        continue
                    
                    # Get options (over/under)
                    options = line.get('options', [])
                    for option in options:
                        over_under_data = option.get('over_under', {})
                        appearance_stat = over_under_data.get('appearance_stat', {})
                        
                        # Get player info
                        appearance_id = appearance_stat.get('appearance_id')
                        stat_type = appearance_stat.get('stat', '')
                        
                        # Find player from appearances
                        # Note: This is simplified - full implementation would join with appearances
                        
                        prop = {
                            'player_name': 'Unknown',  # Would need to join with appearances/players
                            'stat_type': self._normalize_stat_type(stat_type),
                            'line': float(option.get('stat_value', 0)),
                            'platform': 'underdog'
                        }
                        
                        if prop['line'] > 0:
                            props.append(prop)
                        
                except Exception:
                    continue
            
            logger.info(f"Parsed {len(props)} Underdog props")
            return props
            
        except Exception as e:
            logger.error(f"Error parsing Underdog response: {str(e)}")
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
