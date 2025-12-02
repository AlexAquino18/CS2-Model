import logging
from typing import List, Dict, Tuple
from datetime import datetime, timezone
import uuid
from scrapers import PrizePicksScraper, UnderdogScraper, HLTVScraper
from scrapers.manual_input import ManualDataProvider

logger = logging.getLogger(__name__)

class CS2DataAggregator:
    """Aggregates data from multiple sources and creates projections"""
    
    def __init__(self):
        self.prizepicks_scraper = PrizePicksScraper()
        self.underdog_scraper = UnderdogScraper()
        self.hltv_scraper = HLTVScraper()
        self.manual_provider = ManualDataProvider()
        self.scraping_status = {
            'hltv': {'success': False, 'error': None, 'last_attempt': None},
            'prizepicks': {'success': False, 'error': None, 'last_attempt': None},
            'underdog': {'success': False, 'error': None, 'last_attempt': None}
        }
    
    async def fetch_all_data(self) -> Tuple[List[Dict], List[Dict]]:
        """Fetch data from all sources and combine"""
        logger.info("Starting data aggregation from all sources...")
        
        from datetime import datetime, timezone
        
        # Update attempt timestamps
        now = datetime.now(timezone.utc).isoformat()
        
        # Fetch from HLTV
        try:
            self.scraping_status['hltv']['last_attempt'] = now
            hltv_matches = self.hltv_scraper.fetch_upcoming_matches()
            if hltv_matches:
                self.scraping_status['hltv']['success'] = True
                self.scraping_status['hltv']['error'] = None
            else:
                self.scraping_status['hltv']['success'] = False
                self.scraping_status['hltv']['error'] = "No matches returned (possible 403 or rate limit)"
        except Exception as e:
            hltv_matches = []
            self.scraping_status['hltv']['success'] = False
            self.scraping_status['hltv']['error'] = str(e)
        
        # Fetch from PrizePicks
        try:
            self.scraping_status['prizepicks']['last_attempt'] = now
            prizepicks_props = self.prizepicks_scraper.fetch_cs2_props()
            if prizepicks_props:
                self.scraping_status['prizepicks']['success'] = True
                self.scraping_status['prizepicks']['error'] = None
            else:
                self.scraping_status['prizepicks']['success'] = False
                self.scraping_status['prizepicks']['error'] = "No props returned (API returned 403 - anti-scraping protection)"
        except Exception as e:
            prizepicks_props = []
            self.scraping_status['prizepicks']['success'] = False
            self.scraping_status['prizepicks']['error'] = str(e)
        
        # Fetch from Underdog
        try:
            self.scraping_status['underdog']['last_attempt'] = now
            underdog_props = self.underdog_scraper.fetch_cs2_props()
            if underdog_props:
                self.scraping_status['underdog']['success'] = True
                self.scraping_status['underdog']['error'] = None
            else:
                self.scraping_status['underdog']['success'] = False
                self.scraping_status['underdog']['error'] = "No props returned (API unavailable)"
        except Exception as e:
            underdog_props = []
            self.scraping_status['underdog']['success'] = False
            self.scraping_status['underdog']['error'] = str(e)
        
        logger.info(f"Fetched: {len(hltv_matches)} HLTV matches, {len(prizepicks_props)} PrizePicks props, {len(underdog_props)} Underdog props")
        
        # If we have HLTV matches, use them even without PrizePicks props
        if hltv_matches:
            logger.info("Using HLTV matches - generating sample props since PrizePicks unavailable")
            matches, projections = self._combine_data_with_mock_props(hltv_matches, prizepicks_props, underdog_props)
            return matches, projections
        
        # If no real data available at all
        if not hltv_matches and not prizepicks_props:
            logger.warning("No data available from scrapers, using sample data template")
            logger.info("Note: PrizePicks blocked by anti-scraping protection")
            return [], []
        
        # Combine and process data
        matches, projections = self._combine_data(hltv_matches, prizepicks_props, underdog_props)
        
        return matches, projections
    
    def get_scraping_status(self) -> Dict:
        """Return current scraping status"""
        return self.scraping_status
    
    def _combine_data(self, hltv_matches: List[Dict], prizepicks_props: List[Dict], underdog_props: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Combine data from different sources"""
        matches = []
        all_projections = []
        
        # Process each HLTV match
        for hltv_match in hltv_matches:
            match_id = str(uuid.uuid4())
            
            # Create match object
            match = {
                'id': match_id,
                'team1': hltv_match['team1'],
                'team2': hltv_match['team2'],
                'tournament': hltv_match['tournament'],
                'start_time': hltv_match['start_time'].isoformat(),
                'map1': 'TBD',
                'map2': 'TBD',
                'status': 'upcoming'
            }
            matches.append(match)
            
            # Find matching props for this match
            match_projections = self._find_matching_props(
                match_id,
                hltv_match,
                prizepicks_props,
                underdog_props
            )
            
            all_projections.extend(match_projections)
        
        return matches, all_projections
    
    def _find_matching_props(self, match_id: str, match: Dict, pp_props: List[Dict], ud_props: List[Dict]) -> List[Dict]:
        """Find props that match this match"""
        projections = []
        
        # Group props by player
        player_props = {}
        
        for prop in pp_props:
            player = prop['player_name']
            stat_type = prop['stat_type']
            
            if player not in player_props:
                player_props[player] = {}
            
            if stat_type not in player_props[player]:
                player_props[player][stat_type] = {
                    'prizepicks': None,
                    'underdog': None
                }
            
            player_props[player][stat_type]['prizepicks'] = prop['line']
        
        # Add underdog props
        for prop in ud_props:
            player = prop['player_name']
            stat_type = prop['stat_type']
            
            if player not in player_props:
                player_props[player] = {}
            
            if stat_type not in player_props[player]:
                player_props[player][stat_type] = {
                    'prizepicks': None,
                    'underdog': None
                }
            
            player_props[player][stat_type]['underdog'] = prop['line']
        
        # Create projections
        for player, stats in player_props.items():
            for stat_type, lines in stats.items():
                pp_line = lines['prizepicks']
                ud_line = lines['underdog']
                
                if pp_line or ud_line:
                    # Use average of available lines as our projection
                    available_lines = [l for l in [pp_line, ud_line] if l]
                    projected_value = sum(available_lines) / len(available_lines)
                    
                    dfs_lines = []
                    if pp_line:
                        dfs_lines.append({
                            'platform': 'prizepicks',
                            'stat_type': stat_type,
                            'line': pp_line,
                            'maps': 'Map1+Map2'
                        })
                    if ud_line:
                        dfs_lines.append({
                            'platform': 'underdog',
                            'stat_type': stat_type,
                            'line': ud_line,
                            'maps': 'Map1+Map2'
                        })
                    
                    # Determine which team (simplified)
                    team = match['team1']  # Would need better logic
                    
                    projection = {
                        'match_id': match_id,
                        'player_name': player,
                        'team': team,
                        'stat_type': stat_type,
                        'projected_value': round(projected_value, 1),
                        'confidence': 75.0,
                        'dfs_lines': dfs_lines,
                        'value_opportunity': False,
                        'difference': 0.0
                    }
                    
                    projections.append(projection)
        
        return projections
