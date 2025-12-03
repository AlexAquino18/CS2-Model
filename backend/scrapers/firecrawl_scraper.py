"""
Firecrawl-based scraper for PrizePicks
Uses Firecrawl API to bypass Cloudflare protection
"""
import logging
from typing import List, Dict
from firecrawl import FirecrawlApp
import json

logger = logging.getLogger(__name__)

class FirecrawlPrizePicksScraper:
    """Use Firecrawl to scrape PrizePicks data"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.app = FirecrawlApp(api_key=api_key)
    
    def scrape_prizepicks_api(self) -> List[Dict]:
        """Scrape PrizePicks API using Firecrawl"""
        try:
            logger.info("Using Firecrawl to fetch PrizePicks data")
            
            # Try to scrape the API directly
            url = "https://api.prizepicks.com/projections?per_page=500&single_stat=true&game_mode=pickem"
            
            # Use correct method name: scrape (not scrape_url)
            result = self.app.scrape(url, params={'formats': ['json']})
            
            if result:
                logger.info(f"✅ Firecrawl returned data: {type(result)}")
                
                # Check different possible response structures
                if 'markdown' in result:
                    # Try to parse markdown as JSON
                    try:
                        import json
                        data = json.loads(result['markdown'])
                        return self._parse_api_response(data)
                    except:
                        pass
                
                if 'html' in result:
                    # Try to extract JSON from HTML
                    try:
                        import json
                        data = json.loads(result['html'])
                        return self._parse_api_response(data)
                    except:
                        pass
                
                if 'data' in result:
                    return self._parse_api_response(result['data'])
                
                # Log what we got
                logger.info(f"Firecrawl result keys: {result.keys() if isinstance(result, dict) else 'not a dict'}")
                logger.warning("Could not find parseable data in Firecrawl response")
            
            return []
            
        except Exception as e:
            logger.error(f"Error using Firecrawl to scrape PrizePicks: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def scrape_prizepicks_website(self) -> List[Dict]:
        """Scrape PrizePicks website for CS2 data"""
        try:
            logger.info("Using Firecrawl to scrape PrizePicks website")
            
            url = "https://app.prizepicks.com/"
            
            result = self.app.scrape_url(
                url=url,
                params={
                    'formats': ['markdown', 'html'],
                    'onlyMainContent': True
                }
            )
            
            if result:
                logger.info("✅ Successfully scraped PrizePicks website with Firecrawl")
                # Parse the HTML/markdown for CS2 props
                return self._parse_website_content(result)
            
            return []
            
        except Exception as e:
            logger.error(f"Error scraping PrizePicks website: {e}")
            return []
    
    def _parse_api_response(self, data: str) -> List[Dict]:
        """Parse API response from Firecrawl"""
        try:
            # Try to parse as JSON
            if isinstance(data, str):
                data = json.loads(data)
            
            props = []
            
            if 'data' in data:
                projections = data['data']
                included = data.get('included', [])
                
                # Create player lookup
                players = {item['id']: item for item in included if item.get('type') == 'new_player'}
                
                for projection in projections:
                    try:
                        attrs = projection.get('attributes', {})
                        relationships = projection.get('relationships', {})
                        
                        # Get player name
                        player_id = relationships.get('new_player', {}).get('data', {}).get('id')
                        player_info = players.get(player_id, {}).get('attributes', {})
                        player_name = player_info.get('display_name', 'Unknown')
                        
                        # Get stat and line
                        stat_type = attrs.get('stat_type', '')
                        line = attrs.get('line_score')
                        
                        if line and player_name and player_name != 'Unknown':
                            props.append({
                                'player_name': player_name,
                                'stat_type': self._normalize_stat_type(stat_type),
                                'line': float(line),
                                'platform': 'prizepicks'
                            })
                    except:
                        continue
            
            logger.info(f"Parsed {len(props)} props from Firecrawl response")
            return props
            
        except Exception as e:
            logger.error(f"Error parsing Firecrawl response: {e}")
            return []
    
    def _parse_website_content(self, result: Dict) -> List[Dict]:
        """Parse website HTML/markdown content"""
        # This would need more complex parsing based on the actual HTML structure
        logger.info("Website parsing not fully implemented yet")
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
