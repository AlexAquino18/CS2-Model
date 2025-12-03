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
            logger.info("🔥 Using Firecrawl to fetch CS2 props from PrizePicks")
            
            # Fetch CS2-specific props (league_id=265)
            url = "https://api.prizepicks.com/projections?league_id=265&per_page=250&single_stat=true&game_mode=pickem"
            
            # Use correct method: scrape (returns Document object)
            result = self.app.scrape(url)
            
            if result:
                logger.info(f"✅ Firecrawl returned Document")
                
                # Firecrawl returns a Document object with markdown attribute containing JSON
                if hasattr(result, 'markdown') and result.markdown:
                    try:
                        # Remove code fence if present
                        markdown = result.markdown.strip()
                        if markdown.startswith('```json'):
                            markdown = markdown[7:]  # Remove ```json
                        if markdown.startswith('```'):
                            markdown = markdown[3:]  # Remove ```
                        if markdown.endswith('```'):
                            markdown = markdown[:-3]  # Remove closing ```
                        
                        markdown = markdown.strip()
                        
                        # Parse JSON
                        data = json.loads(markdown)
                        logger.info(f"✅ Parsed JSON from Firecrawl markdown")
                        
                        return self._parse_api_response(data)
                    except Exception as e:
                        logger.error(f"Error parsing markdown as JSON: {e}")
                        logger.debug(f"Markdown preview: {result.markdown[:500]}")
                
                logger.warning("Could not extract parseable data from Firecrawl response")
            
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
            
            result = self.app.scrape(
                url,
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
                
                # Create league lookup
                leagues = {item['id']: item['attributes']['name'] for item in included if item.get('type') == 'league'}
                
                for projection in projections:
                    try:
                        attrs = projection.get('attributes', {})
                        relationships = projection.get('relationships', {})
                        
                        # Get league info
                        league_id = relationships.get('league', {}).get('data', {}).get('id')
                        league_name = leagues.get(league_id, '')
                        
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
                                'platform': 'prizepicks',
                                'league_id': league_id,
                                'league_name': league_name
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
