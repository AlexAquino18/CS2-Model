import requests
from bs4 import BeautifulSoup
import logging
import json
from typing import List, Dict, Optional
import time

logger = logging.getLogger(__name__)

class PrizePicksScraper:
    """Scraper for PrizePicks CS2 props"""
    
    def __init__(self):
        self.base_url = "https://api.prizepicks.com/projections"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
    
    def fetch_cs2_props(self) -> List[Dict]:
        """Fetch CS2 projections from PrizePicks API"""
        try:
            # Try direct API first - no league_id filter
            response = requests.get(self.base_url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                # Filter for CS2/Counter-Strike
                cs2_projections = self._parse_projections(data)
                if cs2_projections:
                    return cs2_projections
            else:
                logger.info(f"PrizePicks API returned status {response.status_code}, trying alternative method")
            
            # Try with different endpoint structure
            alt_url = "https://api.prizepicks.com/projections?league_id=1"  # Try league ID 1
            response = requests.get(alt_url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                cs2_projections = self._parse_projections(data)
                if cs2_projections:
                    return cs2_projections
            
            logger.info("Trying Selenium-based scraping for PrizePicks")
            return self._scrape_with_selenium()
                
        except Exception as e:
            logger.error(f"Error fetching PrizePicks data: {e}")
            return []
    
    def _parse_projections(self, data: Dict) -> List[Dict]:
        """Parse projections from API response"""
        projections = []
        
        try:
            if 'data' in data:
                for item in data['data']:
                    if item.get('type') == 'projection':
                        attrs = item.get('attributes', {})
                        
                        # Extract player and stat info
                        projection = {
                            'player_name': attrs.get('description', '').split(' - ')[0].strip(),
                            'stat_type': self._normalize_stat_type(attrs.get('stat_type', '')),
                            'line': float(attrs.get('line_score', 0)),
                            'game_info': attrs.get('description', ''),
                            'start_time': attrs.get('start_time', ''),
                        }
                        
                        if projection['player_name'] and projection['line'] > 0:
                            projections.append(projection)
            
            logger.info(f"Parsed {len(projections)} PrizePicks projections")
            return projections
            
        except Exception as e:
            logger.error(f"Error parsing projections: {e}")
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
    
    def _scrape_website(self) -> List[Dict]:
        """Fallback: Scrape PrizePicks website directly"""
        try:
            # This would require more complex scraping with Selenium
            # For now, return empty list
            logger.info("Website scraping not implemented yet")
            return []
        except Exception as e:
            logger.error(f"Error scraping website: {e}")
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
