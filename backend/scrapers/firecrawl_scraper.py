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
                
                # Create lookups for all types
                players = {item['id']: item for item in included if item.get('type') == 'new_player'}
                games = {item['id']: item for item in included if item.get('type') == 'game'}
                teams = {item['id']: item for item in included if item.get('type') == 'team'}
                leagues = {item['id']: item['attributes']['name'] for item in included if item.get('type') == 'league'}
                
                for projection in projections:
                    try:
                        attrs = projection.get('attributes', {})
                        relationships = projection.get('relationships', {})
                        
                        # Get league info
                        league_id = relationships.get('league', {}).get('data', {}).get('id')
                        league_name = leagues.get(league_id, '')
                        
                        # Get player info
                        player_id = relationships.get('new_player', {}).get('data', {}).get('id')
                        player_obj = players.get(player_id, {})
                        player_attrs = player_obj.get('attributes', {})
                        player_name = player_attrs.get('display_name', 'Unknown')
                        
                        # Get team from player's team attribute
                        player_team = player_attrs.get('team', '')
                        
                        # Also try to get team from team_data relationship
                        team_data_id = player_obj.get('relationships', {}).get('team_data', {}).get('data', {}).get('id')
                        team_obj = teams.get(team_data_id, {})
                        team_abbr = team_obj.get('attributes', {}).get('abbreviation', '')
                        
                        # Use whichever team info is available
                        team_name = player_team or team_abbr
                        
                        # Get game info for context
                        game_id = relationships.get('game', {}).get('data', {}).get('id')
                        game_obj = games.get(game_id, {})
                        game_external_id = game_obj.get('attributes', {}).get('external_game_id', '')
                        
                        # Get stat and line
                        stat_type = attrs.get('stat_type', '')
                        line = attrs.get('line_score')
                        
                        if line and player_name and player_name != 'Unknown':
                            props.append({
                                'player_name': player_name,
                                'team': team_name,  # Add team information
                                'stat_type': self._normalize_stat_type(stat_type),
                                'line': float(line),
                                'platform': 'prizepicks',
                                'league_id': league_id,
                                'league_name': league_name,
                                'game_id': game_id,
                                'game_external_id': game_external_id
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


class FirecrawlUnderdogScraper:
    """Use Firecrawl to scrape Underdog Fantasy data"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.app = FirecrawlApp(api_key=api_key)
    
    def scrape_underdog_api(self) -> List[Dict]:
        """Scrape Underdog Fantasy API using Firecrawl"""
        try:
            logger.info("🔥 Using Firecrawl to fetch Underdog Fantasy data")
            
            # Underdog API endpoint
            url = "https://api.underdogfantasy.com/beta/v5/over_under_lines"
            
            result = self.app.scrape(url)
            
            if result and hasattr(result, 'markdown'):
                try:
                    # Parse JSON from markdown
                    markdown = result.markdown.strip()
                    if markdown.startswith('```json'):
                        markdown = markdown[7:]
                    elif markdown.startswith('```'):
                        markdown = markdown[3:]
                    if markdown.endswith('```'):
                        markdown = markdown[:-3]
                    
                    markdown = markdown.strip()
                    data = json.loads(markdown)
                    
                    # Check for error response
                    if 'status' in data and data.get('status') in [422, 403, 429]:
                        error_msg = data.get('detail', 'API blocked')
                        error_code = data.get('code', 'unknown')
                        logger.warning(f"❌ Underdog API blocked: {error_msg} (code: {error_code})")
                        logger.info("Note: Underdog Fantasy may not currently offer CS2 props or is blocking API access")
                        return []
                    
                    logger.info(f"✅ Parsed JSON from Firecrawl for Underdog")
                    return self._parse_underdog_response(data)
                    
                except Exception as e:
                    logger.error(f"Error parsing Underdog markdown: {e}")
            
            return []
            
        except Exception as e:
            logger.error(f"Error using Firecrawl for Underdog: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def _parse_underdog_response(self, data: Dict) -> List[Dict]:
        """Parse Underdog API response"""
        props = []
        
        try:
            players_data = data.get('players', [])
            over_under_lines = data.get('over_under_lines', [])
            appearances = data.get('appearances', [])
            
            # Create lookups
            players_dict = {p['id']: p for p in players_data}
            appearances_dict = {a['id']: a for a in appearances}
            
            for line in over_under_lines:
                try:
                    # Get game info
                    game = line.get('game', {})
                    sport_id = game.get('sport_id', '')
                    
                    # Filter for esports/CS2
                    if 'esport' not in sport_id.lower() and 'cs' not in sport_id.lower():
                        continue
                    
                    # Get options (over/under)
                    options = line.get('options', [])
                    for option in options:
                        over_under = option.get('over_under', {})
                        appearance_stat = over_under.get('appearance_stat', {})
                        
                        appearance_id = appearance_stat.get('appearance_id')
                        stat_type = appearance_stat.get('display_stat', '')
                        stat_value = option.get('stat_value')
                        
                        if not stat_value:
                            continue
                        
                        # Get player from appearance
                        appearance = appearances_dict.get(appearance_id, {})
                        player_id = appearance.get('player_id')
                        player = players_dict.get(player_id, {})
                        player_name = player.get('display_name', 'Unknown')
                        
                        if player_name != 'Unknown':
                            props.append({
                                'player_name': player_name,
                                'stat_type': self._normalize_stat_type(stat_type),
                                'line': float(stat_value),
                                'platform': 'underdog'
                            })
                    
                except Exception:
                    continue
            
            logger.info(f"Parsed {len(props)} props from Underdog")
            return props
            
        except Exception as e:
            logger.error(f"Error parsing Underdog response: {e}")
            return []
    
    def _normalize_stat_type(self, stat_type: str) -> str:
        """Normalize stat type"""
        stat_type_lower = stat_type.lower()
        
        if 'kill' in stat_type_lower:
            return 'kills'
        elif 'headshot' in stat_type_lower or 'hs' in stat_type_lower:
            return 'headshots'
        else:
            return stat_type_lower
